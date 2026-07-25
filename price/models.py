from django.db import models

from goods.models import Good
from person.models import BaseModel


class PriceHistory(BaseModel):
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True, null=True)  # ISO 4217
