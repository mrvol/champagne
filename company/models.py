import hashlib
from pathlib import Path

import httpx
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.base import ContentFile
from django.db import models

from person.models import BaseModel, CURRENCY

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
    verified_seller = models.BooleanField(default=False)  # also doubles as the "approved & public" gate for onboarded Wine Houses
    dispute_count = models.PositiveIntegerField(default=0)

    # --- Company information (onboarding) ---
    name = models.CharField(max_length=255, blank=True, null=True)  # trade/brand name, may differ from legal_name
    founders = models.JSONField(default=list, blank=True)  # list of founder names
    ownership_info = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # general/marketing description
    history = models.TextField(blank=True, null=True)  # winery history
    awards = models.JSONField(default=list, blank=True)  # e.g. ["Decanter Gold 2023"]
    languages_spoken = models.JSONField(default=list, blank=True)  # ISO 639-1 codes the house can do business in

    # --- Business contact (onboarding) ---
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    contact_position = models.CharField(max_length=255, blank=True, null=True)
    support_contact = models.CharField(max_length=255, blank=True, null=True)  # customer support email/phone

    # --- Address & location (onboarding) ---
    registered_address = models.TextField(blank=True, null=True)
    operational_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    postal_code = models.CharField(max_length=32, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # --- Banking & financial (onboarding) ---
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_holder = models.CharField(max_length=255, blank=True, null=True)
    iban = models.CharField(max_length=64, blank=True, null=True)
    swift_bic = models.CharField(max_length=32, blank=True, null=True)
    bank_account_number = models.CharField(max_length=64, blank=True, null=True)
    payment_terms = models.CharField(max_length=64, blank=True, null=True)  # e.g. "Net 30"
    currency = models.CharField(choices=CURRENCY, default=1)  # ISO 4217

    # --- Public profile (onboarding) ---
    social_links = models.JSONField(default=dict, blank=True)  # {"instagram": "https://...", ...}
    pr_website = models.URLField(blank=True, null=True)
    press_kit_url = models.URLField(blank=True, null=True)
    sustainability_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.legal_name or f'Company #{self.pk}'

    @classmethod
    def as_json(cls, qs):
        return [
            {
                'pk': c.pk,
                'name': c.name or c.legal_name,
                'legal_name': c.legal_name,
                'country': c.country,
                'region': c.region,
                'industry': c.industry,
                'verified_seller': c.verified_seller,
                'rating': c.rating,
                'review_count': c.review_count,
                'trust_score': c.trust_score,
                'contact_email': c.contact_email,
                'contact_phone': c.contact_phone,
                'website': c.website,
                'logo_url': c.logo_url,
                'updated': naturaltime(c.changed),
            }
            for c in qs
        ]

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

    def attach_photo(self, uploaded_file, category=None):
        content = uploaded_file.read()
        digest = hashlib.md5(content).hexdigest()
        photo = self.photos.filter(md5=digest).first()
        if not photo:
            uploaded_file.seek(0)
            photo = CompanyPhoto.objects.create(company=self, md5=digest, category=category or CompanyPhoto.CATEGORY_OTHER, image=uploaded_file)
        if self.hero_photo_id is None:
            self.hero_photo_id = photo.pk
            self.save()
        return photo

    def upload(self, url_or_path, category=None):
        if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
            content = httpx.get(url_or_path, timeout=10).content
        else:
            content = Path(url_or_path).read_bytes()
        digest = hashlib.md5(content).hexdigest()

        photo = CompanyPhoto.objects.filter(md5=digest).first()
        if not photo:
            photo = CompanyPhoto.objects.create(company=self, md5=digest, category=category or CompanyPhoto.CATEGORY_OTHER)
            directory = photo.md5_path()
            relative_name = directory.relative_to(settings.MEDIA_ROOT) / f'{digest}.jpg'
            photo.image.save(str(relative_name), ContentFile(content), save=True)

        if self.hero_photo_id is None:
            self.hero_photo_id = photo.pk
            self.save()
        return photo


class CompanyPhoto(BaseModel):
    CATEGORY_WINERY = 'winery'
    CATEGORY_VINEYARD = 'vineyard'
    CATEGORY_CELLAR = 'cellar'
    CATEGORY_OTHER = 'other'
    CATEGORY_CHOICES = [
        (CATEGORY_WINERY, 'Winery'),
        (CATEGORY_VINEYARD, 'Vineyard'),
        (CATEGORY_CELLAR, 'Cellar'),
        (CATEGORY_OTHER, 'Other'),
    ]

    md5 = models.CharField(max_length=32, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField()
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    description = models.CharField(max_length=255, blank=True, null=True)

    def md5_path(self):
        p = Path(settings.MEDIA_ROOT) / 'int_storage' / 'cc' / self.md5[:2] / self.md5[2:4] / self.md5[4:6] / self.md5
        p.mkdir(parents=True, exist_ok=True)
        return p
