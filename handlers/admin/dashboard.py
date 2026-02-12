"""
Admin dashboard handler.
Shows statistics and overview of the restaurant bot.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from keyboards.admin_keyboard import get_admin_keyboard
from utils.decorators import admin_only, is_admin
from utils.constants import EMOJI_BACK

router = Router()


@router.message(Command("admin"))
@admin_only
async def admin_panel(message: Message):
    """
    Show admin panel.
    Only accessible to admin users.
    """
    await message.answer(
        "🔧 <b>Admin panel</b>\n\n"
        "Nimani boshqarmoqchisiz?",
        reply_markup=get_admin_keyboard()
    )


@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    """Show admin panel from callback."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 <b>Admin panel</b>\n\n"
        "Nimani boshqarmoqchisiz?",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    """
    Display bot statistics.
    Shows user count, orders, revenue, and other metrics.
    """
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    # Calculate statistics
    users = db.data.get("users", {})
    orders = db.data.get("orders", {})
    reservations = db.data.get("reservations", {})
    carts = db.data.get("carts", {})
    
    total_users = len(users)
    total_orders = len(orders)
    active_carts = sum(1 for cart in carts.values() if cart.get("items"))
    total_reservations = len(reservations)
    
    # Calculate revenue
    total_revenue = 0
    completed_orders = 0
    for order in orders.values():
        if order.get("status") in ["delivered", "completed"]:
            total_revenue += order.get("total", 0) + order.get("delivery_fee", 0) - order.get("discount", 0)
            completed_orders += 1
    
    # Menu statistics
    menu_items = 0
    for category in db.data.get("menu", {}).values():
        menu_items += len(category)
    
    # Active promo codes
    promo_codes = db.data.get("promo_codes", {})
    active_promos = sum(1 for p in promo_codes.values() if p.get("is_active", True))
    
    text = "📊 <b>Bot statistikasi</b>\n\n"
    text += f"👥 <b>Jami foydalanuvchilar:</b> {total_users}\n"
    text += f"📦 <b>Jami buyurtmalar:</b> {total_orders}\n"
    text += f"✅ <b>Yakunlangan buyurtmalar:</b> {completed_orders}\n"
    text += f"🛒 <b>Faol savatlar:</b> {active_carts}\n"
    text += f"📅 <b>Bronlar:</b> {total_reservations}\n"
    text += f"🍽️ <b>Menyu mahsulotlari:</b> {menu_items}\n"
    text += f"🎁 <b>Faol promo kodlar:</b> {active_promos}\n\n"
    text += f"💰 <b>Jami daromad:</b> ${total_revenue:.2f}\n"
    
    if completed_orders > 0:
        avg_order = total_revenue / completed_orders
        text += f"📈 <b>O'rtacha buyurtma:</b> ${avg_order:.2f}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Admin panel", callback_data="admin_panel")]
        ])
    )
    await callback.answer()
