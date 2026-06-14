from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from app.models.category import Category
from app.models.product import Product


def categories_kb(categories: List[Category]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        emoji = cat.emoji or "🔥"
        builder.button(text=f"{emoji} {cat.name}", callback_data=f"cat:{cat.id}")
    builder.button(text="📋 Barcha tandirlar", callback_data="cat:all")
    builder.button(text="⬅️ Bosh menyu", callback_data="back:main")
    builder.adjust(1)
    return builder.as_markup()


def products_kb(products: List[Product], back_callback: str = "cat:back") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.button(text=product.name, callback_data=f"prod:{product.id}")
    builder.button(text="⬅️ Ortga", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def product_detail_kb(product_id: int, back_callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 Buyurtma berish", callback_data=f"order:{product_id}")
    builder.button(text="📞 Biz bilan bog'lanish", callback_data="goto:contact")
    builder.button(text="⬅️ Ortga", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()
