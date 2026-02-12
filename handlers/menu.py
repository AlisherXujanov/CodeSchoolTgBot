from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database.db_helper import db
from keyboards.main_keyboard import get_main_keyboard, get_back_keyboard
from utils.decorators import is_admin

# Create router instance
router = Router()

# Category display names (Uzbek)
CATEGORY_NAMES = {
    "pizza": "Pitsa",
    "burgers": "Burgerlar",
    "drinks": "Ichimliklar",
}


@router.callback_query(F.data == "menu")
async def show_menu_categories(callback: CallbackQuery):
    """Show menu categories"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🍕 Pitsa", callback_data="category_pizza"),
            InlineKeyboardButton(
                text="🍔 Burgerlar", callback_data="category_burgers")
        ],
        [
            InlineKeyboardButton(
                text="🥤 Ichimliklar", callback_data="category_drinks"),
            InlineKeyboardButton(text="🛒 Savat", callback_data="cart")
        ],
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back")
        ]
    ])

    await callback.message.edit_text(
        "🍽️ <b>Kategoriyani tanlang:</b>",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_items(callback: CallbackQuery):
    """Show items in selected category"""
    category = callback.data.split("_")[1]
    items = db.get_menu_category(category)

    if not items:
        await callback.answer("Bu kategoriya boʻsh!", show_alert=True)
        return

    keyboard_buttons = []
    category_title = CATEGORY_NAMES.get(category, category.title())
    text = f"🍽️ <b>{category_title}</b>\n\n"

    for item in items:
        text += f"<b>{item['name']}</b> - ${item['price']:.2f}\n"
        text += f"<i>{item['description']}</i>\n\n"

        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"➕ Qoʻshish: {item['name']}",
                callback_data=f"add_{item['id']}"
            )
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(text="⬅️ Menyuga qaytish", callback_data="menu")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    """Add item to cart"""
    item_id = int(callback.data.split("_")[1])
    item = db.get_item_by_id(item_id)

    if not item:
        await callback.answer("Mahsulot topilmadi!", show_alert=True)
        return

    db.add_to_cart(callback.from_user.id, item_id)

    await callback.answer(f"✅ {item['name']} savatga qoʻshildi!", show_alert=True)


# Cart handlers moved to handlers/cart.py


@router.callback_query(F.data == "contact")
async def show_contact(callback: CallbackQuery):
    """Show contact information"""
    contact_text = """
📞 <b>Aloqa maʼlumotlari</b>

📱 Telefon: +1 (555) 123-4567
📧 Email: info@restaurant.com
🌐 Vebsayt: www.restaurant.com

<b>Bizni kuzating:</b>
📘 Facebook: @restaurant
📷 Instagram: @restaurant
🐦 Twitter: @restaurant
    """

    await callback.message.edit_text(
        contact_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "location")
async def show_location(callback: CallbackQuery):
    """Show restaurant location"""
    await callback.message.edit_text(
        "📍 <b>Bizning joylashuvimiz</b>\n\n"
        "123 Main Street\n"
        "City Center, State 12345\n\n"
        "Shahar markazida joylashganmiz!",
        reply_markup=get_back_keyboard()
    )
    # Send actual location
    await callback.message.answer_location(
        latitude=40.7128,  # Replace with actual coordinates
        longitude=-74.0060
    )
    await callback.answer()


@router.callback_query(F.data == "hours")
async def show_hours(callback: CallbackQuery):
    """Show opening hours"""
    hours_text = """
⏰ <b>Ish vaqti</b>

<b>Dushanba - Payshanba:</b> 11:00 - 22:00
<b>Juma - Shanba:</b> 11:00 - 23:00
<b>Yakshanba:</b> 12:00 - 21:00

<b>Oshxona yopilishdan 30 daqiqa oldin ishlashni toʻxtatadi</b>
    """

    await callback.message.edit_text(
        hours_text,
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    """Go back to main menu"""
    await callback.message.edit_text(
        f"👋 Qaytganingiz bilan, {callback.from_user.full_name}!\n\n"
        f"Nima qilmoqchisiz?",
        reply_markup=get_main_keyboard(callback.from_user.id)
    )
    await callback.answer()
