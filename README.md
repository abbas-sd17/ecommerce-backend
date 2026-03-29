# E-Commerce Backend — Django REST Framework

**Scaler Neovarsity | Backend Specialization | Applied Software Project**
**Student:** Syed Abbas Raza | **Email:** abbas.sd17@gmail.com

---

## Project Overview

A production-ready e-commerce backend built lecture-by-lecture during the Scaler Neovarsity Backend Specialization. Features include product management, advanced querying, middleware, caching with Redis, and Razorpay payment integration.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Django 4.2 | Web framework |
| Django REST Framework | API layer |
| SQLite (dev) / MySQL (prod) | Database |
| Redis | Caching layer |
| Razorpay | Payment gateway |
| Gunicorn | WSGI server |
| AWS EC2 + RDS + EBS | Deployment |

## Project Structure

```
ecommerce_backend/
├── ecommerce_backend/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── products/                 # Product management app
│   ├── models.py             # Product, Category, Order, Profile
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API views (CRUD + search + cache)
│   ├── urls.py               # URL routing
│   ├── decorators.py         # Custom decorators (Lecture 4)
│   ├── exceptions.py         # Custom exceptions (Lecture 4)
│   ├── pagination.py         # Custom paginator (Lecture 10)
│   └── middlewares/
│       └── logmiddleware.py  # Logger middleware (Lecture 5)
├── payments/                 # Payment service app
│   ├── models.py             # Payment model with idempotency
│   ├── serializers.py
│   ├── views.py              # PaymentView, WebhookView
│   ├── urls.py
│   ├── gateways/
│   │   ├── base.py           # Abstract PaymentGateway (Lecture 9)
│   │   └── razorpay_gateway.py
│   └── services/
│       └── payment_service.py
├── .ebextensions/
│   └── django.config         # AWS EBS config (Lecture 8)
├── docs/
│   ├── screenshots/          # Report PNGs + README
│   ├── Syed_Abbas_Raza_Project_Report_With_Screenshots.docx
│   └── Project_Report_Template_with_Screenshots.docx  # optional (--source template)
├── requirements.txt
└── manage.py
```

## Report documentation

- **`docs/screenshots/`** — PNG screenshots for the Applied Software Project report (DRF API, Django admin, payments).
- **Your Word report** — keep **`Syed_Abbas_Raza_Project_Report.docx`** in the folder **above** this repo (`syedbackendprojectscaler/`, next to the Scaler template).
- **`docs/Syed_Abbas_Raza_Project_Report_With_Screenshots.docx`** — your report plus an **Appendix** with all figures. Regenerate after editing the source `.docx` or replacing PNGs:

```bash
pip install python-docx
python docs/append_screenshots_to_report.py
```

Also creates **`../Syed_Abbas_Raza_Project_Report_With_Screenshots.docx`** beside your source file. Empty template only: `python docs/append_screenshots_to_report.py --source template` → `docs/Project_Report_Template_with_Screenshots.docx`.

## API Endpoints

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List all products |
| GET | `/api/products/<id>/` | Get product (cached) |
| POST | `/api/products/create/` | Create product |
| PUT | `/api/products/<id>/update/` | Update product |
| DELETE | `/api/products/<id>/delete/` | Delete product |
| GET | `/api/products/filter/` | Filter with Q objects |
| GET | `/api/products/<id>/stock/` | Check stock |
| POST | `/api/products/search/` | Search + paginate |
| GET | `/api/products/categories/` | List categories |
| GET | `/api/products/health/` | Health check |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/payments/initiate/` | Initiate payment |
| POST | `/api/payments/verify/` | Verify payment |
| POST | `/api/payments/webhook/` | Razorpay webhook |
| GET | `/api/payments/` | List payments |

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/abbas-sd17/ecommerce-backend.git
cd ecommerce-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create superuser (optional)
python manage.py createsuperuser

# 6. Start development server
python manage.py runserver

# Server runs at: http://127.0.0.1:8000/
# Admin panel: http://127.0.0.1:8000/admin/
```

## Environment Variables

```env
RAZORPAY_ID=rzp_test_your_key
RAZORPAY_SECRET=your_secret
# Public HTTPS URL in production (Razorpay cannot call localhost)
RAZORPAY_CALLBACK_URL=https://your-domain.com/api/payments/verify/
# Dashboard → Webhooks → your endpoint → signing secret (validates X-Razorpay-Signature)
RAZORPAY_WEBHOOK_SECRET=whsec_...
```

**Idempotency (Lecture 8):** send the same `Idempotency-Key` header (or `idempotency_key` in the JSON body) on `POST /api/payments/initiate/` to safely retry; the API returns the existing payment and link without double-charging.

## Lecture-to-Feature Mapping

| Lecture | Feature Added |
|---------|--------------|
| 1 | Django REST Framework setup, ProductSerializer, GET endpoints |
| 2 | Abstract models, Q objects, query chaining |
| 3 | Relationships (FK, M2M, O2O), create_product, select_related |
| 4 | Custom exceptions, decorators |
| 5 | Logger middleware |
| 6 | AWS RDS setup, MySQL config |
| 7 | WSGI/Gunicorn, VPC, security groups, Route 53, Load Balancer |
| 8 | Idempotency, Payment model, webhooks, EBS deployment |
| 9 | Razorpay integration, abstract PaymentGateway, service layer |
| 10 | Pagination, Redis caching, search API |

## Deployment (AWS)

See [Deployment Flow](#) in the project report for full AWS architecture details.

```bash
# Deploy to Elastic Beanstalk
eb init -p python-3.11 ecommerce-backend
eb create ecommerce-production
eb deploy
```
