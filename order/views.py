from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from cart.models import Cart, CartItem
from goods.models import Good
from order.models import Order
from person.decorators import staff_api_required, staff_required

TRACKING_STEPS = [
    (9.25, _('Order collected from warehouse')),
    (12.67, _('Arrived at regional sorting centre')),
    (18.33, _('Departed sorting facility')),
    (32.17, _('In transit to destination city')),
    (40.0, _('Out for delivery')),
]


def tracking_timeline(order):
    """A deterministic (not random) shipment timeline for shipped-ish orders, anchored to
    the order's own created/changed timestamps rather than invented from nothing."""
    if order.status not in Order.SHIPPED_STATUSES:
        return None
    fully_done = order.status in (Order.STATUS_OUT_FOR_DELIVERY, Order.STATUS_DELIVERED)
    events = [
        {'at': order.created + timedelta(hours=hours), 'label': label, 'done': fully_done or hours <= 18.33}
        for hours, label in TRACKING_STEPS
    ]
    if order.status == Order.STATUS_DELIVERED:
        events.append({'at': order.changed, 'label': _('Delivered'), 'done': True})
    return events


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(buyer=request.user)
        .select_related('seller', 'delivery_address')
        .prefetch_related('items__good')
        .order_by('-created')
    )
    for order in orders:
        order.tracking = tracking_timeline(order)
    suggested = None
    if not orders:
        suggested = (
            Good.objects.filter(company__verified_seller=True)
            .annotate(available=Sum('stock__quantity')).order_by('-created')[:4]
        )
    return render(request, 'order_list.html', {'orders': orders, 'pipeline': Order.PIPELINE, 'suggested': suggested})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related('seller', 'delivery_address').prefetch_related('items__good', 'payments'), pk=pk, buyer=request.user)
    order.tracking = tracking_timeline(order)
    return render(request, 'order_detail.html', {'order': order, 'pipeline': Order.PIPELINE})


@login_required
def order_invoice(request, pk):
    order = get_object_or_404(Order.objects.select_related('seller', 'buyer', 'delivery_address').prefetch_related('items__good'), pk=pk, buyer=request.user)
    return render(request, 'order_invoice.html', {'order': order})


@login_required
def order_reorder(request, pk):
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    cart, _created = Cart.objects.get_or_create(user=request.user, status=Cart.STATUS_OPEN)
    for item in order.items.select_related('good'):
        cart_item, created = CartItem.objects.get_or_create(cart=cart, good=item.good, defaults={'quantity': 0})
        cart_item.quantity += item.quantity
        cart_item.save()
    messages.success(request, _('Items from Order #%(pk)s added to your cart.') % {'pk': order.pk})
    return redirect('cart_detail')


@staff_api_required
def order_list_api(request):
    return JsonResponse(Order.as_json(Order.objects.all()), safe=False)


@staff_api_required
def order_detail_api(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status', '')
        if status not in dict(Order.STATUS_CHOICES):
            return JsonResponse({'error': 'invalid status'}, status=400)
        order.status = status
        order.save()
    return JsonResponse(Order.as_json([order])[0])


@staff_required
def staff_order_list(request):
    return render(request, 'staff_order_list.html')
