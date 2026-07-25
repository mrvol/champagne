from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, render

from goods.models import Good
from warehouse.models import Stock


def good_list(request):
    q = request.GET.get('q', '').strip()
    goods = Good.objects.all()
    if q:
        goods = goods.filter(Q(name__icontains=q) | Q(region__icontains=q) | Q(grape_variety__icontains=q))
    return render(request, 'good_list.html', {'goods': goods, 'q': q})


def good_detail(request, pk):
    good = get_object_or_404(Good, pk=pk)
    available = Stock.objects.filter(good=good).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'good_detail.html', {
        'good': good,
        'available': available,
        'grape_varieties': good.grape_variety_list(),
    })
