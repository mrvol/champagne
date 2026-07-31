from django.db.models import Count, Q, Sum
from django.forms import modelform_factory
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render

from company.models import Company
from goods.forms import GOOD_FIELDS
from goods.models import Good
from person.decorators import staff_api_required, staff_required
from warehouse.models import Stock


def good_list(request):
    q = request.GET.get('q', '').strip()
    goods = Good.objects.filter(company__verified_seller=True).annotate(available=Sum('stock__quantity'))
    if q:
        goods = goods.filter(Q(name__icontains=q) | Q(region__icontains=q) | Q(grape_variety__icontains=q))
    return render(request, 'good_list.html', {'goods': goods, 'q': q})


def good_detail(request, pk):
    good = get_object_or_404(Good, pk=pk, company__verified_seller=True)
    available = Stock.objects.filter(good=good).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'good_detail.html', {
        'good': good,
        'available': available,
        'grape_varieties': good.grape_variety_list(),
    })

@staff_required
def staff_good_list(request):
    return render(request, 'staff_good_list.html')


@staff_api_required
def good_detail_api(request, pk=None):
    if request.method == 'POST' and len(request.POST):
        if pk:
            instance = get_object_or_404(Good, pk=pk, company__verified_seller=True)
        else:
            instance = Good(company=Company.objects.filter(verified_seller=True).first())
        # only bind fields the caller actually sent, so a widget that only edits
        # a few fields (e.g. the storefront's quick-edit card) can't be blocked by
        # unrelated required fields (currency, stock_status) it never touches
        fields = [f for f in GOOD_FIELDS if f in request.POST]
        form = modelform_factory(Good, fields=fields)(data=request.POST, instance=instance)
        if form.is_valid():
            good = form.save()
            pk = good.pk

    qs = Good.objects.filter(company__verified_seller=True)
    if pk:
        qs = qs.filter(pk=pk)
    else:
        q = request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(region__icontains=q) | Q(grape_variety__icontains=q))
        status = request.GET.get('status', '').strip()
        if status:
            qs = qs.filter(stock_status=status)
        wine_type = request.GET.get('wine_type', '').strip()
        if wine_type:
            qs = qs.filter(wine_type=wine_type)

    data = Good.as_json(qs)
    if pk:
        if not data:
            raise Http404
        return JsonResponse(data[0])
    return JsonResponse(data, safe=False)


@staff_api_required
def good_photos_api(request, pk):
    good = get_object_or_404(Good, pk=pk, company__verified_seller=True)
    if request.method == 'POST':
        if request.FILES.get('image'):
            good.attach_photo(request.FILES['image'])
        elif request.POST.get('make_main'):
            good.make_main(request.POST['make_main'])
        elif request.POST.get('delete'):
            photo = good.photos.filter(pk=request.POST['delete']).first()
            if photo:
                if good.photo_id == photo.pk:
                    good.photo = good.photos.exclude(pk=photo.pk).first()
                    good.save()
                photo.delete()

    return JsonResponse({
        'main_photo_id': good.photo_id,
        'photos': [{'pk': p.pk, 'url': p.image.url} for p in good.photos.all()],
    })


@staff_api_required
def good_stats_api(request):
    qs = Good.objects.filter(company__verified_seller=True)
    by_status = {row['stock_status']: row['n'] for row in qs.values('stock_status').annotate(n=Count('pk'))}
    return JsonResponse({
        'total': qs.count(),
        'active': by_status.get('in_stock', 0),
        'low_stock': by_status.get('low_stock', 0),
        'out_of_stock': by_status.get('out_of_stock', 0),
    })

