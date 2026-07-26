import base64
import hashlib
import mimetypes
import uuid
from datetime import date

import httpx
from django.contrib.auth.models import AbstractUser
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files.base import ContentFile
from django.db import models


# NOTE: task.models imports BaseModel from this module, so importing task.models here
# at module level would be circular - Order/current_order are imported lazily in methods.

MIN_AGE = 18

CURRENCY = (
    (1, 'EUR'),
    (2, 'USD'),
    (3, 'GBP'),
)


def age_from_birthday(birthday):
    today = date.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))


class BaseModel(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    company_ids = models.JSONField(default=list, blank=True)  # ids of Company this record is scoped to
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    address = models.JSONField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)  # ISO 3166-1 alpha-2
    birthday = models.DateField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(max_length=32, blank=True, null=True)
    language = models.JSONField(default=list, blank=True)  # list of ISO 639-1 codes
    ui_language = models.CharField(max_length=8, blank=True, default='')  # site UI language, e.g. 'en', 'fr', 'ru'
    timezone = models.CharField(max_length=64, blank=True, null=True)
    primary_address = models.ForeignKey('address.Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    roles = models.JSONField(default=list, blank=True)  # e.g. ['buyer', 'seller']
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked = models.BooleanField(default=False)
    login_history = models.JSONField(default=list, blank=True)
    devices = models.JSONField(default=list, blank=True)
    kyc_status = models.CharField(max_length=32, blank=True, null=True)
    identity_documents = models.JSONField(default=list, blank=True)
    terms_accepted_at = models.DateTimeField(blank=True, null=True)
    gdpr_consent = models.BooleanField(default=False)

    def is_of_legal_age(self):
        return bool(self.birthday) and age_from_birthday(self.birthday) >= MIN_AGE

    @classmethod
    def as_json(cls, qs):
        return [
            {
                'pk': u.pk,
                'username': u.username,
                'email': u.email,
                'name': u.get_full_name() or u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'phone': u.phone,
                'country': u.country,
                'roles': u.roles,
                'is_staff': u.is_staff,
                'is_active': u.is_active,
                'email_verified': u.email_verified,
                'avatar_url': u.avatar.url if u.avatar else None,
                'date_joined': naturaltime(u.date_joined),
            }
            for u in qs
        ]

    def set_avatar_from_url(self, url: str) -> None:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').split(';')[0].strip()
        extension = mimetypes.guess_extension(content_type) or ''
        digest = hashlib.sha256(response.content).hexdigest()[:16]
        self.avatar.save(f'{digest}{extension}', ContentFile(response.content), save=True)

    def set_avatar_from_base64(self, data: str, extension: str = '.jpg') -> None:
        raw = base64.b64decode(data)
        digest = hashlib.sha256(raw).hexdigest()[:16]
        self.avatar.save(f'{digest}{extension}', ContentFile(raw), save=True)


class WebAuthnCredential(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webauthn_credentials')
    credential_id = models.BinaryField(unique=True)
    public_key_x = models.BinaryField()
    public_key_y = models.BinaryField()
    sign_count = models.PositiveIntegerField(default=0)
