from django.db.models import Sum
from django.shortcuts import render

from company.models import Company
from goods.models import Good


def home(request):
    featured = Good.objects.filter(company__verified_seller=True).annotate(available=Sum('stock__quantity')).order_by('-created')[:6]
    producers = Company.objects.filter(verified_seller=True)[:3]
    return render(request, 'home.html', {'featured': featured, 'producers': producers})


def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')