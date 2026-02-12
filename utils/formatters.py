"""
Message formatting utilities.
Provides consistent formatting for messages displayed to users.
"""
from typing import Dict, List, Optional
from datetime import datetime
from utils.constants import (
    ORDER_STATUSES, EMOJI_CHECK, EMOJI_CROSS, EMOJI_TIME, EMOJI_LOCATION
)


def format_price(price: float, currency: str = "$") -> str:
    """
    Format price with currency symbol.
    
    Args:
        price: Price value
        currency: Currency symbol (default: $)
        
    Returns:
        Formatted price string
    """
    return f"{currency}{price:.2f}"


def format_order_status(status: str) -> str:
    """
    Format order status with emoji for better UX.
    
    Args:
        status: Order status
        
    Returns:
        Formatted status string with emoji
    """
    status_emojis = {
        "pending": "⏳",
        "confirmed": "✅",
        "preparing": "👨‍🍳",
        "ready": "📦",
        "delivered": "🚚",
        "cancelled": "❌"
    }
    
    status_names = {
        "pending": "Kutilmoqda",
        "confirmed": "Tasdiqlandi",
        "preparing": "Tayyorlanmoqda",
        "ready": "Tayyor",
        "delivered": "Yetkazib berildi",
        "cancelled": "Bekor qilindi"
    }
    
    emoji = status_emojis.get(status, "❓")
    name = status_names.get(status, status)
    
    return f"{emoji} {name}"


def format_reservation_status(status: str) -> str:
    """
    Format reservation status with emoji.
    
    Args:
        status: Reservation status
        
    Returns:
        Formatted status string
    """
    status_emojis = {
        "pending": "⏳",
        "confirmed": "✅",
        "cancelled": "❌",
        "completed": "✓"
    }
    
    status_names = {
        "pending": "Kutilmoqda",
        "confirmed": "Tasdiqlandi",
        "cancelled": "Bekor qilindi",
        "completed": "Yakunlandi"
    }
    
    emoji = status_emojis.get(status, "❓")
    name = status_names.get(status, status)
    
    return f"{emoji} {name}"


def format_rating(rating: int) -> str:
    """
    Format rating as stars.
    
    Args:
        rating: Rating value (1-5)
        
    Returns:
        Star emoji string
    """
    return "⭐" * rating + "☆" * (5 - rating)


def format_datetime(datetime_str: str) -> str:
    """
    Format datetime string for display.
    
    Args:
        datetime_str: ISO format datetime string
        
    Returns:
        Formatted date/time string
    """
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return datetime_str


def format_date(date_str: str) -> str:
    """
    Format date string for display.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        # Format in Uzbek-friendly way
        months = {
            1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel",
            5: "May", 6: "Iyun", 7: "Iyul", 8: "Avgust",
            9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
        }
        return f"{dt.day} {months.get(dt.month, '')} {dt.year}"
    except (ValueError, TypeError):
        return date_str


def format_time(time_str: str) -> str:
    """
    Format time string for display.
    
    Args:
        time_str: Time string (HH:MM)
        
    Returns:
        Formatted time string
    """
    return time_str


def format_order_summary(order: Dict) -> str:
    """
    Format order summary for display.
    
    Args:
        order: Order dictionary
        
    Returns:
        Formatted order summary string
    """
    lines = []
    lines.append(f"📦 <b>Buyurtma #{order.get('order_id', 'N/A')}</b>\n")
    lines.append(f"Status: {format_order_status(order.get('status', 'pending'))}\n")
    
    if order.get('created_at'):
        lines.append(f"{EMOJI_TIME} Sana: {format_datetime(order['created_at'])}\n")
    
    lines.append("\n<b>Mahsulotlar:</b>\n")
    
    # Items would be formatted here if available
    total = order.get('total', 0)
    discount = order.get('discount', 0)
    delivery_fee = order.get('delivery_fee', 0)
    
    lines.append(f"\n<b>Jami:</b> {format_price(total + delivery_fee - discount)}")
    
    return "\n".join(lines)


def format_cart_summary(cart: Dict, items: List[Dict]) -> str:
    """
    Format cart summary for display.
    
    Args:
        cart: Cart dictionary
        items: List of item dictionaries
        
    Returns:
        Formatted cart summary string
    """
    lines = []
    lines.append("🛒 <b>Savatingiz:</b>\n")
    
    total = 0
    for item_id, quantity in cart.get("items", {}).items():
        item = next((i for i in items if i.get("id") == int(item_id)), None)
        if item:
            item_total = item["price"] * quantity
            total += item_total
            lines.append(
                f"<b>{item['name']}</b>\n"
                f"{format_price(item['price'])} x {quantity} = {format_price(item_total)}\n"
            )
    
    if not cart.get("items"):
        return "🛒 <b>Savatingiz boʻsh</b>\n\nMenudan mahsulotlar qoʻshing!"
    
    delivery_fee = cart.get("delivery_fee", 0)
    discount = cart.get("discount", 0)
    
    lines.append(f"\n<b>Oraliq summa:</b> {format_price(total)}")
    if discount > 0:
        lines.append(f"<b>Chegirma:</b> -{format_price(discount)}")
    if delivery_fee > 0:
        lines.append(f"<b>Yetkazib berish:</b> {format_price(delivery_fee)}")
    lines.append(f"<b>Jami:</b> {format_price(total + delivery_fee - discount)}")
    
    return "\n".join(lines)
