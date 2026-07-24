from django.db import models

from person.models import BaseModel


class Address(BaseModel):
    TYPE_CHOICES = [
        ('p', 'Primary'),
        ('b', 'Billing'),
    ]

    type = models.JSONField(default=list)
    user = models.ForeignKey('person.User', on_delete=models.CASCADE, related_name='addresses')
    line1 = models.CharField(max_length=255, blank=True, null=True)
    line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    region = models.CharField(max_length=128, blank=True, null=True)
    postal_code = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO 3166-1 alpha-2
