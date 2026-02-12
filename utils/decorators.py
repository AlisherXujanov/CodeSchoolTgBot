"""
Decorators for handlers and functions.
Provides reusable functionality like admin checks, rate limiting, etc.
"""
import time
from functools import wraps
from typing import Callable, Any, Dict, List
from aiogram.types import Message, CallbackQuery
from config import config
from utils.errors import PermissionError
from utils.constants import MAX_REQUESTS_PER_MINUTE, MAX_REQUESTS_PER_HOUR

# Simple in-memory rate limiting storage
# In production, use Redis or similar
_rate_limit_storage: Dict[int, Dict[str, List[float]]] = {}


def is_admin(user_id: int) -> bool:
    """
    Check if user is admin.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user is admin, False otherwise
    """
    return user_id == config.admin_id


def admin_only(func: Callable) -> Callable:
    """
    Decorator to restrict function access to admin users only.
    
    Usage:
        @admin_only
        async def admin_function(message: Message):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract user_id from message or callback_query
        user_id = None
        for arg in args:
            if isinstance(arg, Message):
                user_id = arg.from_user.id
                break
            elif isinstance(arg, CallbackQuery):
                user_id = arg.from_user.id
                break
        
        if not user_id or not is_admin(user_id):
            raise PermissionError("Bu funksiyaga faqat admin kirishi mumkin")
        
        return await func(*args, **kwargs)
    
    return wrapper


def rate_limit(max_per_minute: int = MAX_REQUESTS_PER_MINUTE,
               max_per_hour: int = MAX_REQUESTS_PER_HOUR) -> Callable:
    """
    Decorator to rate limit function calls per user.
    
    Args:
        max_per_minute: Maximum requests per minute
        max_per_hour: Maximum requests per hour
        
    Usage:
        @rate_limit(max_per_minute=30, max_per_hour=200)
        async def handler(message: Message):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id
            user_id = None
            for arg in args:
                if isinstance(arg, Message):
                    user_id = arg.from_user.id
                    break
                elif isinstance(arg, CallbackQuery):
                    user_id = arg.from_user.id
                    break
            
            if not user_id:
                return await func(*args, **kwargs)
            
            # Initialize user's rate limit data
            if user_id not in _rate_limit_storage:
                _rate_limit_storage[user_id] = {
                    "minute": [],
                    "hour": []
                }
            
            now = time.time()
            user_data = _rate_limit_storage[user_id]
            
            # Clean old entries
            user_data["minute"] = [
                t for t in user_data["minute"] if now - t < 60
            ]
            user_data["hour"] = [
                t for t in user_data["hour"] if now - t < 3600
            ]
            
            # Check limits
            if len(user_data["minute"]) >= max_per_minute:
                if isinstance(args[0], Message):
                    await args[0].answer(
                        "⏳ Juda ko'p so'rovlar! Iltimos, bir daqiqa kutib turing."
                    )
                elif isinstance(args[0], CallbackQuery):
                    await args[0].answer(
                        "Juda ko'p so'rovlar! Kutib turing.",
                        show_alert=True
                    )
                return
            
            if len(user_data["hour"]) >= max_per_hour:
                if isinstance(args[0], Message):
                    await args[0].answer(
                        "⏳ So'rovlar chegarasiga yetdingiz! Iltimos, bir soatdan keyin qayta urinib ko'ring."
                    )
                elif isinstance(args[0], CallbackQuery):
                    await args[0].answer(
                        "So'rovlar chegarasiga yetdingiz! Keyinroq qayta urinib ko'ring.",
                        show_alert=True
                    )
                return
            
            # Record this request
            user_data["minute"].append(now)
            user_data["hour"].append(now)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
