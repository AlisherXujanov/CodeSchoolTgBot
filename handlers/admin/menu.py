"""
Admin menu management handler.
Allows admins to add, edit, delete menu items and categories.
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.db_helper import db
from utils.decorators import is_admin
from utils.constants import EMOJI_BACK, EMOJI_EDIT, EMOJI_DELETE, EMOJI_PLUS

router = Router()


@router.callback_query(F.data == "admin_menu")
async def show_admin_menu(callback: CallbackQuery):
    """Display menu management interface."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    menu = db.data.get("menu", {})
    
    text = "🍽️ <b>Menyu boshqaruvi</b>\n\n"
    
    total_items = 0
    for category, items in menu.items():
        available = sum(1 for item in items if item.get("available", True))
        text += f"<b>{category.title()}</b>: {len(items)} ta ({available} mavjud)\n"
        total_items += len(items)
    
    text += f"\n<b>Jami mahsulotlar:</b> {total_items}\n"
    
    buttons = []
    for category in menu.keys():
        buttons.append([
            InlineKeyboardButton(
                text=f"📁 {category.title()}",
                callback_data=f"admin_category_{category}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text=f"{EMOJI_PLUS} Yangi kategoriya",
            callback_data="admin_add_category"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(text=f"{EMOJI_BACK} Admin panel", callback_data="admin_panel")
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_category_"))
async def show_category_items_admin(callback: CallbackQuery):
    """Display category items for admin management."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    try:
        category = callback.data.split("_")[2]
        items = db.get_menu_category(category)
        
        text = f"🍽️ <b>{category.title()} - Mahsulotlar</b>\n\n"
        
        buttons = []
        for item in items:
            available = "✅" if item.get("available", True) else "❌"
            text += f"{available} <b>{item['name']}</b> - ${item['price']:.2f}\n"
            
            buttons.append([
                InlineKeyboardButton(
                    text=f"{EMOJI_EDIT} {item['name']}",
                    callback_data=f"admin_edit_item_{item['id']}"
                ),
                InlineKeyboardButton(
                    text=f"{EMOJI_DELETE}",
                    callback_data=f"admin_delete_item_{item['id']}"
                )
            ])
            
            # Toggle availability
            new_status = not item.get("available", True)
            status_text = "Yashirish" if item.get("available", True) else "Ko'rsatish"
            buttons.append([
                InlineKeyboardButton(
                    text=f"👁️ {status_text}",
                    callback_data=f"admin_toggle_item_{item['id']}"
                )
            ])
        
        buttons.append([
            InlineKeyboardButton(
                text=f"{EMOJI_PLUS} Yangi mahsulot",
                callback_data=f"admin_add_item_{category}"
            )
        ])
        
        buttons.append([
            InlineKeyboardButton(text=f"{EMOJI_BACK} Menyu", callback_data="admin_menu")
        ])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await callback.answer()
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)


@router.callback_query(F.data.startswith("admin_toggle_item_"))
async def toggle_item_availability(callback: CallbackQuery):
    """Toggle item availability."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q!", show_alert=True)
        return
    
    try:
        item_id = int(callback.data.split("_")[3])
        item = db.get_item_by_id(item_id)
        
        if not item:
            await callback.answer("Mahsulot topilmadi!", show_alert=True)
            return
        
        # Find and update item
        for category_items in db.data.get("menu", {}).values():
            for menu_item in category_items:
                if menu_item.get("id") == item_id:
                    menu_item["available"] = not menu_item.get("available", True)
                    db.save_data()
                    
                    status = "ko'rsatildi" if menu_item["available"] else "yashirildi"
                    await callback.answer(
                        f"✅ Mahsulot {status}!",
                        show_alert=True
                    )
                    
                    # Find category to refresh
                    for cat, items in db.data.get("menu", {}).items():
                        if any(i.get("id") == item_id for i in items):
                            callback.data = f"admin_category_{cat}"
                            await show_category_items_admin(callback)
                            return
                    return
        
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
        
    except Exception as e:
        await callback.answer("Xatolik yuz berdi!", show_alert=True)
