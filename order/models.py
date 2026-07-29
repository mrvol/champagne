from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.utils.translation import gettext_lazy as _

from person.models import CURRENCY, BaseModel


class Order(BaseModel):
    # The linear fulfilment pipeline. PIPELINE holds the codes in progress order (used to
    # compute "how far along" an order is); STATUS_CHOICES adds the two terminal exception
    # states (cancelled/refunded) that fall outside that line.
    STATUS_PLACED = 'placed'
    STATUS_PAYMENT_CONFIRMED = 'payment_confirmed'
    STATUS_PREPARING = 'preparing'
    STATUS_QUALITY_INSPECTION = 'quality_inspection'
    STATUS_PACKED = 'packed'
    STATUS_SHIPPED = 'shipped'
    STATUS_OUT_FOR_DELIVERY = 'out_for_delivery'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'

    PIPELINE = [
        (STATUS_PLACED, _('Order placed'), 'receipt'),
        (STATUS_PAYMENT_CONFIRMED, _('Payment confirmed'), 'card'),
        (STATUS_PREPARING, _('Preparing order'), 'box'),
        (STATUS_QUALITY_INSPECTION, _('Quality inspection'), 'check-shield'),
        (STATUS_PACKED, _('Packed'), 'package'),
        (STATUS_SHIPPED, _('Shipped'), 'truck'),
        (STATUS_OUT_FOR_DELIVERY, _('Out for delivery'), 'truck-fast'),
        (STATUS_DELIVERED, _('Delivered'), 'home'),
    ]
    STATUS_CHOICES = [(code, label) for code, label, icon in PIPELINE] + [
        (STATUS_CANCELLED, _('Cancelled')),
        (STATUS_REFUNDED, _('Refunded')),
    ]
    SHIPPED_STATUSES = (STATUS_SHIPPED, STATUS_OUT_FOR_DELIVERY, STATUS_DELIVERED)

    buyer = models.ForeignKey('person.User', on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey('address.Address', on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_PLACED)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.IntegerField(choices=CURRENCY)  # ISO 4217
    estimated_delivery = models.DateField(blank=True, null=True)
    carrier = models.CharField(max_length=64, blank=True, null=True)  # e.g. "DHL Express"
    tracking_number = models.CharField(max_length=64, blank=True, null=True)
    signature_required = models.BooleanField(default=False)
    delivery_instructions = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)  # buyer-visible notes on the order

    def __str__(self):
        return f'Order #{self.pk}'

    def pipeline_step(self):
        """Index of the current status within PIPELINE, or None for cancelled/refunded."""
        codes = [code for code, label, icon in self.PIPELINE]
        return codes.index(self.status) if self.status in codes else None

    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    def is_in_transit(self):
        return self.status in self.SHIPPED_STATUSES

    def status_icon(self):
        icons = {code: icon for code, label, icon in self.PIPELINE}
        icons[self.STATUS_CANCELLED] = 'cancelled'
        icons[self.STATUS_REFUNDED] = 'refunded'
        return icons.get(self.status, 'receipt')

    @classmethod
    def as_json(cls, qs):
        return [
            {
                'pk': o.pk,
                'status': o.status,
                'status_display': o.get_status_display(),
                'total_amount': o.total_amount,
                'currency': o.currency,
                'currency_display': o.get_currency_display(),
                'buyer': o.buyer.get_full_name() or o.buyer.username,
                'seller': str(o.seller),
                'delivery_address': str(o.delivery_address),
                'updated': naturaltime(o.changed),
            }
            for o in qs
        ]


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    good = models.ForeignKey('goods.Good', on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot: Good.price can change later

    def __str__(self):
        return f'{self.quantity} x {self.good}'

    def line_total(self):
        return self.unit_price * self.quantity
