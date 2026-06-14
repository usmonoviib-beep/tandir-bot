from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.filters import IsAdmin
from app.services.stats_service import StatsService
from app.utils.helpers import truncate_text

router = Router(name="admin_stats")
router.message.filter(IsAdmin())


@router.message(F.text == "📊 Statistika")
async def show_stats(message: Message, session: AsyncSession) -> None:
    service = StatsService(session)
    stats = await service.get_full_stats()

    text = (
        "📊 <b>Statistika</b>\n\n"
        "👥 <b>Foydalanuvchilar</b>\n"
        f"  • Jami: <b>{stats['users_total']}</b>\n"
        f"  • Bugun: <b>{stats['users_today']}</b>\n"
        f"  • Hafta: <b>{stats['users_weekly']}</b>\n"
        f"  • Oy: <b>{stats['users_monthly']}</b>\n\n"
        "📦 <b>Buyurtmalar</b>\n"
        f"  • Jami: <b>{stats['orders_total']}</b>\n"
    )

    if stats["orders_by_product"]:
        text += "\n🔥 <b>Mahsulotlar bo'yicha buyurtmalar:</b>\n"
        for item in stats["orders_by_product"]:
            name = truncate_text(item["name"], 35)
            text += f"  • {name}: <b>{item['count']}</b>\n"
    else:
        text += "\n📭 Hozircha buyurtmalar yo'q."

    await message.answer(text)
