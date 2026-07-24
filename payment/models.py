from django.db import models

from order.models import Order
from person.models import BaseModel


class Payment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey('person.User', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True, null=True)  # ISO 4217
    status = models.CharField(max_length=32, blank=True, null=True)
    provider = models.CharField(max_length=64, blank=True, null=True)
    transaction_id = models.CharField(max_length=128, blank=True, null=True)
