from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.filters import IsAdmin
from app.keyboards.admin import admin_panel_kb
from app.keyboards.user import main_menu_kb

router = Router(name="admin_panel")
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "👑 <b>Admin panel</b>\n\nKerakli bo'limni tanlang 👇",
        reply_markup=admin_panel_kb(),
    )


@router.message(F.text == "🚪 Foydalanuvchi rejimiga o'tish")
async def exit_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🏠 Foydalanuvchi rejimiga o'tdingiz.",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "⚙️ Sozlamalar")
async def settings_menu(message: Message) -> None:
    from config.settings import settings as cfg

    text = (
        "⚙️ <b>Sozlamalar</b>\n\n"
        f"🤖 Bot username: @{cfg.BOT_USERNAME}\n"
        f"👑 Adminlar soni: {len(cfg.admin_ids_list)}\n"
        f"📢 Kanal: {cfg.CHANNEL_URL}\n"
        f"💬 Admin telegram: {cfg.ADMIN_TELEGRAM}\n"
        f"📞 Admin telefon: {cfg.ADMIN_PHONE}\n"
        f"📍 Manzil: {cfg.COMPANY_ADDRESS}\n\n"
        "ℹ️ Sozlamalarni o'zgartirish uchun <code>config/settings.py</code> "
        "yoki <code>.env</code> faylini tahrirlang va botni qayta ishga tushiring."
    )
    await message.answer(text)
