"""
Logger Middleware for the products app.
Lecture 4 & 5 — Middlewares in Django.

Middleware sits between the web server and Django views.
Every request passes through __call__ before reaching the view.
"""
import logging
import time

logger = logging.getLogger(__name__)


class LoggerMiddleware:
    """
    Logs every incoming request path and outgoing response status code.
    Taught in Lecture 5 — Middlewares and Introduction to Cloud Computing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Before view
        start_time = time.time()
        print(f"[MIDDLEWARE] ▶ Request path: {request.path} | Method: {request.method}")
        logger.info(f"Incoming request: {request.method} {request.path}")

        response = self.get_response(request)

        # After view
        duration = round((time.time() - start_time) * 1000, 2)
        print(f"[MIDDLEWARE] ◀ Response status: {response.status_code} | Duration: {duration}ms")
        logger.info(f"Response: {response.status_code} in {duration}ms")

        return response
