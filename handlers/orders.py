"""
Order management handler.
Handles order history, order details, reordering, and order cancellation.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from keyboards.order_keyboard import get_order_history_keyboard, get_order_detail_keyboard
from utils.formatters import format_order_status, format_price, format_datetime
from utils.constants import ORDER_STATUS_PENDING, ORDER_STATUS_CANCELLED, EMOJI_ORDERS, EMOJI_BACK
from datetime import datetime, timedelta

router = Router()


@router.callback_query(F.data == "orders")
async def show_order_history(callback: CallbackQuery):
    """
    Display user's order history.
    Shows list of all past orders with their statuses.
    """
    user_id = callback.from_user.id
    orders = db.get_user_orders(user_id)
    
    if not orders:
        await callback.message.edit_text(
            f"{EMOJI_ORDERS} <b>Buyurtmalar tarixi</b>\n\n"
            "Sizda hali buyurtmalar yo'q.\n"
            "Birinchi buyurtmangizni berish uchun menyudan tanlang!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🍽️ Menyu", callback_data="menu")],
                [InlineKeyboardButton(text=f"{EMOJI_BACK} Asosiy menyu", callback_data="back")]
            ])
        )
        await callback.answer()
        return
    
    text = f"{EMOJI_ORDERS} <b>Buyurtmalar tarixi</b>\n\n"
    text += f"Jami buyurtmalar: {len(orders)}\n\n"
    
    # Show summary of recent orders
    for order in orders[:5]:  # Show first 5
        order_id = order.get("order_id")
        status = order.get("status", "pending")
        created_at = order.get("created_at", "")
        total = order.get("total", 0)
        delivery_fee = order.get("delivery_fee", 0)
        discount = order.get("discount", 0)
        
        text += f"<b>#{order_id}</b> - {format_order_status(status)}\n"
        if created_at:
            text += f"📅 {format_datetime(created_at)}\n"
        text += f"💰 {format_price(total + delivery_fee - discount)}\n\n"
    
    if len(orders) > 5:
        text += f"... va yana {len(orders) - 5} ta buyurtma\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_order_history_keyboard(orders)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_"))
async def show_order_details(callback: CallbackQuery):
    """
    Display detailed information about a specific order.
    Shows items, totals, status, and provides actions.
    """
    try:
        order_id = int(callback.data.split("_")[1])
        order = db.get_order(order_id)
        
        if not order or order.get("user_id") != callback.from_user.id:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return
        
        text = f"{EMOJI_ORDERS} <b>Buyurtma #{order_id}</b>\n\n"
        text += f"Status: {format_order_status(order.get('status', 'pending'))}\n"
        
        if order.get("created_at"):
            text += f"📅 Sana: {format_datetime(order['created_at'])}\n"
        if order.get("updated_at"):
            text += f"🔄 Yangilangan: {format_datetime(order['updated_at'])}\n"
        
        text += "\n<b>Mahsulotlar:</b>\n"
        
        total = 0
        for item_id_str, quantity in order.get("items", {}).items():
            item = db.get_item_by_id(int(item_id_str))
            if item:
                item_total = item["price"] * quantity
                total += item_total
                text += f"• {item['name']} x{quantity}\n"
                text += f"  {format_price(item['price'])} x {quantity} = {format_price(item_total)}\n"
        
        text += "\n<b>Hisob-kitob:</b>\n"
        text += f"Oraliq summa: {format_price(total)}\n"
        
        discount = order.get("discount", 0)
        if discount > 0:
            text += f"Chegirma: -{format_price(discount)}\n"
        
        delivery_fee = order.get("delivery_fee", 0)
        if delivery_fee > 0:
            text += f"Yetkazib berish: {format_price(delivery_fee)}\n"
        
        final_total = total + delivery_fee - discount
        text += f"<b>Jami: {format_price(final_total)}</b>\n"
        
        if order.get("promo_code"):
            text += f"\n🎁 Promo kod: {order['promo_code']}\n"
        
        if order.get("notes"):
            text += f"\n📝 Izoh: {order['notes']}\n"
        
        if order.get("delivery_address"):
            addr = order["delivery_address"]
            text += f"\n📍 Yetkazib berish manzili:\n"
            text += f"{addr.get('street', '')}, {addr.get('city', '')}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_order_detail_keyboard(order_id, order.get("status", "pending"))
        )
        await callback.answer()
        
    except (ValueError, KeyError) as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("reorder_"))
async def reorder(callback: CallbackQuery):
    """
    Reorder items from a previous order.
    Adds all items from the order back to cart.
    """
    try:
        order_id = int(callback.data.split("_")[1])
        order = db.get_order(order_id)
        
        if not order or order.get("user_id") != callback.from_user.id:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return
        
        # Add all items to cart
        user_id = callback.from_user.id
        items_added = 0
        
        for item_id_str, quantity in order.get("items", {}).items():
            item_id = int(item_id_str)
            item = db.get_item_by_id(item_id)
            if item and item.get("available", True):
                db.add_to_cart(user_id, item_id, quantity)
                items_added += 1
        
        if items_added > 0:
            await callback.answer(
                f"✅ {items_added} ta mahsulot savatga qo'shildi!",
                show_alert=True
            )
            # Redirect to cart
            callback.data = "cart"
            from handlers.cart import show_cart
            await show_cart(callback)
        else:
            await callback.answer(
                "Bu buyurtmadagi mahsulotlar endi mavjud emas!",
                show_alert=True
            )
            
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("cancel_order_"))
async def cancel_order(callback: CallbackQuery):
    """
    Cancel a pending order.
    Only allows cancellation within a time limit.
    """
    try:
        order_id = int(callback.data.split("_")[2])
        order = db.get_order(order_id)
        
        if not order or order.get("user_id") != callback.from_user.id:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return
        
        if order.get("status") != ORDER_STATUS_PENDING:
            await callback.answer(
                "Faqat kutilayotgan buyurtmalarni bekor qilish mumkin!",
                show_alert=True
            )
            return
        
        # Check time limit (5 minutes)
        created_at_str = order.get("created_at")
        if created_at_str:
            created_at = datetime.fromisoformat(created_at_str)
            time_limit = timedelta(minutes=5)
            
            if datetime.now() - created_at > time_limit:
                await callback.answer(
                    "Buyurtmani bekor qilish muddati o'tgan! "
                    "Iltimos, restoran bilan bog'laning.",
                    show_alert=True
                )
                return
        
        # Cancel the order
        db.update_order_status(order_id, ORDER_STATUS_CANCELLED)
        
        await callback.answer("✅ Buyurtma bekor qilindi!", show_alert=True)
        
        # Refresh order details
        await show_order_details(callback)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
