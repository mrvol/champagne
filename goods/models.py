import hashlib
from pathlib import Path

import httpx
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Sum

from company.models import Company
from person.models import CURRENCY, BaseModel


# | Classification                                                            |           Residual Sugar | Taste                                                   |
# | ------------------------------------------------------------------------- | -----------------------: | ------------------------------------------------------- |
# | **Brut Nature** (also called **Pas Dosé**, **Dosage Zéro**, **Non Dosé**) | 0–3 g/L (no added sugar) | Bone dry, very crisp, mineral                           |
# | **Extra Brut**                                                            |                  0–6 g/L | Extremely dry                                           |
# | **Brut**                                                                  |         Less than 12 g/L | Dry; the most common style (around 80–90% of Champagne) |
# | **Extra Dry** (*Extra Sec*)                                               |                12–17 g/L | Slightly sweeter than Brut (despite the confusing name) |
# | **Sec**                                                                   |                17–32 g/L | Noticeably sweet                                        |
# | **Demi-Sec**                                                              |                32–50 g/L | Sweet; often paired with desserts                       |
# | **Doux**                                                                  |         More than 50 g/L | Very sweet; now quite rare                              |


class Good(BaseModel):
    SUGAR_LEVEL = (
        (3, 'Brut Nature'),
        (6, 'Extra Brut'),
        (12, 'Brut'),
        (17, 'Extra Dry (Extra Sec)'),
        (32, 'Sec'),
        (50, 'Demi-Sec'),
        (51, 'Doux'),
    )

    TYPE_CHOICES = [
        ('still', 'Still'),
        ('sparkling', 'Sparkling'),
        ('fortified', 'Fortified'),
        ('dessert', 'Dessert'),
        ('rose', 'Rosé'),
    ]

    STOCK_CHOICES = [
        ('in_stock', 'In stock'),
        ('low_stock', 'Low stock'),
        ('out_of_stock', 'Out of stock'),
        ('pre_order', 'Pre-order'),
    ]

    photo = models.ForeignKey('GoodPhoto', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    description = models.TextField(blank=True, null=True)
    bullets = models.JSONField(default=list, blank=True)  # short marketing bullet points
    groups = models.ManyToManyField('GoodGroup', blank=True, related_name='goods')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='goods')
    name = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=64, blank=True, null=True)
    vintage_year = models.PositiveSmallIntegerField(blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)  # appellation / region of origin
    grape_variety = models.CharField(max_length=255, blank=True, null=True)
    volume_ml = models.PositiveIntegerField(blank=True, null=True)  # bottle size, e.g. 750
    abv = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)  # alcohol by volume %
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.IntegerField(choices=CURRENCY)  # ISO 4217
    sugar_level = models.IntegerField(choices=SUGAR_LEVEL, blank=True, null=True)  # upper g/L bound of residual sugar, per classification table above

    barcode = models.CharField(max_length=64, blank=True, null=True)
    planted = models.DateField(blank=True, null=True)  # vineyard planting date
    soil_type = models.CharField(max_length=255, blank=True, null=True)
    elevation = models.PositiveIntegerField(blank=True, null=True)  # vineyard elevation, meters above sea level
    slope = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)  # vineyard slope, % grade
    harvested = models.DateField(blank=True, null=True)
    organic_certified = models.BooleanField(default=False)

    # vineyard
    # row_vineyard
    # positionInRow

    wine_type = models.CharField(max_length=16, choices=TYPE_CHOICES, blank=True, null=True)
    food_pairing = models.TextField(blank=True, null=True)
    awards = models.JSONField(default=list, blank=True)  # e.g. ["Decanter Gold 2023"]
    available_quantity = models.PositiveIntegerField(blank=True, null=True)  # simple onboarding-level stock count
    min_order_quantity = models.PositiveIntegerField(blank=True, null=True)
    stock_status = models.CharField(max_length=16, choices=STOCK_CHOICES, default='in_stock')

    def get_quantity(self):
        return self.stock.aggregate(total=Sum('quantity'))['total'] or 0

    def get_quantity_str(self):
        if self.stock_status == 'pre_order':
            return self.get_stock_status_display()
        q = self.get_quantity()
        if not q:
            return 'Out of stock'
        if q <= 10:
            return 'Low stock'
        return 'In stock'

    @classmethod
    def as_json(cls, qs):
        qs = qs.annotate(available=Sum('stock__quantity'))
        return [
            {
                'pk': g.pk,
                'name': g.name,
                'sku': g.sku,
                'description': g.description,
                'vintage_year': g.vintage_year,
                'region': g.region,
                'grape_variety': g.grape_variety,
                'wine_type': g.wine_type,
                'sugar_level': g.sugar_level,
                'style': g.get_sugar_level_display() if g.sugar_level else g.get_wine_type_display(),
                'price': g.price,
                'currency': g.currency,
                'volume_ml': g.volume_ml,
                'abv': g.abv,
                'available': g.available or 0,
                'available_quantity': g.available_quantity,
                'min_order_quantity': g.min_order_quantity,
                'organic_certified': g.organic_certified,
                'barcode': g.barcode,
                'stock_status': g.stock_status,
                'stock_status_display': g.get_stock_status_display(),
                'updated': naturaltime(g.changed),
                'photo_url': g.photo.image.url if g.photo else None,
            }
            for g in qs
        ]

    def grape_variety_list(self):
        if not self.grape_variety:
            return []
        return [v.strip() for v in self.grape_variety.split(',') if v.strip()]

    def make_main(self, photo_id):
        if self.photos.filter(pk=photo_id).exists():
            self.photo_id = photo_id
            self.save()

    def attach_photo(self, uploaded_file):
        content = uploaded_file.read()
        digest = hashlib.md5(content).hexdigest()
        photo = self.photos.filter(md5=digest).first()
        if not photo:
            uploaded_file.seek(0)
            photo = GoodPhoto.objects.create(good=self, md5=digest, image=uploaded_file)
        if self.photo_id is None:
            self.photo_id = photo.pk
            self.save()
        return photo

    def upload(self, url_or_path):
        if url_or_path.startswith('http://') or url_or_path.startswith('https://'):
            content = httpx.get(url_or_path, timeout=10).content
        else:
            content = Path(url_or_path).read_bytes()
        digest = hashlib.md5(content).hexdigest()

        photo = GoodPhoto.objects.filter(md5=digest).first()
        if not photo:
            photo = GoodPhoto.objects.create(good=self, md5=digest)
            directory = photo.md5_path()
            relative_name = directory.relative_to(settings.MEDIA_ROOT) / f'{digest}.jpg'
            photo.image.save(str(relative_name), ContentFile(content), save=True)

        if self.photo_id is None:
            self.photo_id = photo.pk
            self.save()
        return photo

    def __str__(self):
        return self.name or f'Good #{self.pk}'


class GoodPhoto(BaseModel):
    md5 = models.CharField(max_length=32, unique=True)
    good = models.ForeignKey(Good, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField()
    description = models.CharField(max_length=255, blank=True, null=True)

    def md5_path(self):
        p = Path(settings.MEDIA_ROOT) / 'int_storage' / 'cv' / self.md5[:2] / self.md5[2:4] / self.md5[4:6] / self.md5
        p.mkdir(parents=True, exist_ok=True)
        return p


class GoodGroup(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

