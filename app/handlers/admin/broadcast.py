from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters import IsAdmin
from app.services.broadcast_service import BroadcastService
from app.states import AdminBroadcastStates
from app.keyboards.admin import (
    broadcast_type_kb,
    broadcast_skip_button_kb,
    broadcast_cancel_kb,
    broadcast_confirm_kb,
    admin_panel_kb,
)

router = Router(name="admin_broadcast")
router.message.filter(IsAdmin())

CANCEL_TEXT = "❌ Bekor qilish"
SEND_TEXT = "✅ Yuborish"
SKIP_BUTTON_TEXT = "➡️ Tugma qo'shmasdan davom etish"


@router.message(F.text == "📢 Reklama")
async def broadcast_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "📢 <b>Reklama yuborish</b>\n\nReklama turini tanlang 👇",
        reply_markup=broadcast_type_kb(),
    )


@router.callback_query(IsAdmin(), F.data.startswith("bctype:"))
async def broadcast_type_chosen(callback: CallbackQuery, state: FSMContext) -> None:
    bc_type = callback.data.split(":", 1)[1]
    await state.update_data(bc_type=bc_type)

    if bc_type == "text":
        await state.set_state(AdminBroadcastStates.waiting_text)
        await callback.message.answer(
            "📝 Yuboriladigan matnni kiriting (HTML formatlash qo'llab-quvvatlanadi):",
            reply_markup=broadcast_cancel_kb(),
        )
    elif bc_type == "photo":
        await state.set_state(AdminBroadcastStates.waiting_photo)
        await callback.message.answer(
            "🖼 Rasmni caption (matn) bilan birga yuboring:",
            reply_markup=broadcast_cancel_kb(),
        )
    elif bc_type == "video":
        await state.set_state(AdminBroadcastStates.waiting_video)
        await callback.message.answer(
            "🎥 Videoni caption (matn) bilan birga yuboring:",
            reply_markup=broadcast_cancel_kb(),
        )
    elif bc_type == "button":
        await state.set_state(AdminBroadcastStates.waiting_text)
        await callback.message.answer(
            "📝 Yuboriladigan matnni kiriting:",
            reply_markup=broadcast_cancel_kb(),
        )
    elif bc_type == "forward":
        await state.set_state(AdminBroadcastStates.waiting_forward)
        await callback.message.answer(
            "↪️ Yubormoqchi bo'lgan xabarni forward qiling:",
            reply_markup=broadcast_cancel_kb(),
        )

    await callback.answer()


# ============================================================
# BEKOR QILISH (umumiy)
# ============================================================

@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.waiting_text)
@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.waiting_photo)
@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.waiting_video)
@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.waiting_button_text)
@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.waiting_button_url)
@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.waiting_forward)
@router.message(F.text == CANCEL_TEXT, AdminBroadcastStates.confirm)
async def cancel_broadcast(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_panel_kb())


# ============================================================
# MATN
# ============================================================

@router.message(AdminBroadcastStates.waiting_text)
async def broadcast_text_entered(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    bc_type = data.get("bc_type")

    await state.update_data(bc_text=message.html_text)

    if bc_type == "button":
        await state.set_state(AdminBroadcastStates.waiting_button_text)
        await message.answer(
            "🔘 Tugma matnini kiriting (masalan: 'Batafsil'):",
            reply_markup=broadcast_cancel_kb(),
        )
    else:
        await show_broadcast_confirmation(message, state)


# ============================================================
# RASM
# ============================================================

@router.message(AdminBroadcastStates.waiting_photo)
async def broadcast_photo_entered(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(
            "⚠️ Iltimos, rasm yuboring.",
            reply_markup=broadcast_cancel_kb(),
        )
        return

    await state.update_data(
        bc_photo=message.photo[-1].file_id,
        bc_text=message.html_text or "",
    )
    await show_broadcast_confirmation(message, state)


# ============================================================
# VIDEO
# ============================================================

@router.message(AdminBroadcastStates.waiting_video)
async def broadcast_video_entered(message: Message, state: FSMContext) -> None:
    if not message.video:
        await message.answer(
            "⚠️ Iltimos, video yuboring.",
            reply_markup=broadcast_cancel_kb(),
        )
        return

    await state.update_data(
        bc_video=message.video.file_id,
        bc_text=message.html_text or "",
    )
    await show_broadcast_confirmation(message, state)


# ============================================================
# TUGMALI POST
# ============================================================

@router.message(AdminBroadcastStates.waiting_button_text)
async def broadcast_button_text_entered(message: Message, state: FSMContext) -> None:
    await state.update_data(bc_button_text=message.text.strip())
    await state.set_state(AdminBroadcastStates.waiting_button_url)
    await message.answer(
        "🔗 Tugma havolasini kiriting (https:// bilan boshlansin):",
        reply_markup=broadcast_cancel_kb(),
    )


@router.message(AdminBroadcastStates.waiting_button_url)
async def broadcast_button_url_entered(message: Message, state: FSMContext) -> None:
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
        await message.answer(
            "⚠️ Havola http://, https:// yoki tg:// bilan boshlanishi kerak.",
            reply_markup=broadcast_cancel_kb(),
        )
        return

    await state.update_data(bc_button_url=url)
    await show_broadcast_confirmation(message, state)


# ============================================================
# FORWARD
# ============================================================

@router.message(AdminBroadcastStates.waiting_forward)
async def broadcast_forward_entered(message: Message, state: FSMContext) -> None:
    if not message.forward_origin and not message.forward_from:
        # aiogram 3.13+ forward_origin orqali aniqlash mumkin, lekin
        # forward qilingan xabar ham odatiy message bo'lib keladi
        pass

    await state.update_data(
        bc_forward_chat_id=message.chat.id,
        bc_forward_message_id=message.message_id,
    )
    await show_broadcast_confirmation(message, state)


# ============================================================
# TASDIQLASH VA YUBORISH
# ============================================================

async def show_broadcast_confirmation(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminBroadcastStates.confirm)
    data = await state.get_data()
    bc_type = data.get("bc_type")

    preview_text = "👀 <b>Ko'rib chiqish</b>\n\n"

    if bc_type == "text":
        preview_text += data.get("bc_text", "")
        await message.answer(preview_text, reply_markup=broadcast_confirm_kb())
    elif bc_type == "photo":
        await message.answer_photo(
            data.get("bc_photo"),
            caption=data.get("bc_text") or None,
        )
        await message.answer(
            "⬆️ Reklama shu ko'rinishda yuboriladi.",
            reply_markup=broadcast_confirm_kb(),
        )
    elif bc_type == "video":
        await message.answer_video(
            data.get("bc_video"),
            caption=data.get("bc_text") or None,
        )
        await message.answer(
            "⬆️ Reklama shu ko'rinishda yuboriladi.",
            reply_markup=broadcast_confirm_kb(),
        )
    elif bc_type == "button":
        builder = InlineKeyboardBuilder()
        builder.button(text=data.get("bc_button_text"), url=data.get("bc_button_url"))
        await message.answer(
            data.get("bc_text", ""),
            reply_markup=builder.as_markup(),
        )
        await message.answer(
            "⬆️ Reklama shu ko'rinishda yuboriladi.",
            reply_markup=broadcast_confirm_kb(),
        )
    elif bc_type == "forward":
        await message.answer(
            "⬆️ Forward qilingan xabar shu ko'rinishda yuboriladi.",
            reply_markup=broadcast_confirm_kb(),
        )


@router.message(AdminBroadcastStates.confirm, F.text == SEND_TEXT)
async def send_broadcast(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    data = await state.get_data()
    bc_type = data.get("bc_type")

    await message.answer("⏳ Yuborish boshlandi, biroz kuting...", reply_markup=admin_panel_kb())

    service = BroadcastService(session, bot)

    reply_markup = None
    if bc_type == "button":
        builder = InlineKeyboardBuilder()
        builder.button(text=data.get("bc_button_text"), url=data.get("bc_button_url"))
        reply_markup = builder.as_markup()

    result = await service.broadcast(
        text=data.get("bc_text"),
        photo_id=data.get("bc_photo"),
        video_id=data.get("bc_video"),
        reply_markup=reply_markup,
        forward_from_chat_id=data.get("bc_forward_chat_id"),
        forward_message_id=data.get("bc_forward_message_id"),
    )

    await state.clear()

    await message.answer(
        "✅ <b>Reklama yuborildi!</b>\n\n"
        f"👥 Jami foydalanuvchilar: {result['total']}\n"
        f"✅ Muvaffaqiyatli: {result['success']}\n"
        f"❌ Xatolik: {result['failed']}",
    )
