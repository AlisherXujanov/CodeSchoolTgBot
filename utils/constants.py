"""
Constants used throughout the bot application.
Centralizing constants makes it easier to maintain and update values.
"""

# Order statuses - represents the lifecycle of an order
ORDER_STATUS_PENDING = "pending"
ORDER_STATUS_CONFIRMED = "confirmed"
ORDER_STATUS_PREPARING = "preparing"
ORDER_STATUS_READY = "ready"
ORDER_STATUS_DELIVERED = "delivered"
ORDER_STATUS_CANCELLED = "cancelled"

ORDER_STATUSES = [
    ORDER_STATUS_PENDING,
    ORDER_STATUS_CONFIRMED,
    ORDER_STATUS_PREPARING,
    ORDER_STATUS_READY,
    ORDER_STATUS_DELIVERED,
    ORDER_STATUS_CANCELLED
]

# Reservation statuses
RESERVATION_STATUS_PENDING = "pending"
RESERVATION_STATUS_CONFIRMED = "confirmed"
RESERVATION_STATUS_CANCELLED = "cancelled"
RESERVATION_STATUS_COMPLETED = "completed"

RESERVATION_STATUSES = [
    RESERVATION_STATUS_PENDING,
    RESERVATION_STATUS_CONFIRMED,
    RESERVATION_STATUS_CANCELLED,
    RESERVATION_STATUS_COMPLETED
]

# Rating scale
MIN_RATING = 1
MAX_RATING = 5

# Loyalty program
LOYALTY_POINTS_PER_DOLLAR = 1  # 1 point per dollar spent
LOYALTY_POINTS_REDEMPTION_RATE = 100  # 100 points = $1 discount

# Time limits (in minutes)
ORDER_CANCELLATION_LIMIT = 5  # Can cancel within 5 minutes
RESERVATION_REMINDER_HOURS = 24  # Send reminder 24 hours before

# Cart expiration (in hours)
CART_EXPIRATION_HOURS = 24

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 30
MAX_REQUESTS_PER_HOUR = 200

# Menu categories
MENU_CATEGORIES = ["pizza", "burgers", "drinks", "desserts", "salads", "appetizers"]

# Emoji constants for consistent UI
EMOJI_MENU = "🍽️"
EMOJI_CART = "🛒"
EMOJI_ORDERS = "📦"
EMOJI_PROFILE = "👤"
EMOJI_RESERVATIONS = "📅"
EMOJI_REVIEWS = "⭐"
EMOJI_PROMOTIONS = "🎁"
EMOJI_SETTINGS = "⚙️"
EMOJI_BACK = "⬅️"
EMOJI_CHECK = "✅"
EMOJI_CROSS = "❌"
EMOJI_PLUS = "➕"
EMOJI_MINUS = "➖"
EMOJI_DELETE = "🗑️"
EMOJI_EDIT = "✏️"
EMOJI_LOCATION = "📍"
EMOJI_PHONE = "📞"
EMOJI_TIME = "⏰"
