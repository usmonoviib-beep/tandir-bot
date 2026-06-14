from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from html import escape
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService
from app.keyboards.user import main_menu_kb
from app.utils.logger import logger

router = Router(name="user_start")


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession) -> None:
    user_service = UserService(session)
    user, is_new = await user_service.register_or_update(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
    )

    safe_name = escape(message.from_user.full_name or "")

    text = (
        f"👋 Assalomu alaykum, <b>{safe_name}</b>!\n\n"
        "🔥 <b>Tandir ishlab chiqarish korxonasi</b> botiga xush kelibsiz!\n\n"
        "Bizda turli xil tandirlar mavjud:\n"
        "🍞 Novvoy tandir\n"
        "🥟 Somsa tandir\n"
        "🌍 Yer tandir\n"
        "🛞 Aravali tandir\n"
        "🏡 Hovli tandiri\n"
        "🏪 Kafe va oshxona tandirlari\n"
        "🔥 Maxsus buyurtma tandirlar\n\n"
        "Quyidagi menyudan kerakli bo'limni tanlang 👇"
    )

    await message.answer(text, reply_markup=main_menu_kb())

    if is_new:
        logger.info(f"Yangi foydalanuvchi ro'yxatdan o'tdi: {message.from_user.id}")
