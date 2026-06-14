from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from config.settings import settings


def request_phone_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📞 Raqamni yuborish", request_contact=True))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def cancel_order_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def contact_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📞 Telefon raqam", callback_data="contact:phone")
    builder.button(text="💬 Telegram", url=settings.ADMIN_TELEGRAM)
    builder.button(text="📍 Manzil", callback_data="contact:address")
    builder.button(text="⬅️ Bosh menyu", callback_data="back:main")
    builder.adjust(1)
    return builder.as_markup()
