from django.shortcuts import get_object_or_404, render

from company.models import Company


def company_list(request):
    companies = Company.objects.all()
    return render(request, 'company_list.html', {'companies': companies})


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    featured_goods = company.goods.all()[:4]
    gallery_photos = company.photos.exclude(pk=company.hero_photo_id)[:6]
    return render(request, 'company_detail.html', {
        'company': company,
        'featured_goods': featured_goods,
        'gallery_photos': gallery_photos,
        'grape_varieties': company.grape_varieties(),
    })


def company_goods(request, pk):
    company = get_object_or_404(Company, pk=pk)
    goods = company.goods.all()
    return render(request, 'company_goods.html', {'company': company, 'goods': goods})
