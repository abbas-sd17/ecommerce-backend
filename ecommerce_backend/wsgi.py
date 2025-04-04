"""
WSGI config for ecommerce_backend project.
Lecture 7 — WSGI acts as translator between web server (Gunicorn) and Django app.
Production: Browser → EC2 → Gunicorn → WSGI → Django
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')
application = get_wsgi_application()
