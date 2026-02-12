"""
Data models for the restaurant bot.
These dataclasses represent the structure of our data entities.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class UserProfile:
    """User profile information"""
    user_id: int
    first_name: str = ""
    last_name: str = ""
    username: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: str = ""
    loyalty_points: int = 0
    total_orders: int = 0
    preferences: Dict = field(default_factory=dict)  # Dietary restrictions, allergies, etc.


@dataclass
class DeliveryAddress:
    """Delivery address for a user"""
    id: int
    label: str  # Home, Work, etc.
    street: str
    city: str
    postal_code: str
    notes: Optional[str] = None
    is_default: bool = False


@dataclass
class Order:
    """Order information"""
    order_id: int
    user_id: int
    items: Dict[str, int]  # item_id: quantity
    total: float
    status: str  # pending, confirmed, preparing, ready, delivered, cancelled
    delivery_address: Optional[Dict] = None
    promo_code: Optional[str] = None
    discount: float = 0.0
    delivery_fee: float = 0.0
    created_at: str = ""
    updated_at: str = ""
    notes: Optional[str] = None


@dataclass
class Reservation:
    """Table reservation information"""
    reservation_id: int
    user_id: int
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    party_size: int
    status: str  # pending, confirmed, cancelled, completed
    special_requests: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Review:
    """Review/rating for an order or item"""
    review_id: int
    user_id: int
    order_id: Optional[int] = None
    item_id: Optional[int] = None
    rating: int  # 1-5 stars
    comment: Optional[str] = None
    created_at: str = ""


@dataclass
class PromoCode:
    """Promotional code information"""
    code: str
    discount_type: str  # percentage or fixed
    discount_value: float
    min_order: float = 0.0
    max_uses: Optional[int] = None
    used_count: int = 0
    valid_from: str = ""
    valid_until: str = ""
    is_active: bool = True
