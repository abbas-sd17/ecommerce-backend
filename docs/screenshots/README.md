# Report screenshots

PNG captures for the Applied Software Project / academy report. Taken from the local app at `http://127.0.0.1:8000`.

| File | Description |
|------|-------------|
| `01-api-products-list.png` | DRF browsable API — `GET /api/products/` (Lecture 1). |
| `02-api-products-filter.png` | `GET /api/products/filter/?min_price=100&max_price=5000` (Lecture 2). |
| `03-django-admin-login.png` | Django admin login. |
| `04-django-admin-index.png` | Admin index — Users, Payments, Products, etc. |
| `05-api-product-stock.png` | `GET /api/products/<id>/stock/` (Lecture 4). |
| `06-api-payments-list.png` | `GET /api/payments/` — idempotency & webhook fields (Lectures 8–9). |
| `07-api-products-health.png` | `GET /api/products/health/` — health check (Lecture 10). |
| `08-api-products-search-get-405.png` | `GET /api/products/search/` — **405** (search is **POST**-only by design). |
| `09-api-products-search-post-200.png` | `POST /api/products/search/` — paginated search (Lecture 10). |

**GET `/api/products/<id>/`:** requires Redis **or** `IGNORE_EXCEPTIONS: True` in cache settings so the view still works when Redis is not running.

A merged Word document including these figures is at `../Project_Report_Template_with_Screenshots.docx` (generated from the Scaler template + this appendix).
