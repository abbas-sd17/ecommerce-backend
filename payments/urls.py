"""URL patterns for the payments app."""
from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.PaymentView.as_view(), name='initiate_payment'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify_payment'),
    path('webhook/', views.WebhookView.as_view(), name='payment_webhook'),
    path('', views.PaymentListView.as_view(), name='payment_list'),
    path('<str:payment_id>/', views.PaymentDetailView.as_view(), name='payment_detail'),
]
