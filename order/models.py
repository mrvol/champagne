from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models

from person.models import CURRENCY, BaseModel


class Order(BaseModel):
    buyer = models.ForeignKey('person.User', on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey('address.Address', on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=32, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.IntegerField(choices=CURRENCY)  # ISO 4217

    def __str__(self):
        return f'Order #{self.pk}'

    @classmethod
    def as_json(cls, qs):
        return [
            {
                'pk': o.pk,
                'status': o.status,
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
