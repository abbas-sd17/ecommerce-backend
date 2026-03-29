"""
Razorpay payment gateway implementation.
Lecture 9 — RazorPay Integration with abstract class pattern.
"""
import hashlib
import hmac
from typing import Optional

from django.conf import settings
from .base import PaymentGateway


class RazorpayPaymentGateway(PaymentGateway):
    """
    Razorpay implementation of PaymentGateway.
    Taught in Lecture 9 — Payment Gateway Abstract Class.

    Uses Razorpay's payment link API to generate payment URLs.
    Amounts passed as integers (paise) — avoids floating point issues (Lecture 8).
    Callback URLs must be public domain, not localhost (Lecture 9).
    """

    def __init__(self):
        try:
            import razorpay
            self.client = razorpay.Client(
                auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET)
            )
        except ImportError:
            self.client = None

    def create_payment_link(self, order_id: str, payment_id: str, amount: int) -> dict:
        """
        Creates a Razorpay payment link.
        Amount must be in paise (100 paise = ₹1).
        """
        if not self.client:
            # Mock response when razorpay package not installed (dev mode)
            return {
                "payment_link": f"https://rzp.io/mock/{payment_id}",
                "gateway_order_id": f"order_mock_{order_id}",
                "payment_id": payment_id,
            }

        base_callback = getattr(settings, 'RAZORPAY_CALLBACK_URL', '').rstrip('/')
        sep = '&' if '?' in base_callback else '?'
        callback_url = f"{base_callback}{sep}payment_id={payment_id}"

        payment_data = {
            "amount": amount,
            "currency": "INR",
            "accept_partial": False,
            "reference_id": payment_id,
            "description": f"Payment for Order {order_id}",
            "notes": {
                "internal_payment_id": str(payment_id),
                "order_id": str(order_id),
            },
            "notify": {
                "sms": True,
                "email": True
            },
            "reminder_enable": True,
            "callback_url": callback_url,
            "callback_method": "get"
        }

        response = self.client.payment_link.create(data=payment_data)
        return {
            "payment_link": response.get("short_url"),
            "gateway_order_id": response.get("id"),
            "payment_id": payment_id,
        }

    def verify_payment(self, gateway_order_id: str, gateway_payment_id: str, signature: str) -> bool:
        """
        Verifies Razorpay payment signature using HMAC-SHA256.
        Security: prevents man-in-the-middle attacks (Lecture 8).
        """
        if not self.client:
            # Mock verification in dev mode
            return True

        try:
            self.client.utility.verify_payment_link_signature({
                "razorpay_payment_link_id": gateway_order_id,
                "razorpay_payment_id": gateway_payment_id,
                "razorpay_signature": signature,
            })
            return True
        except Exception:
            return False

    def verify_webhook_signature(self, raw_body: bytes, signature_header: Optional[str] = None) -> bool:
        """
        Razorpay: HMAC-SHA256(hex) of raw body with webhook secret (Lecture 8).
        If RAZORPAY_WEBHOOK_SECRET is unset, accepts any request (local dev only).
        """
        secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '') or ''
        if not secret:
            return True
        if not signature_header:
            return False
        expected = hmac.new(
            secret.encode('utf-8'),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature_header)
