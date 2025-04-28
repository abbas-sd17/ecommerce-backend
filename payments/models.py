"""
Payment models.
Lecture 8: Idempotency in payments — unique payment_id per transaction.
Lecture 9: Payment model linked to orders, multiple payment methods.
"""
from django.db import models
from django.contrib.auth.models import User


class Payment(models.Model):
    """
    Stores payment records with idempotency support.
    Lecture 8 — Idempotency: payment_id is the unique idempotency key.
    Each payment attempt gets a unique payment_id ensuring one charge.
    """
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_METHOD = [
        ('RAZORPAY', 'Razorpay'),
        ('WALLET', 'Wallet'),
        ('CREDIT_CARD', 'Credit Card'),
        ('UPI', 'UPI'),
    ]

    # Idempotency key — unique per payment attempt (Lecture 8)
    payment_id = models.CharField(max_length=255, unique=True)

    # FK to order — order_id alone is NOT sufficient (Lecture 8, partial payments)
    order_id = models.CharField(max_length=100)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.IntegerField()  # Stored as integer (paise), avoids float issues
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, default='RAZORPAY')

    # Gateway-specific fields
    gateway_payment_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_order_id = models.CharField(max_length=255, blank=True, null=True)
    gateway_signature = models.CharField(max_length=255, blank=True, null=True)

    # Webhook tracking (Lecture 8)
    webhook_received = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_id} — {self.status}"
