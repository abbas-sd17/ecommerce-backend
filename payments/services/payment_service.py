"""
Payment service layer.
Lecture 9 — Business logic in service layer (keep views thin).
Lecture 8 — Idempotency, webhook handling, reconciliation.
"""
import uuid
from ..models import Payment
from ..gateways.razorpay_gateway import RazorpayPaymentGateway


class PaymentService:
    """
    Handles all payment business logic.
    Taught in Lecture 9 — Service layer pattern.
    Views delegate to this service; gateways are injected via abstract class.
    """

    def __init__(self, gateway=None):
        # Dependency injection — swap gateway without changing service (Lecture 9)
        self.gateway = gateway or RazorpayPaymentGateway()

    def initiate_payment(self, order_id: str, amount: int, user) -> dict:
        """
        Initiates a new payment for an order.
        Creates a unique payment_id (idempotency key) — Lecture 8.
        Amount stored as integer (paise) — Lecture 8.

        Flow:
        1. Generate unique payment_id
        2. Save pending payment record
        3. Create payment link via gateway
        4. Return payment link to frontend
        """
        # Generate unique payment_id — the idempotency key (Lecture 8)
        payment_id = f"pay_{uuid.uuid4().hex}"

        # Save payment as PENDING (Lecture 9 — save before gateway call)
        payment = Payment.objects.create(
            payment_id=payment_id,
            order_id=order_id,
            user=user,
            amount=amount,
            status='PENDING',
        )

        # Create payment link via gateway (Lecture 9 — Abstract class)
        gateway_response = self.gateway.create_payment_link(order_id, payment_id, amount)

        # Update with gateway order ID
        payment.gateway_order_id = gateway_response.get('gateway_order_id')
        payment.save()

        return {
            "payment_id": payment_id,
            "payment_link": gateway_response.get("payment_link"),
            "amount": amount,
            "order_id": order_id,
        }

    def verify_and_confirm(self, payment_id: str, gateway_payment_id: str, signature: str) -> dict:
        """
        Verifies payment after user completes it.
        Called from webhook or callback URL (Lecture 8).
        Uses gateway signature verification to prevent fraud (Lecture 8).
        """
        try:
            payment = Payment.objects.get(payment_id=payment_id)
        except Payment.DoesNotExist:
            return {"success": False, "error": "Payment not found"}

        # Verify signature (Lecture 8 — Security)
        is_valid = self.gateway.verify_payment(
            gateway_order_id=payment.gateway_order_id,
            gateway_payment_id=gateway_payment_id,
            signature=signature
        )

        if is_valid:
            payment.status = 'SUCCESS'
            payment.gateway_payment_id = gateway_payment_id
            payment.gateway_signature = signature
            payment.save()
            return {"success": True, "payment_id": payment_id, "status": "SUCCESS"}
        else:
            payment.status = 'FAILED'
            payment.save()
            return {"success": False, "error": "Signature verification failed"}

    def handle_webhook(self, payload: dict) -> dict:
        """
        Handles Razorpay webhook events.
        Lecture 8 — Webhooks as solution to callback failures.
        Webhooks are independent of callback URLs and more reliable.
        """
        event = payload.get('event')
        payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})

        gateway_payment_id = payment_entity.get('id')
        reference_id = payment_entity.get('description', '').replace('Payment for Order ', '')

        if event == 'payment.captured':
            try:
                payment = Payment.objects.get(payment_id=reference_id)
                payment.status = 'SUCCESS'
                payment.gateway_payment_id = gateway_payment_id
                payment.webhook_received = True
                payment.save()
                return {"status": "updated", "payment_id": reference_id}
            except Payment.DoesNotExist:
                return {"status": "payment_not_found"}

        return {"status": "unhandled_event", "event": event}
