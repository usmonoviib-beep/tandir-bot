from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🔥 Tandirlar"))
    builder.row(
        KeyboardButton(text="📢 Kanalimiz"),
        KeyboardButton(text="📞 Bog'lanish"),
    )
    builder.row(KeyboardButton(text="ℹ️ Bot haqida"))
    return builder.as_markup(resize_keyboard=True)
