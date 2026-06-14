from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def admin_panel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📦 Mahsulotlar"),
        KeyboardButton(text="📨 Buyurtmalar"),
    )
    builder.row(
        KeyboardButton(text="📊 Statistika"),
        KeyboardButton(text="📢 Reklama"),
    )
    builder.row(KeyboardButton(text="⚙️ Sozlamalar"))
    builder.row(KeyboardButton(text="🚪 Foydalanuvchi rejimiga o'tish"))
    return builder.as_markup(resize_keyboard=True)
