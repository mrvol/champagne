import secrets

from django.db import models
from django.utils import timezone

from person.models import BaseModel


def generate_token():
    return secrets.token_urlsafe(32)


class Invitation(BaseModel):
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_EXPIRED = 'expired'
    STATUS_REVOKED = 'revoked'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_REVOKED, 'Revoked'),
    ]

    STEP_ACCOUNT = 'account'
    STEP_COMPANY = 'company'
    STEP_PRODUCTS = 'products'
    STEP_REVIEW = 'review'
    STEP_DONE = 'done'
    STEP_CHOICES = [
        (STEP_ACCOUNT, 'Account'),
        (STEP_COMPANY, 'Company profile'),
        (STEP_PRODUCTS, 'Product catalogue'),
        (STEP_REVIEW, 'Review & submit'),
        (STEP_DONE, 'Done'),
    ]

    token = models.CharField(max_length=64, unique=True, default=generate_token, editable=False)
    contact_email = models.EmailField()  # the Wine House contact the link is sent to
    contact_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    step = models.CharField(max_length=16, choices=STEP_CHOICES, default=STEP_ACCOUNT)
    invited_by = models.ForeignKey('person.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_invitations')
    user = models.ForeignKey('person.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='invitation')
    company = models.ForeignKey('company.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='invitation')
    expires_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Invitation for {self.contact_email} ({self.get_status_display()})'

    def is_usable(self):
        if self.status in (self.STATUS_REVOKED, self.STATUS_EXPIRED, self.STATUS_COMPLETED):
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            if self.status != self.STATUS_EXPIRED:
                self.status = self.STATUS_EXPIRED
                self.save(update_fields=['status'])
            return False
        return True

    def advance(self, step):
        # Plain save (not update_fields) - callers often set other fields (user, company)
        # on this same instance right before calling advance(); update_fields would drop them.
        self.step = step
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_IN_PROGRESS
        self.save()

    def mark_completed(self):
        self.status = self.STATUS_COMPLETED
        self.step = self.STEP_DONE
        self.completed_at = timezone.now()
        self.save()
