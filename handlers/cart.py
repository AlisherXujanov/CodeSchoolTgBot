"""
Enhanced cart management handler.
Handles adding items, updating quantities, removing items, and applying promo codes.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from keyboards.cart_keyboard import get_cart_keyboard, get_empty_cart_keyboard
from utils.formatters import format_cart_summary
from utils.validators import validate_quantity
from utils.errors import ValidationError, CartError
from utils.constants import EMOJI_CART

router = Router()


@router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    """
    Display user's shopping cart with all items and controls.
    Shows item quantities, totals, and provides controls to modify cart.
    """
    user_id = callback.from_user.id
    cart = db.get_cart(user_id)
    
    if not cart.get("items"):
        await callback.message.edit_text(
            "🛒 <b>Savatingiz boʻsh</b>\n\n"
            "Menudan mahsulotlar qoʻshing!",
            reply_markup=get_empty_cart_keyboard()
        )
        await callback.answer()
        return
    
    # Get item details for display
    items = []
    for item_id_str in cart["items"].keys():
        item = db.get_item_by_id(int(item_id_str))
        if item:
            items.append(item)
    
    # Format cart summary
    text = format_cart_summary(cart, items)
    
    # Add promo code info if applied
    if cart.get("promo_code"):
        promo = db.get_promo_code(cart["promo_code"])
        if promo:
            text += f"\n\n🎁 <b>Promo kod:</b> {cart['promo_code']}"
            if cart.get("discount", 0) > 0:
                text += f"\n💰 <b>Chegirma:</b> ${cart['discount']:.2f}"
    
    # Check minimum order
    settings = db.get_settings()
    min_order = settings.get("min_order", 15.00)
    subtotal = cart.get("total", 0) - cart.get("discount", 0)
    
    if subtotal < min_order:
        text += f"\n\n⚠️ <b>Minimal buyurtma:</b> ${min_order:.2f}"
        text += f"\nYana ${min_order - subtotal:.2f} qo'shing!"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cart_keyboard(cart["items"], show_checkout=(subtotal >= min_order))
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cart_inc_"))
async def increase_quantity(callback: CallbackQuery):
    """
    Increase quantity of an item in cart.
    Validates quantity before updating to prevent errors.
    """
    try:
        item_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        cart = db.get_cart(user_id)
        current_quantity = cart["items"].get(str(item_id), 0)
        new_quantity = current_quantity + 1
        
        # Validate new quantity
        validate_quantity(new_quantity)
        
        db.update_cart_item_quantity(user_id, item_id, new_quantity)
        
        item = db.get_item_by_id(item_id)
        if item:
            await callback.answer(
                f"✅ {item['name']} miqdori oshirildi: {new_quantity}",
                show_alert=False
            )
        else:
            await callback.answer("✅ Miqdor oshirildi", show_alert=False)
        
        # Refresh cart display
        await show_cart(callback)
        
    except ValidationError as e:
        await callback.answer(e.message, show_alert=True)
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("cart_dec_"))
async def decrease_quantity(callback: CallbackQuery):
    """
    Decrease quantity of an item in cart.
    Removes item if quantity reaches 0.
    """
    try:
        item_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        cart = db.get_cart(user_id)
        current_quantity = cart["items"].get(str(item_id), 0)
        
        if current_quantity <= 1:
            # Remove item if quantity is 1 or less
            db.remove_from_cart(user_id, item_id)
            item = db.get_item_by_id(item_id)
            if item:
                await callback.answer(
                    f"🗑️ {item['name']} savatdan olib tashlandi",
                    show_alert=False
                )
        else:
            new_quantity = current_quantity - 1
            db.update_cart_item_quantity(user_id, item_id, new_quantity)
            item = db.get_item_by_id(item_id)
            if item:
                await callback.answer(
                    f"✅ {item['name']} miqdori kamaytirildi: {new_quantity}",
                    show_alert=False
                )
        
        # Refresh cart display
        await show_cart(callback)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("cart_remove_"))
async def remove_item(callback: CallbackQuery):
    """
    Remove item completely from cart.
    Provides confirmation feedback to user.
    """
    try:
        item_id = int(callback.data.split("_")[2])
        user_id = callback.from_user.id
        
        item = db.get_item_by_id(item_id)
        db.remove_from_cart(user_id, item_id)
        
        if item:
            await callback.answer(
                f"🗑️ {item['name']} savatdan olib tashlandi",
                show_alert=False
            )
        else:
            await callback.answer("✅ Mahsulot olib tashlandi", show_alert=False)
        
        # Refresh cart display
        await show_cart(callback)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    """
    Clear entire cart after user confirmation.
    Provides feedback and shows empty cart message.
    """
    user_id = callback.from_user.id
    db.clear_cart(user_id)
    
    await callback.answer("🗑️ Savat tozalandi!", show_alert=True)
    
    await callback.message.edit_text(
        "🛒 <b>Savatingiz boʻsh</b>\n\n"
        "Menudan mahsulotlar qoʻshing!",
        reply_markup=get_empty_cart_keyboard()
    )


@router.callback_query(F.data == "apply_promo")
async def apply_promo_prompt(callback: CallbackQuery):
    """
    Prompt user to enter promo code.
    In a real implementation, this would use a state machine to collect input.
    """
    await callback.message.edit_text(
        "🎁 <b>Promo kod kiriting:</b>\n\n"
        "Promo kodni yuborish uchun quyidagi formatda yuboring:\n"
        "<code>/promo KOD</code>\n\n"
        "Masalan: <code>/promo SALE10</code>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="cart")]
        ])
    )
    await callback.answer()
