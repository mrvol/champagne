from django.shortcuts import get_object_or_404, render

from goods.models import Good


def good_list(request):
    goods = Good.objects.all()
    return render(request, 'good_list.html', {'goods': goods})


def good_detail(request, pk):
    good = get_object_or_404(Good, pk=pk)
    return render(request, 'good_detail.html', {'good': good})
