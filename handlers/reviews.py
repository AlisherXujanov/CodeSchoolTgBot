"""
Reviews and ratings handler.
Handles order reviews, item ratings, and feedback collection.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from utils.formatters import format_rating
from utils.validators import validate_rating
from utils.constants import EMOJI_REVIEWS, EMOJI_BACK, MIN_RATING, MAX_RATING
from utils.errors import ValidationError

router = Router()


@router.callback_query(F.data.startswith("review_order_"))
async def review_order_prompt(callback: CallbackQuery):
    """Prompt user to review an order."""
    try:
        order_id = int(callback.data.split("_")[2])
        order = db.get_order(order_id)
        
        if not order or order.get("user_id") != callback.from_user.id:
            await callback.answer("Buyurtma topilmadi!", show_alert=True)
            return
        
        # Check if already reviewed
        reviews = db.get_reviews(order_id=order_id)
        user_review = next((r for r in reviews if r.get("user_id") == callback.from_user.id), None)
        
        if user_review:
            await callback.message.edit_text(
                f"{EMOJI_REVIEWS} <b>Baho berildi</b>\n\n"
                f"Siz bu buyurtmaga allaqachon baho bergansiz:\n"
                f"{format_rating(user_review.get('rating', 0))}\n\n"
                f"{user_review.get('comment', 'Izoh yo\'q')}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"{EMOJI_BACK} Buyurtma", callback_data=f"order_{order_id}")]
                ])
            )
            await callback.answer()
            return
        
        # Show rating options
        buttons = []
        for rating in range(MIN_RATING, MAX_RATING + 1):
            buttons.append([
                InlineKeyboardButton(
                    text=f"{format_rating(rating)}",
                    callback_data=f"rate_order_{order_id}_{rating}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(text=f"{EMOJI_BACK} Buyurtma", callback_data=f"order_{order_id}")
        ])
        
        await callback.message.edit_text(
            f"{EMOJI_REVIEWS} <b>Buyurtmaga baho bering</b>\n\n"
            f"Buyurtma #{order_id} uchun qanday baho berasiz?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("rate_order_"))
async def submit_order_rating(callback: CallbackQuery):
    """Submit rating for an order."""
    try:
        parts = callback.data.split("_")
        order_id = int(parts[2])
        rating = int(parts[3])
        
        # Validate rating
        rating = validate_rating(rating)
        
        # Create review
        review_id = db.create_review(
            user_id=callback.from_user.id,
            rating=rating,
            order_id=order_id
        )
        
        await callback.answer(
            f"✅ {format_rating(rating)} Baho berildi! Rahmat!",
            show_alert=True
        )
        
        # Show thank you message
        await callback.message.edit_text(
            f"{EMOJI_REVIEWS} <b>Rahmat!</b>\n\n"
            f"Sizning bahoingiz: {format_rating(rating)}\n\n"
            f"Fikr-mulohazalaringiz biz uchun muhim!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📝 Izoh qo'shish", callback_data=f"add_comment_{review_id}")],
                [InlineKeyboardButton(text=f"{EMOJI_BACK} Buyurtma", callback_data=f"order_{order_id}")]
            ])
        )
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
