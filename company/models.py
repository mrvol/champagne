from django.db import models
from django.forms import ModelForm

from person.models import BaseModel

# Create your models here.

class Company(BaseModel):
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    registration_number = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO 3166-1 alpha-2, jurisdiction of registration
    tax_id = models.CharField(max_length=64, blank=True, null=True)  # VAT/EIN/etc.
    vat_number = models.CharField(max_length=64, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    employee_count = models.PositiveIntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    verified_seller = models.BooleanField(default=False)
    dispute_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
