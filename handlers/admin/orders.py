"""
Admin order management handler.
Allows admins to view, update status, and manage orders.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from utils.decorators import is_admin
from utils.formatters import format_order_status, format_price, format_datetime
from utils.constants import ORDER_STATUSES, EMOJI_BACK

router = Router()


@router.callback_query(F.data == "admin_orders")
async def show_admin_orders(callback: CallbackQuery):
    """Display all orders for admin management."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    orders = list(db.data.get("orders", {}).values())
    
    # Sort by created_at descending
    orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Filter by status
    pending_orders = [o for o in orders if o.get("status") == "pending"]
    active_orders = [o for o in orders if o.get("status") in ["confirmed", "preparing", "ready"]]
    
    text = "📦 <b>Buyurtmalar boshqaruvi</b>\n\n"
    text += f"⏳ Kutilayotgan: {len(pending_orders)}\n"
    text += f"🔄 Faol: {len(active_orders)}\n"
    text += f"📦 Jami: {len(orders)}\n\n"
    
    # Show recent orders
    text += "<b>So'nggi buyurtmalar:</b>\n"
    for order in orders[:10]:
        order_id = order.get("order_id")
        status = order.get("status", "pending")
        user_id = order.get("user_id")
        total = order.get("total", 0)
        text += f"#{order_id} - {format_order_status(status)} - ${total:.2f}\n"
    
    buttons = []
    for order in orders[:10]:
        order_id = order.get("order_id")
        buttons.append([
            InlineKeyboardButton(
                text=f"Buyurtma #{order_id}",
                callback_data=f"admin_order_{order_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="⏳ Kutilayotganlar", callback_data="admin_orders_pending"),
        InlineKeyboardButton(text="🔄 Faollar", callback_data="admin_orders_active")
    ])
    
    buttons.append([
        InlineKeyboardButton(text=f"{EMOJI_BACK} Admin panel", callback_data="admin_panel")
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_order_"))
async def show_admin_order_details(callback: CallbackQuery):
    """Display order details for admin."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    try:
        order_id = int(callback.data.split("_")[2])
        order = db.get_order(order_id)
        
        if not order:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return
        
        text = f"📦 <b>Buyurtma #{order_id}</b>\n\n"
        text += f"Status: {format_order_status(order.get('status', 'pending'))}\n"
        text += f"👤 Foydalanuvchi ID: {order.get('user_id')}\n"
        
        if order.get("created_at"):
            text += f"📅 Sana: {format_datetime(order['created_at'])}\n"
        
        text += "\n<b>Mahsulotlar:</b>\n"
        total = 0
        for item_id_str, quantity in order.get("items", {}).items():
            item = db.get_item_by_id(int(item_id_str))
            if item:
                item_total = item["price"] * quantity
                total += item_total
                text += f"• {item['name']} x{quantity} = {format_price(item_total)}\n"
        
        text += f"\n<b>Jami:</b> {format_price(total + order.get('delivery_fee', 0) - order.get('discount', 0))}\n"
        
        # Status update buttons
        current_status = order.get("status", "pending")
        buttons = []
        
        for status in ORDER_STATUSES:
            if status != current_status:
                status_names = {
                    "pending": "⏳ Kutilmoqda",
                    "confirmed": "✅ Tasdiqlandi",
                    "preparing": "👨‍🍳 Tayyorlanmoqda",
                    "ready": "📦 Tayyor",
                    "delivered": "🚚 Yetkazildi",
                    "cancelled": "❌ Bekor qilindi"
                }
                buttons.append([
                    InlineKeyboardButton(
                        text=status_names.get(status, status),
                        callback_data=f"admin_update_status_{order_id}_{status}"
                    )
                ])
        
        buttons.append([
            InlineKeyboardButton(text=f"{EMOJI_BACK} Buyurtmalar", callback_data="admin_orders")
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("admin_update_status_"))
async def update_order_status(callback: CallbackQuery):
    """Update order status."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    try:
        parts = callback.data.split("_")
        order_id = int(parts[3])
        new_status = parts[4]
        
        db.update_order_status(order_id, new_status)
        
        await callback.answer(
            f"✅ Status yangilandi: {format_order_status(new_status)}",
            show_alert=True
        )
        
        # Refresh order details
        await show_admin_order_details(callback)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
