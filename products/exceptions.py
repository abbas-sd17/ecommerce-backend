"""
Custom exceptions for the products app.
Lecture 4 — Exception Handling in Django.
"""


class ProductOutOfStockException(Exception):
    """
    Raised when a product is requested but is out of stock.
    Taught in Lecture 4 — Custom Exceptions.
    """
    def __init__(self, product_name=None):
        self.product_name = product_name
        message = f"Product '{product_name}' is out of stock." if product_name else "Product is out of stock."
        super().__init__(message)


class InvalidOrderException(Exception):
    """Raised when an order cannot be processed due to invalid data."""
    pass
