"""
Custom exception classes for the restaurant bot.
Using custom exceptions makes error handling more specific and informative.
"""


class RestaurantBotError(Exception):
    """Base exception for all bot-related errors"""
    pass


class ValidationError(RestaurantBotError):
    """Raised when input validation fails"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class OrderError(RestaurantBotError):
    """Raised when order-related operations fail"""
    pass


class CartError(RestaurantBotError):
    """Raised when cart operations fail"""
    pass


class ReservationError(RestaurantBotError):
    """Raised when reservation operations fail"""
    pass


class PaymentError(RestaurantBotError):
    """Raised when payment operations fail"""
    pass


class DatabaseError(RestaurantBotError):
    """Raised when database operations fail"""
    pass


class PermissionError(RestaurantBotError):
    """Raised when user doesn't have permission for an action"""
    pass
