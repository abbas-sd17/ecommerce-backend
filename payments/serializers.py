"""
Serializers for the payments app.
Lecture 9 — PaymentSerializer, InitiatePaymentSerializer.
"""
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_id', 'status', 'gateway_payment_id',
                            'gateway_order_id', 'gateway_signature', 'webhook_received']


class InitiatePaymentSerializer(serializers.Serializer):
    """
    Validates payment initiation request.
    Taught in Lecture 9 — PaymentSerializer with order_number and amount.
    """
    order_id = serializers.CharField(max_length=100)
    amount = serializers.IntegerField(min_value=1)  # In paise (Lecture 8 — use integers)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0.")
        return value


class VerifyPaymentSerializer(serializers.Serializer):
    """Validates payment verification callback data."""
    payment_id = serializers.CharField()
    gateway_payment_id = serializers.CharField()
    signature = serializers.CharField()


class WebhookSerializer(serializers.Serializer):
    """Accepts raw Razorpay webhook payload."""
    event = serializers.CharField()
    payload = serializers.DictField()
