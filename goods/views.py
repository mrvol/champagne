from django.db.models import Sum
from django.shortcuts import get_object_or_404, render

from goods.models import Good
from warehouse.models import Stock


def good_list(request):
    goods = Good.objects.all()
    return render(request, 'good_list.html', {'goods': goods})


def good_detail(request, pk):
    good = get_object_or_404(Good, pk=pk)
    available = Stock.objects.filter(good=good).aggregate(total=Sum('quantity'))['total'] or 0
    return render(request, 'good_detail.html', {'good': good, 'available': available})
