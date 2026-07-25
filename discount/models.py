from django.db import models

from goods.models import Good
from person.models import BaseModel


class Discount(BaseModel):
    good = models.ForeignKey(Good, on_delete=models.CASCADE, null=True, blank=True, related_name='discounts')  # null = applies storewide
    rule_type = models.CharField(max_length=32)  # e.g. 'quantity', 'seasonal', 'new_good'
    params = models.JSONField(default=dict, blank=True)  # e.g. {'min_quantity': 10} or {'max_age_days': 30}
    percent_off = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    amount_off = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    starts_at = models.DateTimeField(blank=True, null=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    priority = models.PositiveIntegerField(default=0)  # combining/ordering multiple applicable discounts
