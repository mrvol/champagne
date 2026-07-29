from datetime import timedelta

from django.db import models
from django.utils import timezone

from address.models import Address
from goods.models import Good
from order.models import Order, OrderItem
from person.models import BaseModel, User


class Cart(BaseModel):
    STATUS_OPEN = 'open'
    STATUS_ORDERED = 'ordered'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_ORDERED, 'Ordered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)

    def total_amount(self):
        return sum(item.good.price * item.quantity for item in self.items.all())

    def place_order(self, delivery_address: Address) -> Order:
        first_item = self.items.first()
        order = Order.objects.create(
            buyer=self.user,
            seller=first_item.good.company,
            delivery_address=delivery_address,
            status=Order.STATUS_PLACED,
            total_amount=self.total_amount(),
            currency=first_item.good.currency,
            estimated_delivery=timezone.now().date() + timedelta(days=5),
        )
        for item in self.items.all():
            OrderItem.objects.create(order=order, good=item.good, quantity=item.quantity, unit_price=item.good.price)
        self.status = self.STATUS_ORDERED
        self.save()
        return order


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
