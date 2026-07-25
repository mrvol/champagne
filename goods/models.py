import hashlib
from pathlib import Path

import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models

from company.models import Company
from person.models import BaseModel


class Good(BaseModel):
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
    currency = models.CharField(max_length=3, blank=True, null=True)  # ISO 4217

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

    def make_main(self, photo_id):
        if self.photos.filter(pk=photo_id).exists():
            self.photo_id = photo_id
            self.save()

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

