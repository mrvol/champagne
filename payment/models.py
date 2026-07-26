from django.db import models

from order.models import Order
from person.models import CURRENCY, BaseModel


class Payment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey('person.User', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.IntegerField(choices=CURRENCY)  # ISO 4217
    status = models.CharField(max_length=32, blank=True, null=True)
    provider = models.CharField(max_length=64, blank=True, null=True)
    transaction_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f'Payment #{self.pk}'
