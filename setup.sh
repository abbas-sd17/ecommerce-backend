#!/bin/bash
# ============================================================
# E-Commerce Backend — Setup & Run Script
# Scaler Neovarsity | Syed Abbas Raza
# ============================================================
# Usage:
#   chmod +x setup.sh
#   ./setup.sh          → full setup + start server
#   ./setup.sh --run    → skip setup, just start server
#   ./setup.sh --reset  → wipe DB and start fresh
# ============================================================

set -e  # Exit immediately on any error

# ── Colors ────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log()    { echo -e "${GREEN}[✔] $1${NC}"; }
warn()   { echo -e "${YELLOW}[!] $1${NC}"; }
error()  { echo -e "${RED}[✘] $1${NC}"; exit 1; }
header() { echo -e "\n${BLUE}══════════════════════════════════════${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}══════════════════════════════════════${NC}"; }

# ── Banner ────────────────────────────────────────────────
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   E-Commerce Backend — Django REST Framework ║${NC}"
echo -e "${BLUE}║   Scaler Neovarsity | Syed Abbas Raza        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"
echo ""

# ── Parse arguments ───────────────────────────────────────
RUN_ONLY=false
RESET=false

for arg in "$@"; do
  case $arg in
    --run)   RUN_ONLY=true ;;
    --reset) RESET=true ;;
    --help)
      echo "Usage: ./setup.sh [--run | --reset | --help]"
      echo "  (no args)  Full setup + start server"
      echo "  --run      Skip setup, just start server"
      echo "  --reset    Delete DB and start fresh"
      exit 0
      ;;
  esac
done

# ── Check Python ──────────────────────────────────────────
header "Checking Python"
if ! command -v python3 &> /dev/null; then
  error "Python 3 not found. Please install Python 3.10 or higher."
fi

PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
log "Python found: $PY_VERSION"

# ── Reset mode ────────────────────────────────────────────
if [ "$RESET" = true ]; then
  header "Resetting Project"
  warn "Removing db.sqlite3..."
  rm -f db.sqlite3
  log "Database wiped."
fi

# ── Skip setup if --run ───────────────────────────────────
if [ "$RUN_ONLY" = true ]; then
  header "Starting Server (skip setup)"
  python3 manage.py runserver 0.0.0.0:8000
  exit 0
fi

# ══════════════════════════════════════════════════════════
# FULL SETUP
# ══════════════════════════════════════════════════════════

# ── Step 1: Virtual environment ───────────────────────────
header "Step 1 — Virtual Environment"

if [ ! -d "venv" ]; then
  log "Creating virtual environment..."
  python3 -m venv venv
  log "Virtual environment created at ./venv"
else
  log "Virtual environment already exists."
fi

# Activate venv
source venv/bin/activate
log "Virtual environment activated."

# ── Step 2: Install dependencies ─────────────────────────
header "Step 2 — Installing Dependencies"
log "Installing from requirements.txt..."

# Core packages (always available)
pip install --upgrade pip --quiet

# Install one by one so partial installs still work
pip install "Django==4.2.7" --quiet && log "Django installed" || warn "Django install failed"
pip install "djangorestframework==3.14.0" --quiet && log "DRF installed" || warn "DRF install failed"
pip install "gunicorn==21.2.0" --quiet && log "Gunicorn installed" || warn "Gunicorn install failed"
pip install "python-decouple==3.8" --quiet && log "python-decouple installed" || warn "python-decouple install failed"

# Optional packages (skip gracefully if unavailable)
pip install "django-redis==5.4.0" --quiet && log "django-redis installed" || warn "django-redis not installed (Redis caching disabled)"
pip install "redis==5.0.1" --quiet && log "redis installed" || warn "redis not installed"
pip install "razorpay==1.4.1" --quiet && log "razorpay installed" || warn "razorpay not installed (payment gateway in mock mode)"

echo ""
log "All dependencies processed."

# ── Step 3: Environment file ──────────────────────────────
header "Step 3 — Environment Configuration"

if [ ! -f ".env" ]; then
  cat > .env << 'ENVEOF'
# Django settings
SECRET_KEY=django-insecure-scaler-neovarsity-backend-key-replace-in-production
DEBUG=True
ALLOWED_HOSTS=*

# Razorpay credentials (replace with real keys for payment testing)
RAZORPAY_ID=rzp_test_your_key_id
RAZORPAY_SECRET=your_razorpay_secret

# Razorpay callback (must be public URL in production, not localhost)
RAZORPAY_CALLBACK_URL=http://127.0.0.1:8000/api/payments/verify/
ENVEOF
  log ".env file created with default settings."
  warn "Edit .env to add real Razorpay keys if testing payments."
else
  log ".env file already exists — skipping."
fi

# ── Step 4: Patch settings.py to use .env ─────────────────
header "Step 4 — Settings Check"

# Check if decouple is being used; if not, settings.py already has hardcoded values
python3 -c "import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','ecommerce_backend.settings'); django.setup(); print('Settings OK')" 2>/dev/null && log "Django settings loaded successfully." || warn "Settings check failed — continuing anyway."

# ── Step 5: Run migrations ────────────────────────────────
header "Step 5 — Database Migrations"

python3 manage.py migrate --run-syncdb 2>/dev/null || python3 manage.py migrate
log "Migrations complete. Database ready."

# ── Step 6: Create superuser ──────────────────────────────
header "Step 6 — Admin User"

# Check if superuser already exists
SUPERUSER_EXISTS=$(python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()
from django.contrib.auth.models import User
print('yes' if User.objects.filter(is_superuser=True).exists() else 'no')
" 2>/dev/null)

if [ "$SUPERUSER_EXISTS" = "no" ]; then
  log "Creating default admin user..."
  python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
print('Superuser created: admin / admin123')
"
  warn "Default admin credentials: username=admin, password=admin123"
  warn "Change this password before deploying to production!"
else
  log "Admin user already exists."
fi

# ── Step 7: Load sample data ──────────────────────────────
header "Step 7 — Sample Data"

python3 -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()
from products.models import Category, Product
from django.contrib.auth.models import User

if Product.objects.count() == 0:
    # Create categories
    cat1, _ = Category.objects.get_or_create(name='Electronics', defaults={'description': 'Electronic gadgets and devices'})
    cat2, _ = Category.objects.get_or_create(name='Clothing', defaults={'description': 'Apparel and fashion'})
    cat3, _ = Category.objects.get_or_create(name='Books', defaults={'description': 'Books and stationery'})

    # Create products
    products = [
        {'name': 'Wireless Headphones', 'price': 1999.99, 'category': cat1, 'is_available': True, 'description': 'Premium noise-cancelling headphones'},
        {'name': 'Mechanical Keyboard', 'price': 3499.00, 'category': cat1, 'is_available': True, 'description': 'RGB mechanical gaming keyboard'},
        {'name': 'Classic White Shirt', 'price': 599.00, 'category': cat2, 'is_available': True, 'description': 'Cotton formal shirt'},
        {'name': 'Denim Jacket', 'price': 1299.00, 'category': cat2, 'is_available': False, 'description': 'Slim fit denim jacket - out of stock'},
        {'name': 'Clean Code (Book)', 'price': 499.00, 'category': cat3, 'is_available': True, 'description': 'By Robert C. Martin'},
        {'name': 'Django for Professionals', 'price': 349.00, 'category': cat3, 'is_available': True, 'description': 'Advanced Django development'},
    ]

    for p in products:
        Product.objects.get_or_create(name=p['name'], defaults=p)

    print(f'Created {len(products)} sample products across 3 categories.')
else:
    print(f'Sample data already exists ({Product.objects.count()} products).')
"

# ── Step 8: Check Redis ────────────────────────────────────
header "Step 8 — Redis Check"

if command -v redis-cli &> /dev/null; then
  if redis-cli ping &> /dev/null; then
    log "Redis is running. Caching will be active."
  else
    warn "Redis is installed but not running. Start it with: redis-server"
    warn "Caching will fall back gracefully (no errors, just no cache)."
  fi
else
  warn "Redis not found. Caching will be disabled."
  warn "To enable: install Redis (brew install redis / apt install redis-server)"
fi

# ── Ready summary ─────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Setup Complete! Ready to run.              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BLUE}Admin Panel:${NC}    http://127.0.0.1:8000/admin/"
echo -e "  ${BLUE}Admin Login:${NC}    admin / admin123"
echo ""
echo -e "  ${BLUE}API Endpoints:${NC}"
echo -e "    GET   http://127.0.0.1:8000/api/products/"
echo -e "    GET   http://127.0.0.1:8000/api/products/1/"
echo -e "    POST  http://127.0.0.1:8000/api/products/search/"
echo -e "    GET   http://127.0.0.1:8000/api/products/filter/?min_price=100"
echo -e "    POST  http://127.0.0.1:8000/api/payments/initiate/"
echo -e "    GET   http://127.0.0.1:8000/health/"
echo ""
echo -e "  ${BLUE}Stop server:${NC}    Ctrl + C"
echo ""

# ── Step 9: Start server ──────────────────────────────────
header "Step 9 — Starting Development Server"
log "Server starting at http://127.0.0.1:8000/"
echo ""

python3 manage.py runserver 0.0.0.0:8000
