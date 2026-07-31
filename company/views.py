from django.forms import modelform_factory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from company.forms import COMPANY_FIELDS
from company.models import Company
from person.decorators import staff_api_required, staff_required


def company_list(request):
    companies = Company.objects.filter(verified_seller=True)
    return render(request, 'company_list.html', {'companies': companies})


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk, verified_seller=True)
    featured_goods = company.goods.all()[:4]
    gallery_photos = company.photos.exclude(pk=company.hero_photo_id)[:6]
    return render(request, 'company_detail.html', {
        'company': company,
        'featured_goods': featured_goods,
        'gallery_photos': gallery_photos,
        'grape_varieties': company.grape_varieties(),
    })


def company_goods(request, pk):
    company = get_object_or_404(Company, pk=pk, verified_seller=True)
    goods = company.goods.all()
    return render(request, 'company_goods.html', {'company': company, 'goods': goods})


@staff_api_required
def company_detail_api(request, pk):
    if request.method == 'POST' and len(request.POST):
        instance = get_object_or_404(Company, pk=pk)
        # only bind fields the caller actually sent, so the storefront's quick-edit
        # widget can't be blocked by unrelated required fields it never touches
        fields = [f for f in COMPANY_FIELDS if f in request.POST]
        form = modelform_factory(Company, fields=fields)(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()

    company = get_object_or_404(Company, pk=pk)
    return JsonResponse(Company.as_json([company])[0])


@staff_api_required
def company_list_api(request):
    return JsonResponse(Company.as_json(Company.objects.all()), safe=False)


@staff_required
def staff_company_list(request):
    return render(request, 'staff_company_list.html')
