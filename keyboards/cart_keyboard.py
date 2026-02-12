"""
Keyboard layouts for cart management.
Provides inline keyboards for cart operations like quantity adjustment and checkout.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.constants import EMOJI_PLUS, EMOJI_MINUS, EMOJI_DELETE, EMOJI_CHECK, EMOJI_BACK


def get_cart_keyboard(cart_items: dict, show_checkout: bool = True) -> InlineKeyboardMarkup:
    """
    Create keyboard for cart view with item management buttons.
    
    Args:
        cart_items: Dictionary of item_id: quantity
        show_checkout: Whether to show checkout button
        
    Returns:
        InlineKeyboardMarkup for cart
    """
    buttons = []
    
    # Add buttons for each item (quantity controls)
    for item_id, quantity in cart_items.items():
        buttons.append([
            InlineKeyboardButton(
                text=f"{EMOJI_MINUS}",
                callback_data=f"cart_dec_{item_id}"
            ),
            InlineKeyboardButton(
                text=f"{quantity}",
                callback_data=f"cart_item_{item_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI_PLUS}",
                callback_data=f"cart_inc_{item_id}"
            ),
            InlineKeyboardButton(
                text=f"{EMOJI_DELETE}",
                callback_data=f"cart_remove_{item_id}"
            )
        ])
    
    # Main action buttons
    if show_checkout and cart_items:
        buttons.append([
            InlineKeyboardButton(
                text=f"{EMOJI_CHECK} Buyurtma berish",
                callback_data="checkout"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🎁 Promo kod qo'shish",
            callback_data="apply_promo"
        ),
        InlineKeyboardButton(
            text="🗑️ Savatni tozalash",
            callback_data="clear_cart"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text=f"{EMOJI_BACK} Menyuga qaytish",
            callback_data="menu"
        ),
        InlineKeyboardButton(
            text="🏠 Asosiy menyu",
            callback_data="back"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_empty_cart_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for empty cart."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🍽️ Menyuni ko'rish",
                callback_data="menu"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"{EMOJI_BACK} Asosiy menyu",
                callback_data="back"
            )
        ]
    ])
