import hashlib
from pathlib import Path

import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.forms import ModelForm

from person.models import BaseModel

# Create your models here.

class Company(BaseModel):
    hero_photo = models.ForeignKey('CompanyPhoto', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    legal_name = models.CharField(max_length=255, blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)  # short brand identity line for the hero
    story = models.TextField(blank=True, null=True)  # brand story: heritage, craftsmanship, values
    registration_number = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO 3166-1 alpha-2, jurisdiction of registration
    region = models.CharField(max_length=255, blank=True, null=True)  # wine region / appellation, e.g. "Champagne, France"
    tax_id = models.CharField(max_length=64, blank=True, null=True)  # VAT/EIN/etc.
    vat_number = models.CharField(max_length=64, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    certifications = models.JSONField(default=list, blank=True)  # e.g. ["Organic", "AOC Champagne", "HVE3"]
    annual_production = models.PositiveIntegerField(blank=True, null=True)  # bottles per year
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=32, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    employee_count = models.PositiveIntegerField(blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    trust_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    verified_seller = models.BooleanField(default=False)
    dispute_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.legal_name or f'Company #{self.pk}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def grape_varieties(self):
        varieties = []
        for value in self.goods.exclude(grape_variety__isnull=True).exclude(grape_variety='').values_list('grape_variety', flat=True):
            for variety in value.split(','):
                variety = variety.strip()
                if variety and variety not in varieties:
                    varieties.append(variety)
        return varieties

    def make_hero(self, photo_id):
        if self.photos.filter(pk=photo_id).exists():
            self.hero_photo_id = photo_id
            self.save()

    def upload(self, url_or_path):
        if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
            content = httpx.get(url_or_path, timeout=10).content
        else:
            content = Path(url_or_path).read_bytes()
        digest = hashlib.md5(content).hexdigest()

        photo = CompanyPhoto.objects.filter(md5=digest).first()
        if not photo:
            photo = CompanyPhoto.objects.create(company=self, md5=digest)
            directory = photo.md5_path()
            relative_name = directory.relative_to(settings.MEDIA_ROOT) / f'{digest}.jpg'
            photo.image.save(str(relative_name), ContentFile(content), save=True)

        if self.hero_photo_id is None:
            self.hero_photo_id = photo.pk
            self.save()
        return photo


class CompanyPhoto(BaseModel):
    md5 = models.CharField(max_length=32, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField()
    description = models.CharField(max_length=255, blank=True, null=True)

    def md5_path(self):
        p = Path(settings.MEDIA_ROOT) / 'int_storage' / 'cc' / self.md5[:2] / self.md5[2:4] / self.md5[4:6] / self.md5
        p.mkdir(parents=True, exist_ok=True)
        return p


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
