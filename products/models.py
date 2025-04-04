"""
Products app models.
Lecture 1: Base Product model
Lecture 2: Abstract base model (AuditData), Category with custom PK
Lecture 3: Relationships — Category (FK), Order (M2M), Profile (O2O)
"""
from django.db import models
from django.contrib.auth.models import User


# ── Lecture 2 ──────────────────────────────────────────────────────────────
class AuditData(models.Model):
    """
    Abstract base model providing audit fields to all inheriting models.
    Taught in Lecture 2 — Model Inheritance.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ── Lecture 3 ──────────────────────────────────────────────────────────────
class Category(models.Model):
    """
    Product category. Demonstrates custom primary key (Lecture 2)
    and One-to-Many relationship with Product (Lecture 3).
    """
    name = models.CharField(max_length=100, primary_key=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ── Lecture 1 & 3 ──────────────────────────────────────────────────────────
class Product(AuditData):
    """
    Core Product model.
    Lecture 1: Basic model with serializer and API views.
    Lecture 3: FK to Category, is_available field.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    def __str__(self):
        return self.name


# ── Lecture 3 ──────────────────────────────────────────────────────────────
class Order(AuditData):
    """
    Order model. Demonstrates Many-to-Many relationship with Product (Lecture 3).
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.FloatField(default=0.0)
    order_number = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Order #{self.order_number} — {self.user.username}"


# ── Lecture 3 ──────────────────────────────────────────────────────────────
class Profile(models.Model):
    """
    User profile. Demonstrates One-to-One relationship (Lecture 3).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
