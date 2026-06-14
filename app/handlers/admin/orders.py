from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from html import escape

from app.filters import IsAdmin
from app.services.order_service import OrderService
from app.keyboards.admin import orders_filter_kb, orders_list_kb, order_detail_kb
from app.utils.helpers import format_price, order_status_emoji, format_datetime
from app.models.order import OrderStatus

router = Router(name="admin_orders")
router.message.filter(IsAdmin())


STATUS_TITLES = {
    "new": "🟡 Yangi buyurtmalar",
    "in_progress": "🔵 Jarayondagi buyurtmalar",
    "completed": "🟢 Yakunlangan buyurtmalar",
    "cancelled": "🔴 Bekor qilingan buyurtmalar",
    "all": "📋 Barcha buyurtmalar",
}


@router.message(F.text == "📨 Buyurtmalar")
async def show_orders_menu(message: Message) -> None:
    await message.answer(
        "📨 <b>Buyurtmalar</b>\n\nKerakli filterni tanlang 👇",
        reply_markup=orders_filter_kb(),
    )


@router.callback_query(IsAdmin(), F.data.startswith("ordstatus:"))
async def show_orders_list(callback: CallbackQuery, session: AsyncSession) -> None:
    status = callback.data.split(":", 1)[1]
    service = OrderService(session)

    if status == "all":
        orders = await service.get_all_orders()
    else:
        orders = await service.get_orders_by_status(status)

    title = STATUS_TITLES.get(status, "📋 Buyurtmalar")

    if not orders:
        await callback.answer("📭 Bu bo'limda buyurtmalar yo'q", show_alert=True)
        return

    text = f"{title}\n\nJami: {len(orders)} ta\n\nBatafsil ko'rish uchun bosing 👇"

    try:
        await callback.message.edit_text(text, reply_markup=orders_list_kb(orders, status))
    except Exception:
        await callback.message.answer(text, reply_markup=orders_list_kb(orders, status))
    await callback.answer()


@router.callback_query(IsAdmin(), F.data.startswith("ordview:"))
async def show_order_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    order_id = int(callback.data.split(":", 1)[1])
    service = OrderService(session)
    order = await service.get_order(order_id)

    if not order:
        await callback.answer("😔 Buyurtma topilmadi", show_alert=True)
        return

    username = f"@{escape(order.user.username)}" if order.user and order.user.username else "yo'q"

    text = (
        f"🔥 <b>Buyurtma #{order.id}</b>\n\n"
        f"👤 Ism: {escape(order.customer_name)}\n"
        f"📞 Telefon: {escape(order.customer_phone)}\n"
        f"🔥 Mahsulot: {escape(order.product.name) if order.product else '—'}\n"
        f"💰 Narx: {format_price(order.product.price) if order.product else '—'}\n"
        f"🆔 Telegram ID: <code>{order.user.telegram_id if order.user else '—'}</code>\n"
        f"👤 Username: {username}\n"
        f"🕒 Sana: {format_datetime(order.created_at)}\n\n"
        f"📌 Holat: {order_status_emoji(order.status)}\n\n"
        "Holatni o'zgartirish uchun tugmani bosing 👇"
    )

    try:
        await callback.message.edit_text(text, reply_markup=order_detail_kb(order.id, order.status))
    except Exception:
        await callback.message.answer(text, reply_markup=order_detail_kb(order.id, order.status))
    await callback.answer()


@router.callback_query(IsAdmin(), F.data.startswith("ordset:"))
async def set_order_status(callback: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    _, order_id_str, new_status = callback.data.split(":")
    order_id = int(order_id_str)

    service = OrderService(session)
    order = await service.update_status(order_id, new_status)

    if not order:
        await callback.answer("😔 Buyurtma topilmadi", show_alert=True)
        return

    await callback.answer(f"✅ Holat o'zgartirildi: {order_status_emoji(new_status)}")

    # Qayta yuklab ko'rsatish
    order = await service.get_order(order_id)
    username = f"@{escape(order.user.username)}" if order.user and order.user.username else "yo'q"

    text = (
        f"🔥 <b>Buyurtma #{order.id}</b>\n\n"
        f"👤 Ism: {escape(order.customer_name)}\n"
        f"📞 Telefon: {escape(order.customer_phone)}\n"
        f"🔥 Mahsulot: {escape(order.product.name) if order.product else '—'}\n"
        f"💰 Narx: {format_price(order.product.price) if order.product else '—'}\n"
        f"🆔 Telegram ID: <code>{order.user.telegram_id if order.user else '—'}</code>\n"
        f"👤 Username: {username}\n"
        f"🕒 Sana: {format_datetime(order.created_at)}\n\n"
        f"📌 Holat: {order_status_emoji(order.status)}\n\n"
        "Holatni o'zgartirish uchun tugmani bosing 👇"
    )

    try:
        await callback.message.edit_text(text, reply_markup=order_detail_kb(order.id, order.status))
    except Exception:
        pass

    # Mijozga xabar (ixtiyoriy - status o'zgarganda)
    if order.user and new_status in (OrderStatus.IN_PROGRESS.value, OrderStatus.COMPLETED.value, OrderStatus.CANCELLED.value):
        messages = {
            OrderStatus.IN_PROGRESS.value: "🔵 Sizning buyurtmangiz jarayonga olindi!",
            OrderStatus.COMPLETED.value: "🟢 Sizning buyurtmangiz yakunlandi! Xaridingiz uchun rahmat.",
            OrderStatus.CANCELLED.value: "🔴 Afsuski, sizning buyurtmangiz bekor qilindi. Batafsil ma'lumot uchun biz bilan bog'laning.",
        }
        try:
            await bot.send_message(
                order.user.telegram_id,
                f"📦 <b>Buyurtma #{order.id}</b>\n\n{messages[new_status]}"
            )
        except Exception:
            pass


@router.callback_query(IsAdmin(), F.data == "ord:menu")
async def back_to_filter(callback: CallbackQuery) -> None:
    try:
        await callback.message.edit_text(
            "📨 <b>Buyurtmalar</b>\n\nKerakli filterni tanlang 👇",
            reply_markup=orders_filter_kb(),
        )
    except Exception:
        await callback.message.answer(
            "📨 <b>Buyurtmalar</b>\n\nKerakli filterni tanlang 👇",
            reply_markup=orders_filter_kb(),
        )
    await callback.answer()


@router.callback_query(IsAdmin(), F.data == "ord:back")
async def back_to_filter_from_detail(callback: CallbackQuery) -> None:
    await back_to_filter(callback)
