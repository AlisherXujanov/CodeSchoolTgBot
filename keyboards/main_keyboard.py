from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.decorators import is_admin
from config import config


def get_main_keyboard(user_id: int = None):
    """
    Create main menu keyboard with all available features.
    
    Args:
        user_id: Optional user ID to check for admin access
        
    Returns:
        InlineKeyboardMarkup with main menu options
    """
    keyboard_buttons = [
        [
            InlineKeyboardButton(text="🍽️ Menyu", callback_data="menu"),
            InlineKeyboardButton(text="🛒 Savatim", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="📦 Buyurtmalarim", callback_data="orders"),
            InlineKeyboardButton(text="👤 Profil", callback_data="profile")
        ],
        [
            InlineKeyboardButton(text="📅 Bronlar", callback_data="reservations"),
            InlineKeyboardButton(text="🎁 Promotsiyalar", callback_data="promotions")
        ],
        [
            InlineKeyboardButton(text="📞 Aloqa", callback_data="contact"),
            InlineKeyboardButton(text="📍 Joylashuv", callback_data="location")
        ],
        [
            InlineKeyboardButton(text="⏰ Ish vaqti", callback_data="hours")
        ]
    ]
    
    # Add admin button if user is admin
    if user_id and is_admin(user_id):
        keyboard_buttons.append([
            InlineKeyboardButton(text="🔧 Admin panel", callback_data="admin_panel")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)


def get_back_keyboard():
    """Create back to main menu keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Asosiy menyuga qaytish",
                              callback_data="back")]
    ])
    return keyboard
