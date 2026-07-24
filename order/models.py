from django.db import models

from person.models import BaseModel


class Order(BaseModel):
    buyer = models.ForeignKey('person.User', on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey('company.Company', on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey('address.Address', on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=32, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, blank=True, null=True)  # ISO 4217
