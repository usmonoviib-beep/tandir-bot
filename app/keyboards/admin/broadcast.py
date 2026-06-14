from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def broadcast_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Matn", callback_data="bctype:text")
    builder.button(text="🖼 Rasm", callback_data="bctype:photo")
    builder.button(text="🎥 Video", callback_data="bctype:video")
    builder.button(text="🔗 Tugmali post", callback_data="bctype:button")
    builder.button(text="↪️ Forward xabar", callback_data="bctype:forward")
    builder.button(text="⬅️ Ortga", callback_data="ap:menu")
    builder.adjust(1)
    return builder.as_markup()


def broadcast_skip_button_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➡️ Tugma qo'shmasdan davom etish"))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def broadcast_cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def broadcast_confirm_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✅ Yuborish"))
    builder.row(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)
