from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from app.models.order import Order, OrderStatus


def orders_filter_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🟡 Yangi", callback_data="ordstatus:new")
    builder.button(text="🔵 Jarayonda", callback_data="ordstatus:in_progress")
    builder.button(text="🟢 Yakunlandi", callback_data="ordstatus:completed")
    builder.button(text="🔴 Bekor qilindi", callback_data="ordstatus:cancelled")
    builder.button(text="📋 Barchasi", callback_data="ordstatus:all")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def orders_list_kb(orders: List[Order], status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for order in orders:
        status_emoji = {
            OrderStatus.NEW.value: "🟡",
            OrderStatus.IN_PROGRESS.value: "🔵",
            OrderStatus.COMPLETED.value: "🟢",
            OrderStatus.CANCELLED.value: "🔴",
        }.get(order.status, "⚪")
        product_name = order.product.name if order.product else "?"
        builder.button(
            text=f"{status_emoji} #{order.id} | {order.customer_name} | {product_name}",
            callback_data=f"ordview:{order.id}",
        )
    builder.button(text="⬅️ Ortga", callback_data="ord:menu")
    builder.adjust(1)
    return builder.as_markup()


def order_detail_kb(order_id: int, current_status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    statuses = [
        (OrderStatus.NEW.value, "🟡 Yangi"),
        (OrderStatus.IN_PROGRESS.value, "🔵 Jarayonda"),
        (OrderStatus.COMPLETED.value, "🟢 Yakunlandi"),
        (OrderStatus.CANCELLED.value, "🔴 Bekor qilindi"),
    ]
    for status_value, label in statuses:
        if status_value != current_status:
            builder.button(text=label, callback_data=f"ordset:{order_id}:{status_value}")
    builder.button(text="⬅️ Ortga", callback_data="ord:back")
    builder.adjust(1)
    return builder.as_markup()
