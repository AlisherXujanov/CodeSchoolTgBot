"""
Input validation functions.
Validates user inputs before processing to prevent errors and ensure data integrity.
"""
import re
from typing import Optional
from datetime import datetime
from utils.errors import ValidationError
from utils.constants import MIN_RATING, MAX_RATING


def validate_phone(phone: str) -> str:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        Cleaned phone number
        
    Raises:
        ValidationError: If phone format is invalid
    """
    if not phone:
        raise ValidationError("Telefon raqami kiritilmadi", "phone")
    
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    # Check if it's a reasonable length (7-15 digits)
    if len(cleaned) < 7 or len(cleaned) > 15:
        raise ValidationError("Telefon raqami noto'g'ri formatda", "phone")
    
    return cleaned


def validate_email(email: str) -> str:
    """
    Validate email format.
    
    Args:
        email: Email string
        
    Returns:
        Lowercased email
        
    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("Email kiritilmadi", "email")
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Email noto'g'ri formatda", "email")
    
    return email.lower()


def validate_rating(rating: int) -> int:
    """
    Validate rating value (1-5).
    
    Args:
        rating: Rating value
        
    Returns:
        Validated rating
        
    Raises:
        ValidationError: If rating is out of range
    """
    if not isinstance(rating, int):
        try:
            rating = int(rating)
        except (ValueError, TypeError):
            raise ValidationError("Reyting raqam bo'lishi kerak", "rating")
    
    if rating < MIN_RATING or rating > MAX_RATING:
        raise ValidationError(
            f"Reyting {MIN_RATING} dan {MAX_RATING} gacha bo'lishi kerak",
            "rating"
        )
    
    return rating


def validate_date(date_str: str) -> str:
    """
    Validate date string format (YYYY-MM-DD).
    
    Args:
        date_str: Date string
        
    Returns:
        Validated date string
        
    Raises:
        ValidationError: If date format is invalid
    """
    if not date_str:
        raise ValidationError("Sana kiritilmadi", "date")
    
    try:
        # Try to parse the date
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise ValidationError("Sana noto'g'ri formatda (YYYY-MM-DD bo'lishi kerak)", "date")


def validate_time(time_str: str) -> str:
    """
    Validate time string format (HH:MM).
    
    Args:
        time_str: Time string
        
    Returns:
        Validated time string
        
    Raises:
        ValidationError: If time format is invalid
    """
    if not time_str:
        raise ValidationError("Vaqt kiritilmadi", "time")
    
    try:
        # Try to parse the time
        datetime.strptime(time_str, "%H:%M")
        return time_str
    except ValueError:
        raise ValidationError("Vaqt noto'g'ri formatda (HH:MM bo'lishi kerak)", "time")


def validate_quantity(quantity: int) -> int:
    """
    Validate item quantity (must be positive).
    
    Args:
        quantity: Quantity value
        
    Returns:
        Validated quantity
        
    Raises:
        ValidationError: If quantity is invalid
    """
    if not isinstance(quantity, int):
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValidationError("Miqdor raqam bo'lishi kerak", "quantity")
    
    if quantity < 1:
        raise ValidationError("Miqdor 1 dan katta bo'lishi kerak", "quantity")
    
    if quantity > 100:
        raise ValidationError("Miqdor 100 dan oshmasligi kerak", "quantity")
    
    return quantity


def validate_party_size(size: int) -> int:
    """
    Validate party size for reservations.
    
    Args:
        size: Party size
        
    Returns:
        Validated party size
        
    Raises:
        ValidationError: If party size is invalid
    """
    if not isinstance(size, int):
        try:
            size = int(size)
        except (ValueError, TypeError):
            raise ValidationError("Mehmonlar soni raqam bo'lishi kerak", "party_size")
    
    if size < 1:
        raise ValidationError("Mehmonlar soni kamida 1 bo'lishi kerak", "party_size")
    
    if size > 20:
        raise ValidationError("Mehmonlar soni 20 dan oshmasligi kerak", "party_size")
    
    return size


def validate_price(price: float) -> float:
    """
    Validate price value (must be non-negative).
    
    Args:
        price: Price value
        
    Returns:
        Validated price
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        price = float(price)
    except (ValueError, TypeError):
        raise ValidationError("Narx raqam bo'lishi kerak", "price")
    
    if price < 0:
        raise ValidationError("Narx manfiy bo'lishi mumkin emas", "price")
    
    return round(price, 2)
