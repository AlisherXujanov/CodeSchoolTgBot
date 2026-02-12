"""
Promotions and loyalty system handler.
Handles promo codes, special offers, and loyalty program.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.db_helper import db
from utils.constants import EMOJI_PROMOTIONS, EMOJI_BACK, EMOJI_CHECK
from utils.formatters import format_price

router = Router()


@router.callback_query(F.data == "promotions")
async def show_promotions(callback: CallbackQuery):
    """Display available promotions and offers."""
    text = f"{EMOJI_PROMOTIONS} <b>Promotsiyalar va takliflar</b>\n\n"
    
    # Get active promo codes
    promo_codes = db.data.get("promo_codes", {})
    active_promos = [
        p for p in promo_codes.values()
        if p.get("is_active", True)
    ]
    
    if active_promos:
        text += "<b>Faol promo kodlar:</b>\n"
        for promo in active_promos[:5]:  # Show first 5
            code = promo.get("code", "")
            discount_type = promo.get("discount_type", "percentage")
            discount_value = promo.get("discount_value", 0)
            min_order = promo.get("min_order", 0)
            
            if discount_type == "percentage":
                discount_text = f"{discount_value}%"
            else:
                discount_text = format_price(discount_value)
            
            text += f"🎁 <b>{code}</b> - {discount_text} chegirma\n"
            if min_order > 0:
                text += f"   Minimal buyurtma: {format_price(min_order)}\n"
            text += "\n"
    else:
        text += "Hozircha faol promo kodlar yo'q.\n\n"
    
    # Loyalty program info
    user = db.get_user(callback.from_user.id)
    loyalty_points = user.get("loyalty_points", 0)
    
    text += "<b>Loyalti dasturi:</b>\n"
    text += f"💰 Sizning ballaringiz: {loyalty_points}\n"
    text += "Har bir dollarda 1 ball olasiz!\n"
    text += "100 ball = $1 chegirma\n\n"
    
    text += "Promo kodni qo'llash uchun /promo KOD buyrug'ini ishlating."
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🍽️ Buyurtma berish", callback_data="menu")],
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Asosiy menyu", callback_data="back")]
        ])
    )
    await callback.answer()


@router.message(Command("promo"))
async def apply_promo_command(message: Message):
    """Handle /promo command to apply promo code."""
    try:
        # Extract promo code from command
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer(
                "❌ Promo kod kiritilmadi!\n\n"
                "Ishlatish: <code>/promo KOD</code>\n"
                "Masalan: <code>/promo SALE10</code>"
            )
            return
        
        promo_code = parts[1].upper()
        user_id = message.from_user.id
        
        # Apply promo code
        success = db.apply_promo_code(user_id, promo_code)
        
        if success:
            cart = db.get_cart(user_id)
            promo = db.get_promo_code(promo_code)
            
            if promo:
                discount_type = promo.get("discount_type", "percentage")
                discount_value = promo.get("discount_value", 0)
                
                if discount_type == "percentage":
                    discount_text = f"{discount_value}%"
                else:
                    discount_text = format_price(discount_value)
                
                await message.answer(
                    f"{EMOJI_CHECK} <b>Promo kod qo'llandi!</b>\n\n"
                    f"Kod: <b>{promo_code}</b>\n"
                    f"Chegirma: {discount_text}\n\n"
                    f"Savatingizni ko'rish uchun /cart buyrug'ini ishlating."
                )
            else:
                await message.answer(f"{EMOJI_CHECK} Promo kod qo'llandi!")
        else:
            await message.answer(
                "❌ Promo kod topilmadi yoki faol emas!\n\n"
                "Mavjud promo kodlarni ko'rish uchun 'Promotsiyalar' tugmasini bosing."
            )
            
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi! Iltimos, qayta urinib ko'ring.")


@router.callback_query(F.data == "apply_promo")
async def apply_promo_callback(callback: CallbackQuery):
    """Redirect to promo command help."""
    await callback.message.edit_text(
        "🎁 <b>Promo kod qo'llash</b>\n\n"
        "Promo kodni qo'llash uchun quyidagi formatda yuboring:\n"
        "<code>/promo KOD</code>\n\n"
        "Masalan:\n"
        "<code>/promo SALE10</code>\n\n"
        "Yoki 'Promotsiyalar' bo'limidan faol kodlarni ko'rishingiz mumkin.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Promotsiyalar", callback_data="promotions")],
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Savat", callback_data="cart")]
        ])
    )
    await callback.answer()
