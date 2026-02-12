"""
Notification system handler.
Handles sending notifications to users (order updates, reminders, etc.)
"""
from aiogram import Bot
from typing import Optional
from database.db_helper import db
from utils.formatters import format_order_status
from utils.constants import ORDER_STATUSES


async def send_order_notification(
    bot: Bot,
    user_id: int,
    order_id: int,
    status: str,
    message: Optional[str] = None
):
    """
    Send order status update notification to user.
    
    Args:
        bot: Bot instance
        user_id: Telegram user ID
        order_id: Order ID
        status: New order status
        message: Custom message (optional)
    """
    try:
        order = db.get_order(order_id)
        if not order:
            return
        
        status_text = format_order_status(status)
        
        if not message:
            status_messages = {
                "confirmed": "✅ Buyurtmangiz tasdiqlandi va tayyorlashga qo'yildi!",
                "preparing": "👨‍🍳 Buyurtmangiz tayyorlanmoqda...",
                "ready": "📦 Buyurtmangiz tayyor! Tez orada yetkazib beramiz.",
                "delivered": "🚚 Buyurtmangiz yetkazib berildi! Rahmat!",
                "cancelled": "❌ Buyurtmangiz bekor qilindi."
            }
            message = status_messages.get(status, f"Buyurtma holati yangilandi: {status_text}")
        
        text = f"📦 <b>Buyurtma #{order_id}</b>\n\n"
        text += f"{message}\n\n"
        text += f"Status: {status_text}"
        
        await bot.send_message(user_id, text)
        
    except Exception as e:
        print(f"Error sending notification: {e}")


async def send_reservation_reminder(
    bot: Bot,
    user_id: int,
    reservation_id: int
):
    """
    Send reservation reminder to user.
    
    Args:
        bot: Bot instance
        user_id: Telegram user ID
        reservation_id: Reservation ID
    """
    try:
        reservation = db.get_reservation(reservation_id)
        if not reservation:
            return
        
        from utils.formatters import format_date, format_time
        
        text = "📅 <b>Bron eslatmasi</b>\n\n"
        text += f"Bron #{reservation_id}\n"
        text += f"📅 Sana: {format_date(reservation.get('date', ''))}\n"
        text += f"🕐 Vaqt: {format_time(reservation.get('time', ''))}\n"
        text += f"👥 {reservation.get('party_size', 1)} kishi\n\n"
        text += "Kutib qolamiz!"
        
        await bot.send_message(user_id, text)
        
    except Exception as e:
        print(f"Error sending reservation reminder: {e}")


async def send_promotional_message(
    bot: Bot,
    user_id: int,
    title: str,
    message: str,
    promo_code: Optional[str] = None
):
    """
    Send promotional message to user.
    
    Args:
        bot: Bot instance
        user_id: Telegram user ID
        title: Message title
        message: Message content
        promo_code: Optional promo code
    """
    try:
        text = f"🎁 <b>{title}</b>\n\n"
        text += f"{message}\n"
        
        if promo_code:
            text += f"\n🎁 Promo kod: <code>{promo_code}</code>"
        
        await bot.send_message(user_id, text)
        
    except Exception as e:
        print(f"Error sending promotional message: {e}")
