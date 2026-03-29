from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id',
        'client_idempotency_key',
        'order_id',
        'amount',
        'status',
        'payment_method',
        'webhook_received',
        'created_at',
    ]
    list_filter = ['status', 'payment_method', 'webhook_received']
    search_fields = ['payment_id', 'order_id', 'client_idempotency_key']
