from django.db.models import Sum
from django.shortcuts import render

from company.models import Company
from goods.models import Good


def home(request):
    featured = Good.objects.annotate(available=Sum('stock__quantity')).order_by('-created')[:6]
    producers = Company.objects.all()[:3]
    return render(request, 'home.html', {'featured': featured, 'producers': producers})