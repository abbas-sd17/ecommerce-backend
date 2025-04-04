"""
Views for the products app.
Lecture 1: get_products, get_product — function-based API views
Lecture 2: Advanced querying with Q objects, query chaining
Lecture 3: create_product, orders — relationships
Lecture 4: Exception handling, decorators applied
Lecture 10: PageView (search + pagination), get_product with Redis caching
"""
import json
from django.db.models import Q
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer
from .exceptions import ProductOutOfStockException
from .pagination import ProductPaginator


# ── Lecture 1 — Django REST Framework & Serialization ──────────────────────

@api_view(['GET'])
def get_products(request):
    """
    Returns all products.
    Lecture 1 — Basic GET endpoint with serializer.
    """
    products = Product.objects.all()
    serialized_products = ProductSerializer(products, many=True)
    return Response(serialized_products.data)


@api_view(['GET'])
def get_product(request, id):
    """
    Returns a single product by ID with Redis caching.
    Lecture 1 — URL with path parameter, error handling.
    Lecture 10 — Redis cache for faster repeated reads.
    """
    cache_key = f"product_{id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"[CACHE] HIT for key: {cache_key}")
        return Response(cached_data)

    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"status": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serialized_product = ProductSerializer(product)
    data = serialized_product.data

    # Cache with 5-minute timeout (LRU-style)
    cache.set(cache_key, data, timeout=300)
    print(f"[CACHE] MISS — set cache for key: {cache_key}")

    return Response(data)


# ── Lecture 3 — ORM Relationships ──────────────────────────────────────────

@api_view(['POST'])
def create_product(request):
    """
    Creates a new product.
    Lecture 3 — POST endpoint, serializer validation.
    """
    try:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            # Invalidate product list cache
            cache.delete('all_products')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "Internal Server Error", "detail": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
def update_product(request, id):
    """
    Updates a product. Invalidates cache on update.
    Lecture 4 — Exception handling. Lecture 10 — Cache invalidation.
    """
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"status": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    partial = request.method == 'PATCH'
    serializer = ProductSerializer(product, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        # Invalidate cache on update
        cache.delete(f"product_{id}")
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_product(request, id):
    """Deletes a product and clears its cache entry."""
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return Response({"status": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    product.delete()
    cache.delete(f"product_{id}")
    return Response({"status": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)


# ── Lecture 2 — Advanced Querying ──────────────────────────────────────────

@api_view(['GET'])
def filter_products(request):
    """
    Filter products using Q objects and query chaining.
    Lecture 2 — Q Objects, query chaining.
    Query params: min_price, max_price, available, category
    """
    min_price = request.query_params.get('min_price', 0)
    max_price = request.query_params.get('max_price', 999999)
    available = request.query_params.get('available', None)
    category = request.query_params.get('category', None)

    # Query chaining (Lecture 2)
    qs = Product.objects.filter(
        Q(price__gte=min_price) & Q(price__lte=max_price)
    )

    if available is not None:
        qs = qs.filter(is_available=(available.lower() == 'true'))

    if category:
        qs = qs.filter(category__name=category)

    # Print SQL query (Lecture 2)
    print(qs.query)

    serializer = ProductSerializer(qs, many=True)
    return Response(serializer.data)


# ── Lecture 4 — Exception Handling & Decorators ────────────────────────────

@api_view(['GET'])
def check_stock(request, id):
    """
    Checks if a product is in stock. Raises custom exception if not.
    Lecture 4 — Custom exceptions.
    """
    try:
        product = Product.objects.get(id=id)
        if not product.is_available:
            raise ProductOutOfStockException(product.name)
        return Response({"status": "in_stock", "product": product.name})
    except Product.DoesNotExist:
        return Response({"status": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except ProductOutOfStockException as e:
        return Response({"status": "out_of_stock", "detail": str(e)},
                        status=status.HTTP_409_CONFLICT)


# ── Lecture 10 — Pagination & Search ───────────────────────────────────────

class PageView(APIView):
    """
    Search products with pagination support.
    Lecture 10 — POST-based search with pagination and ordering.
    POST body: { "query": "shirt", "page": 1, "ordering": "-created_at" }
    """
    paginator = ProductPaginator()

    def post(self, request):
        page_number = request.data.get('page', 1)
        ordering = request.data.get('ordering', '-created_at')
        query = request.data.get('query', '')

        products = Product.objects.filter(
            name__icontains=query
        ).order_by(ordering)

        # Select related to solve N+1 problem (Lecture 3)
        products = products.select_related('category')

        paginated_qs = self.paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_qs, many=True)
        return self.paginator.get_paginated_response(serializer.data)


# ── Category Views ──────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
def categories(request):
    if request.method == 'GET':
        cats = Category.objects.all()
        return Response(CategorySerializer(cats, many=True).data)
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Health Check ────────────────────────────────────────────────────────────

@api_view(['GET'])
def health_check(request):
    """
    Health endpoint. Returns 200 if service is running.
    Lecture 10 — brief mention of health API.
    """
    return Response({"status": "ok", "service": "products"})
