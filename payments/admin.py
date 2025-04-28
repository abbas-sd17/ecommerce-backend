from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'order_id', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method']
    search_fields = ['payment_id', 'order_id']
