"""
Payment integration handler.
Provides payment processing functionality (placeholder for actual payment gateway integration).
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from utils.constants import EMOJI_CHECK, EMOJI_BACK
from utils.formatters import format_price

router = Router()


@router.callback_query(F.data == "checkout")
async def process_checkout(callback: CallbackQuery):
    """
    Process checkout and create order.
    In production, this would integrate with payment gateway (Stripe, PayPal, etc.)
    """
    user_id = callback.from_user.id
    cart = db.get_cart(user_id)
    
    if not cart.get("items"):
        await callback.answer("Savatingiz bo'sh!", show_alert=True)
        return
    
    # Check minimum order
    settings = db.get_settings()
    min_order = settings.get("min_order", 15.00)
    subtotal = cart.get("total", 0) - cart.get("discount", 0)
    
    if subtotal < min_order:
        await callback.answer(
            f"Minimal buyurtma: ${min_order:.2f}. Yana ${min_order - subtotal:.2f} qo'shing!",
            show_alert=True
        )
        return
    
    # Get user's default address
    user = db.get_user(user_id)
    addresses = user.get("addresses", [])
    default_address = next((a for a in addresses if a.get("is_default", False)), None)
    
    # Create order
    try:
        order_id = db.create_order(
            user_id=user_id,
            delivery_address=default_address,
            notes=None
        )
        
        order = db.get_order(order_id)
        
        # Format order confirmation
        text = f"{EMOJI_CHECK} <b>Buyurtma tasdiqlandi!</b>\n\n"
        text += f"📦 <b>Buyurtma raqami:</b> #{order_id}\n\n"
        text += "📞 Tez orada siz bilan bog'lanamiz, yetkazib berish tafsilotlarini tasdiqlash uchun.\n"
        text += "⏱️ Taxminiy yetkazib berish: 30-45 daqiqa\n\n"
        text += "<b>Buyurtma xulosasi:</b>\n"
        
        for item_id_str, quantity in order.get("items", {}).items():
            item = db.get_item_by_id(int(item_id_str))
            if item:
                text += f"• {item['name']} x{quantity}\n"
        
        delivery_fee = order.get("delivery_fee", 0)
        discount = order.get("discount", 0)
        total = order.get("total", 0)
        
        text += f"\n<b>Jami: {format_price(total + delivery_fee - discount)}</b>\n"
        
        if order.get("promo_code"):
            text += f"\n🎁 Promo kod: {order['promo_code']}\n"
        
        # In production, here you would:
        # 1. Process payment through payment gateway
        # 2. Send invoice to user
        # 3. Update order status based on payment result
        # 4. Send notification to admin
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📦 Buyurtmalarim", callback_data="orders")],
                [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi! Iltimos, qayta urinib ko'ring.", show_alert=True)
