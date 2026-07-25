from django.shortcuts import render

from goods.models import Good


def home(request):
    featured = Good.objects.order_by('-created')[:6]
    return render(request, 'home.html', {'featured': featured})