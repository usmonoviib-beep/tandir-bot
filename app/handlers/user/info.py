from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.keyboards.user import main_menu_kb, contact_kb
from config.settings import settings

router = Router(name="user_info")


@router.message(F.text == "📢 Kanalimiz")
async def show_channel(message: Message) -> None:
    await message.answer(
        f"📢 Bizning rasmiy kanalimiz:\n\n{settings.CHANNEL_URL}\n\n"
        "Yangiliklar va aksiyalardan birinchilardan bo'lib xabardor bo'ling!",
        reply_markup=main_menu_kb(),
    )


@router.message(F.text == "📞 Bog'lanish")
async def show_contact(message: Message) -> None:
    await message.answer(
        "📞 <b>Biz bilan bog'lanish</b>\n\n"
        "Quyidagi usullardan birini tanlang:",
        reply_markup=contact_kb(),
    )


@router.message(F.text == "ℹ️ Bot haqida")
async def show_about(message: Message) -> None:
    await message.answer(settings.BOT_ABOUT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "contact:phone")
async def contact_phone(callback: CallbackQuery) -> None:
    await callback.message.answer(
        f"📞 Telefon raqamimiz:\n\n<b>{settings.ADMIN_PHONE}</b>\n\n"
        "Qo'ng'iroq qilib bog'lanishingiz mumkin."
    )
    await callback.answer()


@router.callback_query(F.data == "contact:address")
async def contact_address(callback: CallbackQuery) -> None:
    await callback.message.answer(
        f"📍 Manzilimiz:\n\n{settings.COMPANY_ADDRESS}"
    )
    await callback.answer()


@router.callback_query(F.data == "goto:contact")
async def goto_contact(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "📞 <b>Biz bilan bog'lanish</b>\n\n"
        "Quyidagi usullardan birini tanlang:",
        reply_markup=contact_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "back:main")
async def back_to_main(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        "🏠 Bosh menyu",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()
