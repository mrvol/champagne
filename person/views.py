import json
import os

import cbor2
from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import Group
from django.forms import modelform_factory
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.i18n import set_language as django_set_language

from person.decorators import staff_api_required, staff_required
from person.models import MIN_AGE, User, WebAuthnCredential, age_from_birthday
from person.passkeys import (
    b64url_decode, b64url_encode, parse_attested_credential_data,
    sign_count_from_auth_data, verify_assertion_signature,
)


def set_language(request):
    response = django_set_language(request)
    lang = request.POST.get('language')
    if request.user.is_authenticated and lang in dict(settings.LANGUAGES):
        request.user.ui_language = lang
        request.user.save(update_fields=['ui_language'])
    return response


def login_view(request):
    error = ''
    if request.POST:
        user = authenticate(request, username=request.POST.get('email', '').strip().lower(),
                            password=request.POST.get('password', ''))
        if user:
            auth_login(request, user)
            nxt = request.GET.get('next', '')
            return redirect(nxt if nxt.startswith('/') else 'home')
        error = _("That email and password don't match.")
    return render(request, 'login.html', {'error': error})


def register(request):
    error = ''
    if request.POST:
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        first, _sep, last = request.POST.get('name', '').strip().partition(' ')
        birthday = parse_date(request.POST.get('birthday', ''))
        if '@' not in email:
            error = _('Enter a valid work email.')
        elif len(password) < 8:
            error = _('The password needs at least 8 characters.')
        elif User.objects.filter(username=email).exists():
            error = _('This email already has an account. Sign in instead.')
        elif not birthday:
            error = _('Enter your date of birth.')
        elif age_from_birthday(birthday) < MIN_AGE:
            error = _('You must be at least %(age)s to sign up.') % {'age': MIN_AGE}
        else:
            user = User.objects.create_user(username=email, email=email, password=password,
                                            first_name=first, last_name=last, birthday=birthday)
            if request.POST.get('role') == 'hiring':
                user.groups.add(Group.objects.get_or_create(name='hiring')[0])
            auth_login(request, user)
            return redirect('home')
    return render(request, 'register.html', {'error': error})


def logout_view(request):
    auth_logout(request)
    return redirect('home')


def person_list(request):
    people = User.objects.order_by('-id')
    return render(request, 'person_list.html', {'people': people})


def person_detail(request, id):
    person = get_object_or_404(User, id=id)
    return render(request, 'person_detail.html', {'person': person})


def user_list(request):
    users = User.objects.all()
    return render(request, 'user_list.html', {'users': users})


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user_detail.html', {'user': user})


USER_FIELDS = ['username', 'email', 'first_name', 'last_name', 'phone', 'country', 'is_staff', 'is_active']


@staff_api_required
def user_detail_api(request, pk=None):
    if request.method == 'POST' and len(request.POST):
        instance = get_object_or_404(User, pk=pk) if pk else User()
        fields = [f for f in USER_FIELDS if f in request.POST]
        form = modelform_factory(User, fields=fields)(data=request.POST, instance=instance)
        if form.is_valid():
            user = form.save(commit=False)
            if 'roles' in request.POST:
                user.roles = [r.strip() for r in request.POST['roles'].split(',') if r.strip()]
            password = request.POST.get('password', '').strip()
            if password:
                user.set_password(password)
            elif not pk:
                return JsonResponse({'error': 'Password is required for new users.'}, status=400)
            user.save()
            pk = user.pk
        else:
            return JsonResponse({'error': form.errors.as_text()}, status=400)

    qs = User.objects.all()
    if pk:
        qs = qs.filter(pk=pk)
    data = User.as_json(qs)
    if pk:
        if not data:
            raise Http404
        return JsonResponse(data[0])
    return JsonResponse(data, safe=False)


@staff_required
def staff_user_list(request):
    return render(request, 'staff_user_list.html')


def passkey_register_options(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest('login required')
    challenge = os.urandom(32)
    request.session['passkey_challenge'] = b64url_encode(challenge)
    rp_id = request.get_host().split(':')[0]
    return JsonResponse({
        'rp': {'id': rp_id, 'name': 'Voilà Champagne'},
        'user': {
            'id': b64url_encode(str(request.user.pk).encode()),
            'name': request.user.email,
            'displayName': request.user.get_full_name() or request.user.username,
        },
        'challenge': b64url_encode(challenge),
        'pubKeyCredParams': [{'type': 'public-key', 'alg': -7}],
        'authenticatorSelection': {
            'authenticatorAttachment': 'platform',
            'residentKey': 'preferred',
            'userVerification': 'required',
        },
        'attestation': 'none',
        'timeout': 60000,
    })


@require_POST
def passkey_register_verify(request):
    if not request.user.is_authenticated:
        return HttpResponseBadRequest('login required')
    challenge = request.session.pop('passkey_challenge', None)
    data = json.loads(request.body)

    client_data_bytes = b64url_decode(data['response']['clientDataJSON'])
    client_data = json.loads(client_data_bytes)
    if not challenge or client_data.get('challenge') != challenge:
        return HttpResponseBadRequest('bad challenge')
    if client_data.get('type') != 'webauthn.create':
        return HttpResponseBadRequest('bad type')
    if client_data.get('origin') != f'{request.scheme}://{request.get_host()}':
        return HttpResponseBadRequest('bad origin')

    attestation_object = cbor2.loads(b64url_decode(data['response']['attestationObject']))
    credential_id, x, y = parse_attested_credential_data(attestation_object['authData'])

    WebAuthnCredential.objects.create(
        user=request.user,
        credential_id=credential_id,
        public_key_x=x.to_bytes(32, 'big'),
        public_key_y=y.to_bytes(32, 'big'),
    )
    return JsonResponse({'ok': True})


@require_POST
def passkey_login_options(request):
    email = request.POST.get('email', '').strip().lower()
    user = User.objects.filter(username=email).first()
    if not user:
        return HttpResponseBadRequest('no such user')
    challenge = os.urandom(32)
    request.session['passkey_challenge'] = b64url_encode(challenge)
    request.session['passkey_login_user_id'] = user.pk
    return JsonResponse({
        'challenge': b64url_encode(challenge),
        'rpId': request.get_host().split(':')[0],
        'allowCredentials': [
            {'type': 'public-key', 'id': b64url_encode(bytes(c.credential_id))}
            for c in user.webauthn_credentials.all()
        ],
        'userVerification': 'required',
        'timeout': 60000,
    })


@require_POST
def passkey_login_verify(request):
    user_id = request.session.get('passkey_login_user_id')
    challenge = request.session.pop('passkey_challenge', None)
    if not user_id:
        return HttpResponseBadRequest('no pending login')
    user = get_object_or_404(User, pk=user_id)
    data = json.loads(request.body)

    client_data_bytes = b64url_decode(data['response']['clientDataJSON'])
    client_data = json.loads(client_data_bytes)
    if not challenge or client_data.get('challenge') != challenge:
        return HttpResponseBadRequest('bad challenge')
    if client_data.get('type') != 'webauthn.get':
        return HttpResponseBadRequest('bad type')
    if client_data.get('origin') != f'{request.scheme}://{request.get_host()}':
        return HttpResponseBadRequest('bad origin')

    credential_id = b64url_decode(data['id'])
    credential = get_object_or_404(WebAuthnCredential, credential_id=credential_id, user=user)

    auth_data = b64url_decode(data['response']['authenticatorData'])
    signature = b64url_decode(data['response']['signature'])
    x = int.from_bytes(bytes(credential.public_key_x), 'big')
    y = int.from_bytes(bytes(credential.public_key_y), 'big')
    if not verify_assertion_signature(auth_data, client_data_bytes, signature, x, y):
        return HttpResponseBadRequest('bad signature')

    sign_count = sign_count_from_auth_data(auth_data)
    if sign_count and sign_count <= credential.sign_count:
        return HttpResponseBadRequest('replay detected')
    credential.sign_count = sign_count
    credential.save()

    request.session.pop('passkey_login_user_id', None)
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    auth_login(request, user)
    return JsonResponse({'ok': True, 'redirect': '/'})
