from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from database.db_helper import db
from keyboards.main_keyboard import get_main_keyboard

# Create router instance
router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    """
    Handle /start command.
    Welcomes user and shows main menu with all available features.
    """
    user_id = message.from_user.id
    
    # Initialize user profile
    user = db.get_user(user_id)
    
    # Update user info if changed
    db.update_user(
        user_id,
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
        username=message.from_user.username
    )
    
    welcome_text = f"👋 Salom, {message.from_user.full_name}!\n\n"
    welcome_text += "🍽️ <b>Restoran botimizga xush kelibsiz!</b>\n\n"
    welcome_text += "Bizning botimizda quyidagi imkoniyatlar mavjud:\n\n"
    welcome_text += "🍽️ <b>Menyu</b> - Mahsulotlarni ko'rib chiqish va buyurtma berish\n"
    welcome_text += "🛒 <b>Savat</b> - Buyurtmalaringizni boshqarish\n"
    welcome_text += "📦 <b>Buyurtmalarim</b> - Buyurtmalar tarixi va holati\n"
    welcome_text += "👤 <b>Profil</b> - Profil sozlamalari va loyalti ballari\n"
    welcome_text += "📅 <b>Bronlar</b> - Stol bron qilish\n"
    welcome_text += "🎁 <b>Promotsiyalar</b> - Promo kodlar va takliflar\n"
    welcome_text += "📞 <b>Aloqa</b> - Biz bilan bog'lanish\n"
    welcome_text += "📍 <b>Joylashuv</b> - Restoran manzili\n"
    welcome_text += "⏰ <b>Ish vaqti</b> - Ish vaqtlari\n"
    
    # Show loyalty points if user has any
    loyalty_points = user.get("loyalty_points", 0)
    if loyalty_points > 0:
        welcome_text += f"\n🎁 Sizning loyalti ballaringiz: {loyalty_points}"
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(user_id)
    )
