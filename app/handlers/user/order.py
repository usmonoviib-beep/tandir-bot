from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from html import escape

from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.keyboards.user import main_menu_kb, request_phone_kb, cancel_order_kb
from app.states import OrderStates
from config.settings import settings
from app.utils.logger import logger

router = Router(name="user_order")


@router.callback_query(F.data.startswith("order:"))
async def start_order(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    product_id = int(callback.data.split(":", 1)[1])

    service = ProductService(session)
    product = await service.get_product(product_id)

    if not product:
        await callback.answer("😔 Mahsulot topilmadi", show_alert=True)
        return

    await state.update_data(product_id=product_id, product_name=product.name)
    await state.set_state(OrderStates.waiting_name)

    await callback.message.answer(
        f"🛒 <b>Buyurtma berish</b>\n\n"
        f"Siz tanladingiz: <b>{product.name}</b>\n\n"
        f"✏️ Buyurtmani rasmiylashtirish uchun, iltimos, <b>ismingizni</b> kiriting:",
        reply_markup=cancel_order_kb(),
    )
    await callback.answer()


@router.message(OrderStates.waiting_name, F.text == "❌ Bekor qilish")
@router.message(OrderStates.waiting_phone, F.text == "❌ Bekor qilish")
async def cancel_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "❌ Buyurtma bekor qilindi.",
        reply_markup=main_menu_kb(),
    )


@router.message(OrderStates.waiting_name)
async def process_name(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer(
            "⚠️ Iltimos, to'g'ri ismingizni kiriting (kamida 2 ta belgi).",
            reply_markup=cancel_order_kb(),
        )
        return

    await state.update_data(customer_name=message.text.strip())
    await state.set_state(OrderStates.waiting_phone)

    await message.answer(
        "📞 Endi telefon raqamingizni yuboring.\n\n"
        "Pastdagi tugma orqali yuborishingiz mumkin yoki qo'lda yozing "
        "(masalan: +998901234567):",
        reply_markup=request_phone_kb(),
    )


@router.message(OrderStates.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    phone = message.contact.phone_number
    await finish_order(message, state, session, bot, phone)


@router.message(OrderStates.waiting_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    phone = message.text.strip()

    # Oddiy validatsiya
    cleaned = phone.replace(" ", "").replace("-", "")
    digits = "".join(filter(str.isdigit, cleaned))
    if len(digits) < 7:
        await message.answer(
            "⚠️ Telefon raqami noto'g'ri. Iltimos, to'g'ri raqam kiriting "
            "(masalan: +998901234567) yoki tugma orqali yuboring.",
            reply_markup=request_phone_kb(),
        )
        return

    await finish_order(message, state, session, bot, phone)


async def finish_order(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    bot: Bot,
    phone: str,
) -> None:
    data = await state.get_data()
    product_id = data.get("product_id")
    customer_name = data.get("customer_name")
    product_name = data.get("product_name", "Noma'lum")

    order_service = OrderService(session)
    order = await order_service.create_order(
        telegram_id=message.from_user.id,
        product_id=product_id,
        customer_name=customer_name,
        customer_phone=phone,
    )

    await state.clear()

    safe_name = escape(customer_name or "")
    safe_product = escape(product_name or "")
    safe_phone = escape(phone or "")

    await message.answer(
        "✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
        f"📦 Mahsulot: {safe_product}\n"
        f"👤 Ism: {safe_name}\n"
        f"📞 Telefon: {safe_phone}\n\n"
        "Tez orada operatorlarimiz siz bilan bog'lanadi. Rahmat! 🙏",
        reply_markup=main_menu_kb(),
    )

    # Adminlarga xabar yuborish
    username = f"@{escape(message.from_user.username)}" if message.from_user.username else "yo'q"
    admin_text = (
        "🔥 <b>YANGI BUYURTMA</b>\n\n"
        f"🆔 Buyurtma raqami: #{order.id}\n"
        f"👤 Ism: {safe_name}\n"
        f"📞 Telefon: {safe_phone}\n"
        f"🔥 Mahsulot: {safe_product}\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n"
        f"👤 Username: {username}\n"
        f"🕒 Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    for admin_id in settings.admin_ids_list:
        try:
            await bot.send_message(admin_id, admin_text)
        except Exception as e:
            logger.warning(f"Adminga xabar yuborilmadi ({admin_id}): {e}")
