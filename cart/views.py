from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from address.models import Address
from cart.models import Cart
from goods.models import Good
from person.models import MIN_AGE
from warehouse.models import Stock


@login_required
def add_to_cart(request, pk):
    good = get_object_or_404(Good, pk=pk)
    requested = int(request.POST.get('quantity') or 1)
    available = Stock.objects.filter(good=good).aggregate(total=Sum('quantity'))['total'] or 0

    cart, _ = Cart.objects.get_or_create(user=request.user, status=Cart.STATUS_OPEN)
    item, created = cart.items.get_or_create(good=good, defaults={'quantity': 0})
    desired = item.quantity + requested
    quantity = min(desired, available)

    if quantity <= 0:
        if created:
            item.delete()
        messages.error(request, f'{good.name} is out of stock.')
    else:
        if quantity < desired:
            messages.warning(request, f'Only {available} of {good.name} in stock.')
        item.quantity = quantity
        item.save()
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user, status=Cart.STATUS_OPEN)
    if request.method == 'POST':
        if not request.user.is_of_legal_age():
            messages.error(request, f'You must be at least {MIN_AGE} to place an order.')
        else:
            address = get_object_or_404(Address, pk=request.POST.get('delivery_address'), user=request.user)
            order = cart.place_order(address)
            return redirect('order_detail', pk=order.pk)
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart, 'addresses': addresses})
