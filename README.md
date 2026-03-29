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
│   └── screenshots/          # Report evidence (PNG) + short README
├── scripts/
│   └── make_submission_zip.sh # Build portal ZIP (excludes venv, .git)
├── requirements.txt
└── manage.py
```

## Report & evidence

- **`docs/screenshots/`** — PNG screenshots (API, admin, payments) to paste into your **Word/PDF** academy report. See `docs/screenshots/README.md` for a file list.
- Submit the **written report** separately on the portal if required (not stored in this repo).

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

## Git workflow (branching)

This repo follows a **GitHub Flow**–style layout (simple and common for coursework and small teams):

| Branch | Role |
|--------|------|
| **`main`** | Always **deployable / submission-ready**. Only merge tested work (via pull request or fast-forward after review). |
| **`develop`** | Optional **integration** line. Day-to-day commits can target `develop`; merge `develop` → `main` when you cut a stable milestone. |
| **`feature/*`**, **`fix/*`**, **`docs/*`** | Short-lived branches off `main` (or `develop`). Example: `feature/payment-webhook-tests`. |

**Typical loop**

```bash
git checkout main && git pull origin main
git checkout -b feature/my-change
# ... commit with clear messages: feat:, fix:, docs:, chore: ...
git push -u origin feature/my-change
# Open a Pull Request on GitHub → merge into main (or into develop first).
```

**Releases:** meaningful snapshots are tagged on `main` (e.g. `v1.0.0`) with `git tag -a v1.0.0 -m "message" && git push origin v1.0.0`.

On GitHub you can enable **branch protection** on `main` (require PR, optional checks) under **Settings → Branches**.

## Publish to GitHub

Remote: **[github.com/abbas-sd17/ecommerce-backend](https://github.com/abbas-sd17/ecommerce-backend)**.

```bash
git push -u origin main
git push -u origin develop   # optional
git push origin v1.0.0       # optional tag
```

## Portal submission (ZIP)

For uploads that ask for **source code without** virtualenv or Git metadata:

1. Use the generated archive next to this folder: **`ecommerce-backend-submission.zip`** (created in `syedbackendprojectscaler/`; excludes `venv/`, `.git/`, `__pycache__`, `*.pyc`, `db.sqlite3`).
2. Attach your **PDF/Word report** separately if the portal has a second field.
3. **Demo data (optional):** after `migrate`, run `python manage.py seed_demo_data` for admin/API samples.

Regenerate the ZIP after code changes (run from the folder that **contains** `ecommerce_backend/`):

```bash
bash ecommerce_backend/scripts/make_submission_zip.sh
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
