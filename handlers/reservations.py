"""
Reservation system handler.
Handles table booking, viewing reservations, and managing reservations.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from utils.formatters import format_reservation_status, format_date, format_time
from utils.constants import EMOJI_RESERVATIONS, EMOJI_BACK, EMOJI_CHECK
from datetime import datetime, timedelta

router = Router()


@router.callback_query(F.data == "reservations")
async def show_reservations(callback: CallbackQuery):
    """Display user's reservations."""
    user_id = callback.from_user.id
    reservations = db.get_user_reservations(user_id)
    
    if not reservations:
        await callback.message.edit_text(
            f"{EMOJI_RESERVATIONS} <b>Bronlar</b>\n\n"
            "Sizda hali bronlar yo'q.\n"
            "Yangi bron qilish uchun quyidagi tugmani bosing!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📅 Yangi bron", callback_data="new_reservation")],
                [InlineKeyboardButton(text=f"{EMOJI_BACK} Asosiy menyu", callback_data="back")]
            ])
        )
        await callback.answer()
        return
    
    text = f"{EMOJI_RESERVATIONS} <b>Bronlar</b>\n\n"
    
    for res in reservations[:5]:  # Show first 5
        res_id = res.get("reservation_id")
        date = res.get("date", "")
        time = res.get("time", "")
        party_size = res.get("party_size", 1)
        status = res.get("status", "pending")
        
        text += f"<b>#{res_id}</b> - {format_reservation_status(status)}\n"
        text += f"📅 {format_date(date)}\n"
        text += f"🕐 {format_time(time)}\n"
        text += f"👥 {party_size} kishi\n\n"
    
    buttons = []
    for res in reservations[:5]:
        res_id = res.get("reservation_id")
        buttons.append([
            InlineKeyboardButton(
                text=f"Bron #{res_id}",
                callback_data=f"reservation_{res_id}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(text="📅 Yangi bron", callback_data="new_reservation"),
        InlineKeyboardButton(text=f"{EMOJI_BACK} Asosiy menyu", callback_data="back")
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data == "new_reservation")
async def new_reservation_prompt(callback: CallbackQuery):
    """Prompt user to create a new reservation."""
    await callback.message.edit_text(
        "📅 <b>Yangi bron</b>\n\n"
        "Bron qilish uchun quyidagi formatda yuboring:\n"
        "<code>/reserve YYYY-MM-DD HH:MM X</code>\n\n"
        "Masalan:\n"
        "<code>/reserve 2025-02-15 19:00 4</code>\n\n"
        "Bu sizga 2025-yil 15-fevral, soat 19:00 da 4 kishilik stolni bron qiladi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Bronlar", callback_data="reservations")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reservation_"))
async def show_reservation_details(callback: CallbackQuery):
    """Display reservation details."""
    try:
        res_id = int(callback.data.split("_")[1])
        reservation = db.get_reservation(res_id)
        
        if not reservation or reservation.get("user_id") != callback.from_user.id:
            await callback.answer("Bron topilmadi!", show_alert=True)
            return
        
        text = f"{EMOJI_RESERVATIONS} <b>Bron #{res_id}</b>\n\n"
        text += f"Status: {format_reservation_status(reservation.get('status', 'pending'))}\n"
        text += f"📅 Sana: {format_date(reservation.get('date', ''))}\n"
        text += f"🕐 Vaqt: {format_time(reservation.get('time', ''))}\n"
        text += f"👥 Mehmonlar soni: {reservation.get('party_size', 1)}\n"
        
        if reservation.get("special_requests"):
            text += f"\n📝 Maxsus so'rovlar:\n{reservation['special_requests']}\n"
        
        buttons = []
        if reservation.get("status") == "pending":
            buttons.append([
                InlineKeyboardButton(
                    text="❌ Bronni bekor qilish",
                    callback_data=f"cancel_reservation_{res_id}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(text=f"{EMOJI_BACK} Bronlar", callback_data="reservations")
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("cancel_reservation_"))
async def cancel_reservation(callback: CallbackQuery):
    """Cancel a reservation."""
    try:
        res_id = int(callback.data.split("_")[2])
        reservation = db.get_reservation(res_id)
        
        if not reservation or reservation.get("user_id") != callback.from_user.id:
            await callback.answer("Bron topilmadi!", show_alert=True)
            return
        
        db.update_reservation_status(res_id, "cancelled")
        await callback.answer("✅ Bron bekor qilindi!", show_alert=True)
        
        # Refresh reservation details
        await show_reservation_details(callback)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
