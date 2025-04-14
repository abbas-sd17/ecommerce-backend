"""
Decorators for the products app.
Lecture 4 — Decorators in Python and Django.
"""
from datetime import datetime
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def after_10pm_deny(func):
    """
    Decorator that denies access after 10 PM.
    Taught in Lecture 4 — Parameterized Decorators.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        now = datetime.now().hour
        if now >= 22:
            return Response(
                {"error": "Service not available after 10 PM."},
                status=status.HTTP_403_FORBIDDEN
            )
        return func(*args, **kwargs)
    return wrapper


def greet_decorator(func):
    """
    Basic decorator example from Lecture 4.
    Prints before and after function execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Hello all")
        result = func(*args, **kwargs)
        print("Bye")
        return result
    return wrapper


def log_request(func):
    """
    Logs incoming API requests — practical application of decorators.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[DECORATOR] Calling {func.__name__} at {datetime.now()}")
        result = func(*args, **kwargs)
        print(f"[DECORATOR] Done {func.__name__}")
        return result
    return wrapper
