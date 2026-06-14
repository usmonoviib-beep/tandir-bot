from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List

from app.models.category import Category
from app.models.product import Product


def admin_products_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Mahsulot qo'shish", callback_data="ap:add")
    builder.button(text="✏️ Tahrirlash / ❌ O'chirish", callback_data="ap:list")
    builder.button(text="📂 Kategoriyalar", callback_data="ap:categories")
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_kb(categories: List[Category], show_add: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        emoji = cat.emoji or "🔥"
        builder.button(text=f"{emoji} {cat.name}", callback_data=f"apcat:{cat.id}")
    if show_add:
        builder.button(text="➕ Kategoriya qo'shish", callback_data="apcat:add")
    builder.button(text="⬅️ Ortga", callback_data="ap:menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_select_kb(categories: List[Category]) -> InlineKeyboardMarkup:
    """Yangi mahsulot uchun kategoriya tanlash"""
    builder = InlineKeyboardBuilder()
    for cat in categories:
        emoji = cat.emoji or "🔥"
        builder.button(text=f"{emoji} {cat.name}", callback_data=f"apaddcat:{cat.id}")
    builder.button(text="⬅️ Bekor qilish", callback_data="ap:menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_products_list_kb(products: List[Product], category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        status = "✅" if product.is_active else "🚫"
        builder.button(
            text=f"{status} {product.name}",
            callback_data=f"approd:{product.id}",
        )
    builder.button(text="⬅️ Ortga", callback_data="ap:categories")
    builder.adjust(1)
    return builder.as_markup()


def admin_product_actions_kb(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Nomi", callback_data=f"apedit:name:{product_id}")
    builder.button(text="📝 Tavsif", callback_data=f"apedit:description:{product_id}")
    builder.button(text="💰 Narx", callback_data=f"apedit:price:{product_id}")
    builder.button(text="📏 O'lcham", callback_data=f"apedit:size:{product_id}")
    builder.button(text="📦 Sig'im", callback_data=f"apedit:capacity:{product_id}")
    builder.button(text="🚚 Yetkazib berish", callback_data=f"apedit:delivery_info:{product_id}")
    builder.button(text="📷 Rasm qo'shish", callback_data=f"apphoto:{product_id}")
    builder.button(text="🎥 Video yuklash", callback_data=f"apvideo:{product_id}")
    builder.button(text="🔁 Faollik holatini almashtirish", callback_data=f"aptoggle:{product_id}")
    builder.button(text="❌ O'chirish", callback_data=f"apdel:{product_id}")
    builder.button(text="⬅️ Ortga", callback_data=f"apcat:{category_id}")
    builder.adjust(2, 2, 2, 1, 1, 1, 1, 1)
    return builder.as_markup()


def confirm_delete_kb(product_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Ha, o'chirish", callback_data=f"apdelconfirm:{product_id}")
    builder.button(text="❌ Yo'q, bekor qilish", callback_data=f"approd:{product_id}")
    builder.adjust(1)
    return builder.as_markup()


def skip_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➡️ O'tkazib yuborish"))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def photos_done_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✅ Rasmlar tugadi"))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def confirm_product_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✅ Saqlash"))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)
