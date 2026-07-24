from django.db import models

from goods.models import Good
from person.models import BaseModel


class Warehouse(BaseModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO 3166-1 alpha-2
    city = models.CharField(max_length=128, blank=True, null=True)
    address = models.TextField(blank=True, null=True)


class Stock(BaseModel):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='stock')
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='stock')
    quantity = models.PositiveIntegerField(default=0)
