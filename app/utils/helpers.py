from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime]) -> str:
    if not dt:
        return "—"
    return dt.strftime("%d.%m.%Y %H:%M")


def format_price(price: Optional[float]) -> str:
    if not price:
        return "Narx so'rovda"
    return f"{price:,.0f} so'm".replace(",", " ")


def order_status_emoji(status: str) -> str:
    statuses = {
        "new": "🟡 Yangi",
        "in_progress": "🔵 Jarayonda",
        "completed": "🟢 Yakunlandi",
        "cancelled": "🔴 Bekor qilindi",
    }
    return statuses.get(status, "❓ Noma'lum")


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
