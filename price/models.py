from django.db import models

from goods.models import Good
from person.models import CURRENCY, BaseModel


class PriceHistory(BaseModel):
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.IntegerField(choices=CURRENCY)  # ISO 4217
