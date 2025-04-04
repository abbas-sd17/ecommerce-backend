"""
URL patterns for the products app.
Lecture 1: basic product CRUD routes
Lecture 2: filter route
Lecture 4: stock check route
Lecture 10: search/pagination route
"""
from django.urls import path
from . import views

urlpatterns = [
    # Lecture 1
    path('', views.get_products, name='get_products'),
    path('<int:id>/', views.get_product, name='get_product'),

    # Lecture 3
    path('create/', views.create_product, name='create_product'),
    path('<int:id>/update/', views.update_product, name='update_product'),
    path('<int:id>/delete/', views.delete_product, name='delete_product'),

    # Lecture 2 — Advanced querying
    path('filter/', views.filter_products, name='filter_products'),

    # Lecture 4 — Exception handling
    path('<int:id>/stock/', views.check_stock, name='check_stock'),

    # Lecture 10 — Pagination & Search
    path('search/', views.PageView.as_view(), name='search_products'),

    # Categories
    path('categories/', views.categories, name='categories'),

    # Health
    path('health/', views.health_check, name='health_check'),
]
