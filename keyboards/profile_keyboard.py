"""
Keyboard layouts for user profile management.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.constants import EMOJI_BACK, EMOJI_PROFILE, EMOJI_SETTINGS


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Create main profile keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📍 Manzillar",
                callback_data="addresses"
            ),
            InlineKeyboardButton(
                text="❤️ Sevimlilar",
                callback_data="favorites"
            )
        ],
        [
            InlineKeyboardButton(
                text="🎁 Loyalti ballari",
                callback_data="loyalty"
            ),
            InlineKeyboardButton(
                text="⚙️ Sozlamalar",
                callback_data="preferences"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI_BACK} Asosiy menyu",
                callback_data="back"
            )
        ]
    ])


def get_addresses_keyboard(addresses: list) -> InlineKeyboardMarkup:
    """Create keyboard for managing addresses."""
    buttons = []
    
    for addr in addresses:
        label = addr.get("label", "Manzil")
        is_default = addr.get("is_default", False)
        default_text = " (Asosiy)" if is_default else ""
        buttons.append([
            InlineKeyboardButton(
                text=f"📍 {label}{default_text}",
                callback_data=f"address_{addr.get('id')}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="➕ Yangi manzil qo'shish",
            callback_data="add_address"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text=f"{EMOJI_BACK} Profil",
            callback_data="profile"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
