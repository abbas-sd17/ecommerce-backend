"""
Payment service layer.
Lecture 9 — Business logic in service layer (keep views thin).
Lecture 8 — Idempotency, webhook handling, reconciliation.
"""
import uuid
from typing import Optional

from django.db import IntegrityError, transaction

from ..models import Payment
from ..gateways.razorpay_gateway import RazorpayPaymentGateway


class PaymentService:
    """
    Handles all payment business logic.
    Taught in Lecture 9 — Service layer pattern.
    Views delegate to this service; gateways are injected via abstract class.
    """

    def __init__(self, gateway=None):
        self.gateway = gateway or RazorpayPaymentGateway()

    def initiate_payment(
        self,
        order_id: str,
        amount: int,
        user,
        client_idempotency_key: Optional[str] = None,
    ) -> dict:
        """
        Initiates a payment for an order.

        Idempotency (Lecture 8):
        - Each row has unique server `payment_id`.
        - Optional `client_idempotency_key`: duplicate requests return the same
          payment row and cached link without creating a second Razorpay link.
        """
        if client_idempotency_key:
            existing = Payment.objects.filter(
                client_idempotency_key=client_idempotency_key
            ).first()
            if existing:
                link = existing.payment_link_url or ''
                if not link and existing.gateway_order_id:
                    link = f"https://rzp.io/i/{existing.gateway_order_id}"
                return {
                    "payment_id": existing.payment_id,
                    "payment_link": link,
                    "amount": existing.amount,
                    "order_id": existing.order_id,
                    "idempotent_replay": True,
                }

        payment_id = f"pay_{uuid.uuid4().hex}"

        try:
            with transaction.atomic():
                payment = Payment.objects.create(
                    payment_id=payment_id,
                    order_id=order_id,
                    user=user,
                    amount=amount,
                    status='PENDING',
                    client_idempotency_key=client_idempotency_key or None,
                )
        except IntegrityError:
            if client_idempotency_key:
                existing = Payment.objects.filter(
                    client_idempotency_key=client_idempotency_key
                ).first()
                if existing:
                    link = existing.payment_link_url or ''
                    if not link and existing.gateway_order_id:
                        link = f"https://rzp.io/i/{existing.gateway_order_id}"
                    return {
                        "payment_id": existing.payment_id,
                        "payment_link": link,
                        "amount": existing.amount,
                        "order_id": existing.order_id,
                        "idempotent_replay": True,
                    }
            raise

        try:
            gateway_response = self.gateway.create_payment_link(
                order_id, payment_id, amount
            )
        except Exception as exc:
            payment.status = 'FAILED'
            payment.save(update_fields=['status', 'updated_at'])
            return {
                "error": "gateway_error",
                "detail": str(exc),
                "payment_id": payment_id,
            }

        payment.gateway_order_id = gateway_response.get('gateway_order_id')
        payment.payment_link_url = gateway_response.get('payment_link')
        payment.save(update_fields=['gateway_order_id', 'payment_link_url', 'updated_at'])

        return {
            "payment_id": payment_id,
            "payment_link": gateway_response.get("payment_link"),
            "amount": amount,
            "order_id": order_id,
            "idempotent_replay": False,
        }

    def verify_and_confirm(self, payment_id: str, gateway_payment_id: str, signature: str) -> dict:
        """
        Verifies payment after user completes it (callback / frontend POST).
        Idempotent: already SUCCESS returns success without re-verifying (Lecture 8).
        """
        try:
            payment = Payment.objects.get(payment_id=payment_id)
        except Payment.DoesNotExist:
            return {"success": False, "error": "Payment not found"}

        if payment.status == 'SUCCESS':
            return {
                "success": True,
                "payment_id": payment_id,
                "status": "SUCCESS",
                "idempotent_replay": True,
            }

        is_valid = self.gateway.verify_payment(
            gateway_order_id=payment.gateway_order_id,
            gateway_payment_id=gateway_payment_id,
            signature=signature,
        )

        if is_valid:
            payment.status = 'SUCCESS'
            payment.gateway_payment_id = gateway_payment_id
            payment.gateway_signature = signature
            payment.save()
            return {"success": True, "payment_id": payment_id, "status": "SUCCESS"}

        payment.status = 'FAILED'
        payment.save(update_fields=['status', 'updated_at'])
        return {"success": False, "error": "Signature verification failed"}

    def handle_webhook(self, payload: dict) -> dict:
        """
        Razorpay webhook events (Lecture 8).
        Idempotent: repeated webhooks for the same outcome are safe.
        """
        event = payload.get('event')
        internal_id = self._extract_internal_payment_id(payload, event)
        if not internal_id:
            return {"status": "unhandled_event", "event": event, "reason": "no_internal_payment_id"}

        try:
            payment = Payment.objects.get(payment_id=internal_id)
        except Payment.DoesNotExist:
            return {"status": "payment_not_found", "payment_id": internal_id}

        if event in ('payment_link.paid', 'payment.captured'):
            if payment.status == 'SUCCESS' and payment.webhook_received:
                return {"status": "ok", "payment_id": internal_id, "idempotent_replay": True}
            gw_id = self._extract_gateway_payment_id(payload, event)
            if gw_id:
                payment.gateway_payment_id = gw_id
            payment.status = 'SUCCESS'
            payment.webhook_received = True
            payment.save()
            return {"status": "updated", "payment_id": internal_id}

        if event == 'payment.failed':
            if payment.status == 'FAILED' and payment.webhook_received:
                return {"status": "ok", "payment_id": internal_id, "idempotent_replay": True}
            payment.status = 'FAILED'
            payment.webhook_received = True
            payment.save()
            return {"status": "updated", "payment_id": internal_id, "new_status": 'FAILED'}

        return {"status": "ignored", "event": event}

    def _extract_internal_payment_id(self, payload: dict, event: Optional[str]) -> Optional[str]:
        plink = (payload.get('payload') or {}).get('payment_link', {}).get('entity') or {}
        if event == 'payment_link.paid' and plink.get('reference_id'):
            return plink['reference_id']

        pay_entity = (payload.get('payload') or {}).get('payment', {}).get('entity') or {}
        if event in ('payment.captured', 'payment.failed'):
            notes = pay_entity.get('notes') or {}
            if isinstance(notes, dict) and notes.get('internal_payment_id'):
                return notes.get('internal_payment_id')
        return None

    def _extract_gateway_payment_id(self, payload: dict, event: Optional[str]) -> Optional[str]:
        if event == 'payment_link.paid':
            return (payload.get('payload', {}).get('payment', {}).get('entity') or {}).get('id')
        if event == 'payment.captured':
            return (payload.get('payload', {}).get('payment', {}).get('entity') or {}).get('id')
        return None
