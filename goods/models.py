from django.db import models

from company.models import Company
from person.models import BaseModel


class Good(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='goods')
    name = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=64, blank=True, null=True)
    vintage_year = models.PositiveSmallIntegerField(blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)  # appellation / region of origin
    grape_variety = models.CharField(max_length=255, blank=True, null=True)
    volume_ml = models.PositiveIntegerField(blank=True, null=True)  # bottle size, e.g. 750
    abv = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  # alcohol by volume %
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)  # ISO 4217
