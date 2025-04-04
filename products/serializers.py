"""
Serializers for the products app.
Lecture 1: ProductSerializer — ModelSerializer covering all fields.
Lecture 3: CategorySerializer, OrderSerializer.
"""
from rest_framework import serializers
from .models import Product, Category, Order


# ── Lecture 1 ──────────────────────────────────────────────────────────────
class ProductSerializer(serializers.ModelSerializer):
    """
    ModelSerializer for Product.
    Taught in Lecture 1 — Django REST Framework and Serialization.
    """
    class Meta:
        model = Product
        fields = '__all__'


# ── Lecture 3 ──────────────────────────────────────────────────────────────
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
