from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from company.models import Company


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


def company_list_api(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'forbidden'}, status=403)
    return JsonResponse(Company.as_json(Company.objects.all()), safe=False)


def staff_company_list(request):
    return render(request, 'staff_company_list.html')
