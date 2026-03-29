@echo off
REM ============================================================
REM E-Commerce Backend — Setup & Run Script (Windows)
REM Scaler Neovarsity | Syed Abbas Raza
REM ============================================================
REM Usage:
REM   Double-click setup.bat       → full setup + start server
REM   setup.bat --run              → skip setup, just start server
REM   setup.bat --reset            → wipe DB and start fresh
REM ============================================================

SETLOCAL ENABLEDELAYEDEXPANSION
SET "GREEN=[92m"
SET "YELLOW=[93m"
SET "RED=[91m"
SET "BLUE=[94m"
SET "NC=[0m"

echo.
echo  ==================================================
echo    E-Commerce Backend - Django REST Framework
echo    Scaler Neovarsity ^| Syed Abbas Raza
echo  ==================================================
echo.

REM ── Parse arguments ──────────────────────────────────────
SET RUN_ONLY=false
SET RESET=false

IF "%1"=="--run"   SET RUN_ONLY=true
IF "%1"=="--reset" SET RESET=true
IF "%1"=="--help" (
  echo Usage: setup.bat [--run ^| --reset ^| --help]
  echo   no args   Full setup + start server
  echo   --run     Skip setup, just start server
  echo   --reset   Delete DB and start fresh
  EXIT /B 0
)

REM ── Check Python ──────────────────────────────────────────
python --version >NUL 2>&1
IF ERRORLEVEL 1 (
  echo [ERROR] Python not found. Install Python 3.10+ from python.org
  PAUSE
  EXIT /B 1
)
echo [OK] Python found
FOR /F "tokens=*" %%i IN ('python --version') DO echo     %%i

REM ── Reset mode ────────────────────────────────────────────
IF "%RESET%"=="true" (
  echo [!] Resetting - removing db.sqlite3...
  IF EXIST db.sqlite3 DEL db.sqlite3
  echo [OK] Database wiped.
)

REM ── Run only mode ─────────────────────────────────────────
IF "%RUN_ONLY%"=="true" (
  echo [>] Starting server only...
  python manage.py runserver 0.0.0.0:8000
  EXIT /B 0
)

REM ── Step 1: Virtual environment ───────────────────────────
echo.
echo  -- Step 1: Virtual Environment --
IF NOT EXIST venv (
  echo [..] Creating virtual environment...
  python -m venv venv
  echo [OK] Virtual environment created.
) ELSE (
  echo [OK] Virtual environment already exists.
)

CALL venv\Scripts\activate.bat
echo [OK] Virtual environment activated.

REM ── Step 2: Install dependencies ─────────────────────────
echo.
echo  -- Step 2: Installing Dependencies --
python -m pip install --upgrade pip --quiet

python -m pip install "Django==4.2.7" --quiet && echo [OK] Django installed
python -m pip install "djangorestframework==3.14.0" --quiet && echo [OK] DRF installed
python -m pip install "gunicorn==21.2.0" --quiet && echo [OK] Gunicorn installed
python -m pip install "python-decouple==3.8" --quiet && echo [OK] python-decouple installed
python -m pip install "django-redis==5.4.0" --quiet && echo [OK] django-redis installed || echo [!] django-redis skipped
python -m pip install "redis==5.0.1" --quiet && echo [OK] redis installed || echo [!] redis skipped
python -m pip install "razorpay==1.4.1" --quiet && echo [OK] razorpay installed || echo [!] razorpay skipped (mock mode)

REM ── Step 3: .env file ─────────────────────────────────────
echo.
echo  -- Step 3: Environment File --
IF NOT EXIST .env (
  (
    echo SECRET_KEY=django-insecure-scaler-neovarsity-backend-key-replace-in-production
    echo DEBUG=True
    echo ALLOWED_HOSTS=*
    echo RAZORPAY_ID=rzp_test_your_key_id
    echo RAZORPAY_SECRET=your_razorpay_secret
    echo RAZORPAY_CALLBACK_URL=http://127.0.0.1:8000/api/payments/verify/
  ) > .env
  echo [OK] .env file created with defaults.
  echo [!] Edit .env to add real Razorpay keys.
) ELSE (
  echo [OK] .env already exists.
)

REM ── Step 4: Migrate ───────────────────────────────────────
echo.
echo  -- Step 4: Database Migrations --
python manage.py migrate
echo [OK] Migrations complete.

REM ── Step 5: Superuser ─────────────────────────────────────
echo.
echo  -- Step 5: Admin User --
python -c "import os,django; os.environ.setdefault('DJANGO_SETTINGS_MODULE','ecommerce_backend.settings'); django.setup(); from django.contrib.auth.models import User; User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin','admin@example.com','admin123') or print('Created admin user: admin / admin123')" 2>NUL
echo [OK] Admin user ready.

REM ── Step 6: Sample data ───────────────────────────────────
echo.
echo  -- Step 6: Sample Data --
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
django.setup()
from products.models import Category, Product
if Product.objects.count() == 0:
    c1,_=Category.objects.get_or_create(name='Electronics',defaults={'description':'Gadgets'})
    c2,_=Category.objects.get_or_create(name='Clothing',defaults={'description':'Apparel'})
    c3,_=Category.objects.get_or_create(name='Books',defaults={'description':'Books'})
    for p in [
        {'name':'Wireless Headphones','price':1999.99,'category':c1,'is_available':True,'description':'Premium headphones'},
        {'name':'Mechanical Keyboard','price':3499.00,'category':c1,'is_available':True,'description':'RGB keyboard'},
        {'name':'Classic White Shirt','price':599.00,'category':c2,'is_available':True,'description':'Cotton shirt'},
        {'name':'Denim Jacket','price':1299.00,'category':c2,'is_available':False,'description':'Out of stock'},
        {'name':'Clean Code (Book)','price':499.00,'category':c3,'is_available':True,'description':'Robert C. Martin'},
        {'name':'Django for Professionals','price':349.00,'category':c3,'is_available':True,'description':'Advanced Django'},
    ]:
        Product.objects.get_or_create(name=p['name'],defaults=p)
    print('Created 6 sample products.')
else:
    print(f'Already have {Product.objects.count()} products.')
"

REM ── Summary ───────────────────────────────────────────────
echo.
echo  ==================================================
echo    Setup Complete! Starting server...
echo  ==================================================
echo.
echo    Admin Panel:  http://127.0.0.1:8000/admin/
echo    Admin Login:  admin / admin123
echo.
echo    API:          http://127.0.0.1:8000/api/products/
echo    Health:       http://127.0.0.1:8000/health/
echo.
echo    Stop server:  Ctrl + C
echo  ==================================================
echo.

REM ── Start server ──────────────────────────────────────────
python manage.py runserver 0.0.0.0:8000

PAUSE
