"""
Abstract base class for payment gateways.
Lecture 9 — Abstract Classes, multiple payment gateway support.
"""
from abc import ABC, abstractmethod
from typing import Optional


class PaymentGateway(ABC):
    """
    Abstract base class for all payment gateways.
    Taught in Lecture 9 — Abstract Classes in Python.

    Any gateway (Razorpay, Stripe, PayU) must implement get_payment().
    This ensures a uniform interface regardless of the gateway used.
    """

    @abstractmethod
    def create_payment_link(self, order_id: str, payment_id: str, amount: int) -> dict:
        """
        Creates a payment link for the user.
        :param order_id: The order being paid for
        :param payment_id: Unique payment ID (idempotency key)
        :param amount: Amount in smallest currency unit (paise for INR)
        :return: dict with payment_link and gateway_order_id
        """
        pass

    @abstractmethod
    def verify_payment(self, gateway_order_id: str, gateway_payment_id: str, signature: str) -> bool:
        """
        Verifies payment signature from the gateway.
        :return: True if payment is valid, False otherwise
        """
        pass

    def verify_webhook_signature(self, raw_body: bytes, signature_header: Optional[str] = None) -> bool:
        """
        Optional webhook HMAC verification (Lecture 8).
        Default: allow (for gateways without webhook signing). Override in concrete gateways.
        """
        return True
