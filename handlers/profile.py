"""
User profile management handler.
Handles user profiles, addresses, favorites, loyalty points, and preferences.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from keyboards.profile_keyboard import get_profile_keyboard, get_addresses_keyboard
from utils.constants import EMOJI_PROFILE, EMOJI_BACK, EMOJI_CHECK
from utils.formatters import format_price

router = Router()


@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    """
    Display user profile information.
    Shows loyalty points, order history summary, and profile options.
    """
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    
    text = f"{EMOJI_PROFILE} <b>Profil</b>\n\n"
    text += f"👤 <b>Ism:</b> {callback.from_user.full_name}\n"
    
    if callback.from_user.username:
        text += f"📱 Username: @{callback.from_user.username}\n"
    
    # Loyalty points
    loyalty_points = user.get("loyalty_points", 0)
    text += f"\n🎁 <b>Loyalti ballari:</b> {loyalty_points}\n"
    
    # Calculate discount from points
    from utils.constants import LOYALTY_POINTS_REDEMPTION_RATE
    discount_available = loyalty_points // LOYALTY_POINTS_REDEMPTION_RATE
    if discount_available > 0:
        text += f"💰 Mavjud chegirma: {format_price(discount_available)}\n"
    
    # Order statistics
    total_orders = user.get("total_orders", 0)
    text += f"\n📦 <b>Buyurtmalar:</b> {total_orders} ta\n"
    
    # Addresses count
    addresses = user.get("addresses", [])
    text += f"📍 <b>Manzillar:</b> {len(addresses)} ta\n"
    
    # Favorites count
    favorites = user.get("favorites", [])
    text += f"❤️ <b>Sevimlilar:</b> {len(favorites)} ta\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_profile_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "addresses")
async def show_addresses(callback: CallbackQuery):
    """Display user's delivery addresses."""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    addresses = user.get("addresses", [])
    
    if not addresses:
        await callback.message.edit_text(
            "📍 <b>Manzillar</b>\n\n"
            "Sizda hali manzil qo'shilmagan.\n"
            "Yetkazib berish uchun manzil qo'shing!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ Yangi manzil qo'shish",
                        callback_data="add_address"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=f"{EMOJI_BACK} Profil",
                        callback_data="profile"
                    )
                ]
            ])
        )
        await callback.answer()
        return
    
    text = "📍 <b>Manzillar</b>\n\n"
    for addr in addresses:
        label = addr.get("label", "Manzil")
        is_default = addr.get("is_default", False)
        default_text = " (Asosiy)" if is_default else ""
        text += f"<b>{label}{default_text}</b>\n"
        text += f"{addr.get('street', '')}\n"
        text += f"{addr.get('city', '')}, {addr.get('postal_code', '')}\n"
        if addr.get("notes"):
            text += f"📝 {addr['notes']}\n"
        text += "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_addresses_keyboard(addresses)
    )
    await callback.answer()


@router.callback_query(F.data == "add_address")
async def add_address_prompt(callback: CallbackQuery):
    """
    Prompt user to add address.
    In a real implementation, this would use a state machine to collect address details.
    """
    await callback.message.edit_text(
        "📍 <b>Yangi manzil qo'shish</b>\n\n"
        "Manzil qo'shish uchun quyidagi formatda yuboring:\n"
        "<code>/address</code>\n\n"
        "Yoki quyidagi formatda:\n"
        "<code>Manzil nomi\nKo'cha\nShahar\nPochta indeksi</code>\n\n"
        "Masalan:\n"
        "<code>Uy\n123 Main Street\nTashkent\n100000</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Manzillar", callback_data="addresses")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "favorites")
async def show_favorites(callback: CallbackQuery):
    """Display user's favorite items."""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    favorite_ids = user.get("favorites", [])
    
    if not favorite_ids:
        await callback.message.edit_text(
            "❤️ <b>Sevimlilar</b>\n\n"
            "Sizda hali sevimli mahsulotlar yo'q.\n"
            "Mahsulotlarni sevimlilar ro'yxatiga qo'shish uchun menyudan tanlang!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🍽️ Menyu", callback_data="menu")],
                [InlineKeyboardButton(text=f"{EMOJI_BACK} Profil", callback_data="profile")]
            ])
        )
        await callback.answer()
        return
    
    text = "❤️ <b>Sevimlilar</b>\n\n"
    buttons = []
    
    for item_id in favorite_ids[:10]:  # Limit to 10
        item = db.get_item_by_id(item_id)
        if item:
            text += f"<b>{item['name']}</b> - {format_price(item['price'])}\n"
            text += f"<i>{item.get('description', '')}</i>\n\n"
            
            buttons.append([
                InlineKeyboardButton(
                    text=f"➕ {item['name']}",
                    callback_data=f"add_{item_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Olib tashlash",
                    callback_data=f"remove_favorite_{item_id}"
                )
            ])
    
    buttons.append([
        InlineKeyboardButton(text="🍽️ Menyu", callback_data="menu"),
        InlineKeyboardButton(text=f"{EMOJI_BACK} Profil", callback_data="profile")
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("remove_favorite_"))
async def remove_favorite(callback: CallbackQuery):
    """Remove item from favorites."""
    try:
        item_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        db.remove_favorite(user_id, item_id)
        
        item = db.get_item_by_id(item_id)
        if item:
            await callback.answer(
                f"❌ {item['name']} sevimlilar ro'yxatidan olib tashlandi",
                show_alert=False
            )
        else:
            await callback.answer("✅ Olib tashlandi", show_alert=False)
        
        # Refresh favorites display
        await show_favorites(callback)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data == "loyalty")
async def show_loyalty(callback: CallbackQuery):
    """Display loyalty points information."""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    loyalty_points = user.get("loyalty_points", 0)
    
    from utils.constants import LOYALTY_POINTS_PER_DOLLAR, LOYALTY_POINTS_REDEMPTION_RATE
    
    text = "🎁 <b>Loyalti ballari</b>\n\n"
    text += f"💰 <b>Jami ballar:</b> {loyalty_points}\n\n"
    
    # Calculate available discount
    discount_available = loyalty_points // LOYALTY_POINTS_REDEMPTION_RATE
    text += f"💵 <b>Mavjud chegirma:</b> {format_price(discount_available)}\n\n"
    
    text += "<b>Qanday ishlaydi:</b>\n"
    text += f"• Har bir dollarda {LOYALTY_POINTS_PER_DOLLAR} ball olasiz\n"
    text += f"• {LOYALTY_POINTS_REDEMPTION_RATE} ball = {format_price(1)} chegirma\n\n"
    
    text += "<b>Ballarni qanday ishlatish:</b>\n"
    text += "Buyurtma berishda ballarni ishlatish imkoniyati bo'ladi!"
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🍽️ Buyurtma berish", callback_data="menu")],
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Profil", callback_data="profile")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data == "preferences")
async def show_preferences(callback: CallbackQuery):
    """Display and manage user preferences."""
    user_id = callback.from_user.id
    user = db.get_user(user_id)
    preferences = user.get("preferences", {})
    
    text = "⚙️ <b>Sozlamalar</b>\n\n"
    
    if preferences:
        text += "<b>Joriy sozlamalar:</b>\n"
        if preferences.get("dietary_restrictions"):
            text += f"🍽️ Dieta: {preferences['dietary_restrictions']}\n"
        if preferences.get("allergies"):
            text += f"⚠️ Allergiyalar: {preferences['allergies']}\n"
        if preferences.get("spice_level"):
            text += f"🌶️ Ziravor darajasi: {preferences['spice_level']}\n"
    else:
        text += "Hozircha sozlamalar yo'q.\n"
    
    text += "\nSozlamalarni o'zgartirish uchun /settings buyrug'ini ishlating."
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{EMOJI_BACK} Profil", callback_data="profile")]
        ])
    )
    await callback.answer()
