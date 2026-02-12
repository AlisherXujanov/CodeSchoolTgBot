"""
Keyboard layouts for admin panel.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.constants import EMOJI_BACK


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Create main admin keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"),
            InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="admin_orders")
        ],
        [
            InlineKeyboardButton(text="🍽️ Menyu boshqaruvi", callback_data="admin_menu"),
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users")
        ],
        [
            InlineKeyboardButton(text="🎁 Promo kodlar", callback_data="admin_promos"),
            InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text=f"{EMOJI_BACK} Asosiy menyu", callback_data="back")
        ]
    ])
