"""
Views for the payments app.
Lecture 8: Idempotency concept, webhook handling.
Lecture 9: PaymentView, WebhookView, VerifyPaymentView.
"""
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import InitiatePaymentSerializer, VerifyPaymentSerializer
from .services.payment_service import PaymentService
from .models import Payment
from .serializers import PaymentSerializer


class PaymentView(APIView):
    """
    Initiates a payment for a given order.
    Lecture 9 — PaymentView with order_id and amount.
    Lecture 8 — Optional Idempotency-Key header or body idempotency_key.

    POST /api/payments/initiate/
    Body: { "order_id": "ORD001", "amount": 50000, "idempotency_key": "optional" }
    Returns: payment_link, payment_id
    """

    def post(self, request):
        data = InitiatePaymentSerializer(data=request.data)
        if not data.is_valid():
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

        order_id = data.validated_data.get('order_id')
        amount = data.validated_data.get('amount')
        client_key = request.META.get('HTTP_IDEMPOTENCY_KEY') or data.validated_data.get(
            'idempotency_key'
        )
        if client_key:
            client_key = str(client_key).strip() or None

        service = PaymentService()
        result = service.initiate_payment(
            order_id=order_id,
            amount=amount,
            user=request.user if request.user.is_authenticated else None,
            client_idempotency_key=client_key,
        )

        if result.get('error'):
            return Response(result, status=status.HTTP_502_BAD_GATEWAY)

        code = (
            status.HTTP_200_OK
            if result.get('idempotent_replay')
            else status.HTTP_201_CREATED
        )
        return Response(result, status=code)


class VerifyPaymentView(APIView):
    """
    Verifies payment after user completes it on the gateway.
    Called from frontend after Razorpay callback (Lecture 9).

    POST /api/payments/verify/
    """

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = PaymentService()
        result = service.verify_and_confirm(**serializer.validated_data)

        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class WebhookView(APIView):
    """
    Receives Razorpay webhook events.
    Lecture 8 — Webhooks; verify X-Razorpay-Signature when RAZORPAY_WEBHOOK_SECRET is set.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw = request.body
        signature = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')

        service = PaymentService()
        if not service.gateway.verify_webhook_signature(raw, signature):
            return Response(
                {'error': 'invalid webhook signature'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = json.loads(raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return Response(
                {'error': 'invalid json body'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = service.handle_webhook(payload)
        return Response(result, status=status.HTTP_200_OK)


class PaymentListView(APIView):
    """List all payments (admin use)."""

    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentDetailView(APIView):
    """Get a single payment by payment_id."""

    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            return Response(PaymentSerializer(payment).data)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
