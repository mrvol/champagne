from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

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
        messages.error(request, _('%(name)s is out of stock.') % {'name': good.name})
    else:
        if quantity < desired:
            messages.warning(request, _('Only %(available)s of %(name)s in stock.') % {'available': available, 'name': good.name})
        item.quantity = quantity
        item.save()
    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user, status=Cart.STATUS_OPEN)
    cart.items.filter(pk=item_id).delete()
    return redirect('cart_detail')


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user, status=Cart.STATUS_OPEN)
    if request.method == 'POST':
        if not request.user.is_of_legal_age():
            messages.error(request, _('You must be at least %(age)s to place an order.') % {'age': MIN_AGE})
        else:
            address = get_object_or_404(Address, pk=request.POST.get('delivery_address'), user=request.user)
            order = cart.place_order(address)
            return redirect('order_detail', pk=order.pk)
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'cart_detail.html', {'cart': cart, 'addresses': addresses})


@login_required
def api_search(request):
    q = request.GET.get('q')
    if not q:
        return JsonResponse([], safe=False)
    qs = Good.objects.filter(name__icontains=q)
    return JsonResponse(Good.as_json(qs), safe=False)

