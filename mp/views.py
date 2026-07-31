from datetime import date

from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from company.models import Company
from goods.models import Good
from person.decorators import staff_required


def home(request):
    featured = Good.objects.filter(company__verified_seller=True).annotate(available=Sum('stock__quantity')).order_by('-created')[:6]
    producers = Company.objects.filter(verified_seller=True)[:3]

    # "Product of the day": a real, deterministic daily rotation (not a random pick per
    # request) over verified, in-stock goods, so the "today only" framing on the homepage
    # is actually true rather than decorative.
    eligible = list(
        Good.objects.filter(company__verified_seller=True)
        .annotate(available=Sum('stock__quantity')).filter(available__gt=0)
        .select_related('company')
    )
    pick = eligible[date.today().toordinal() % len(eligible)] if eligible else None
    pick_discount = None
    pick_price = pick.price if pick else None
    if pick:
        now = timezone.now()
        pick_discount = pick.discounts.filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
        ).order_by('-priority').first()
        if pick_discount and pick.price is not None:
            if pick_discount.percent_off:
                pick_price = pick.price * (1 - pick_discount.percent_off / 100)
            elif pick_discount.amount_off:
                pick_price = max(pick.price - pick_discount.amount_off, 0)

    return render(request, 'home.html', {
        'featured': featured, 'producers': producers,
        'pick': pick, 'pick_discount': pick_discount, 'pick_price': pick_price,
    })


@staff_required
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')