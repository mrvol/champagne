from django.db import models

from payment.models import Payment
from person.models import BaseModel


class Transaction(BaseModel):
    TYPE_CHARGE = 'charge'
    TYPE_REFUND = 'refund'
    TYPE_AUTHORIZATION = 'authorization'
    TYPE_CAPTURE = 'capture'
    TYPE_CHOICES = [
        (TYPE_CHARGE, 'Charge'),
        (TYPE_REFUND, 'Refund'),
        (TYPE_AUTHORIZATION, 'Authorization'),
        (TYPE_CAPTURE, 'Capture'),
    ]

    METHOD_CARD = 'card'
    METHOD_BANK_TRANSFER = 'bank_transfer'
    METHOD_GIFT_CARD = 'gift_card'
    METHOD_WALLET = 'wallet'
    METHOD_CHOICES = [
        (METHOD_CARD, 'Card'),
        (METHOD_BANK_TRANSFER, 'Bank transfer'),
        (METHOD_GIFT_CARD, 'Gift card'),
        (METHOD_WALLET, 'Wallet'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    method = models.CharField(max_length=32, choices=METHOD_CHOICES, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, blank=True, null=True)  # ISO 4217
    status = models.CharField(max_length=32, blank=True, null=True)
    provider = models.CharField(max_length=64, blank=True, null=True)  # e.g. stripe, paypal, gift card issuer
    provider_reference = models.CharField(max_length=128, blank=True, null=True)  # gateway/processor transaction id
    raw_response = models.JSONField(blank=True, null=True)  # technical/provider payload

    def __str__(self):
        return f'Transaction #{self.pk}'
