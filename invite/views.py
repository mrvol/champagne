from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from company.models import Company, CompanyPhoto
from goods.models import Good
from invite.emails import send_completion_notification
from invite.forms import CompanyOnboardingForm, GoodOnboardingForm
from invite.models import Invitation
from person.models import MIN_AGE, User, age_from_birthday

STEP_URL_NAMES = {
    Invitation.STEP_ACCOUNT: 'invite_company',
    Invitation.STEP_COMPANY: 'invite_company',
    Invitation.STEP_PRODUCTS: 'invite_products',
    Invitation.STEP_REVIEW: 'invite_review',
    Invitation.STEP_DONE: 'invite_completed',
}


def _step_redirect(invitation):
    return redirect(STEP_URL_NAMES[invitation.step], token=invitation.token)


def _resolve_step_access(request, token):
    """Common guard for every step view: invitation must be usable and owned by request.user."""
    invitation = get_object_or_404(Invitation, token=token)
    if not invitation.is_usable():
        return None, render(request, 'invite_invalid.html', {'invitation': invitation})
    if not request.user.is_authenticated or request.user.pk != invitation.user_id:
        return None, redirect('invite_landing', token=token)
    return invitation, None


def invitation_landing(request, token):
    invitation = get_object_or_404(Invitation, token=token)
    if not invitation.is_usable():
        return render(request, 'invite_invalid.html', {'invitation': invitation})

    if invitation.user_id and request.user.is_authenticated and request.user.pk == invitation.user_id:
        return _step_redirect(invitation)

    error = ''
    if invitation.user_id:
        # Account already created for this invitation - authenticate and resume.
        if request.method == 'POST':
            user = authenticate(request, username=invitation.contact_email,
                                password=request.POST.get('password', ''))
            if user and user.pk == invitation.user_id:
                auth_login(request, user)
                return _step_redirect(invitation)
            error = _("That password doesn't match this invitation's account.")
        return render(request, 'invite_login.html', {'invitation': invitation, 'error': error})

    # First visit - create the seller account.
    if request.method == 'POST':
        password = request.POST.get('password', '')
        first, _sep, last = request.POST.get('name', '').strip().partition(' ')
        birthday = parse_date(request.POST.get('birthday', ''))
        if len(password) < 8:
            error = _('The password needs at least 8 characters.')
        elif User.objects.filter(username=invitation.contact_email).exists():
            error = _('An account already exists for this email. Contact support to relink your invitation.')
        elif not birthday:
            error = _('Enter your date of birth.')
        elif age_from_birthday(birthday) < MIN_AGE:
            error = _('You must be at least %(age)s to sign up.') % {'age': MIN_AGE}
        else:
            user = User.objects.create_user(
                username=invitation.contact_email, email=invitation.contact_email, password=password,
                first_name=first, last_name=last, birthday=birthday, roles=['seller'],
            )
            invitation.user = user
            invitation.advance(Invitation.STEP_COMPANY)
            auth_login(request, user)
            return _step_redirect(invitation)
    return render(request, 'invite_account.html', {'invitation': invitation, 'error': error})


def invitation_company(request, token):
    invitation, response = _resolve_step_access(request, token)
    if response:
        return response
    if invitation.company_id is None:
        invitation.company = Company.objects.create()
        invitation.save(update_fields=['company'])

    if request.method == 'POST':
        form = CompanyOnboardingForm(request.POST, instance=invitation.company)
        if form.is_valid():
            form.save()
            cover = request.FILES.get('cover_image')
            if cover:
                invitation.company.attach_photo(cover, category=CompanyPhoto.CATEGORY_OTHER)
            for category in (CompanyPhoto.CATEGORY_WINERY, CompanyPhoto.CATEGORY_VINEYARD, CompanyPhoto.CATEGORY_CELLAR):
                for uploaded in request.FILES.getlist(f'{category}_photos'):
                    invitation.company.attach_photo(uploaded, category=category)
            if 'continue' in request.POST:
                invitation.advance(Invitation.STEP_PRODUCTS)
                return redirect('invite_products', token=token)
            messages.success(request, _('Progress saved.'))
            return redirect('invite_company', token=token)
    else:
        form = CompanyOnboardingForm(instance=invitation.company)

    return render(request, 'invite_company.html', {'invitation': invitation, 'form': form})


def invitation_products(request, token):
    invitation, response = _resolve_step_access(request, token)
    if response:
        return response
    if request.method == 'POST' and 'continue' in request.POST:
        invitation.advance(Invitation.STEP_REVIEW)
        return redirect('invite_review', token=token)
    goods = invitation.company.goods.all() if invitation.company_id else Good.objects.none()
    return render(request, 'invite_products.html', {'invitation': invitation, 'goods': goods})


def invitation_product_edit(request, token, pk=None):
    invitation, response = _resolve_step_access(request, token)
    if response:
        return response
    good = get_object_or_404(Good, pk=pk, company=invitation.company) if pk else Good(company=invitation.company)

    if request.method == 'POST':
        form = GoodOnboardingForm(request.POST, instance=good)
        if form.is_valid():
            good = form.save()
            photo = request.FILES.get('photo')
            if photo:
                good.attach_photo(photo)
            messages.success(request, _('Wine saved.'))
            return redirect('invite_products', token=token)
    else:
        form = GoodOnboardingForm(instance=good)

    return render(request, 'invite_product_form.html', {'invitation': invitation, 'form': form, 'good': good})


@require_POST
def invitation_product_delete(request, token, pk):
    invitation, response = _resolve_step_access(request, token)
    if response:
        return response
    Good.objects.filter(pk=pk, company=invitation.company).delete()
    return redirect('invite_products', token=token)


def invitation_review(request, token):
    invitation, response = _resolve_step_access(request, token)
    if response:
        return response
    goods = invitation.company.goods.all() if invitation.company_id else Good.objects.none()
    if request.method == 'POST':
        invitation.mark_completed()
        send_completion_notification(invitation)
        return redirect('invite_completed', token=token)
    return render(request, 'invite_review.html', {'invitation': invitation, 'goods': goods})


def invitation_completed(request, token):
    invitation = get_object_or_404(Invitation, token=token)
    if invitation.status != Invitation.STATUS_COMPLETED:
        return redirect('invite_landing', token=token)
    return render(request, 'invite_completed.html', {'invitation': invitation})
