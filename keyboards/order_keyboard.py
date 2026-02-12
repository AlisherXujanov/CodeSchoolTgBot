"""
Keyboard layouts for order management.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.constants import EMOJI_BACK, EMOJI_ORDERS


def get_order_history_keyboard(orders: list) -> InlineKeyboardMarkup:
    """
    Create keyboard for order history.
    
    Args:
        orders: List of order dictionaries
        
    Returns:
        InlineKeyboardMarkup for order history
    """
    buttons = []
    
    # Add button for each order
    for order in orders[:10]:  # Limit to 10 most recent
        order_id = order.get("order_id")
        status = order.get("status", "pending")
        buttons.append([
            InlineKeyboardButton(
                text=f"{EMOJI_ORDERS} Buyurtma #{order_id} - {status}",
                callback_data=f"order_{order_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=f"{EMOJI_BACK} Asosiy menyu",
            callback_data="back"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_detail_keyboard(order_id: int, status: str) -> InlineKeyboardMarkup:
    """
    Create keyboard for order details.
    
    Args:
        order_id: Order ID
        status: Order status
        
    Returns:
        InlineKeyboardMarkup for order details
    """
    buttons = []
    
    # Add reorder button if order is completed
    if status in ["delivered", "completed"]:
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Qayta buyurtma berish",
                callback_data=f"reorder_{order_id}"
            )
        ])
    
    # Add cancel button if order is pending
    if status == "pending":
        buttons.append([
            InlineKeyboardButton(
                text="❌ Buyurtmani bekor qilish",
                callback_data=f"cancel_order_{order_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="⭐ Baho berish",
            callback_data=f"review_order_{order_id}"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text=f"{EMOJI_BACK} Buyurtmalar tarixi",
            callback_data="orders"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
