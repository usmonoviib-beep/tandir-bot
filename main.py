import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.settings import settings
from app.database.connection import create_tables, AsyncSessionFactory
from app.handlers import setup_routers
from app.middlewares import DbSessionMiddleware, AdminAuthMiddleware, LoggingMiddleware
from app.utils.logger import logger
from app.repositories.category_repo import CategoryRepository


DEFAULT_CATEGORIES = [
    {"name": "Novvoy tandir", "emoji": "🍞", "slug": "novvoy"},
    {"name": "Somsa tandir", "emoji": "🥟", "slug": "somsa"},
    {"name": "Yer tandir", "emoji": "🌍", "slug": "yer"},
    {"name": "Aravali tandir", "emoji": "🛞", "slug": "aravali"},
    {"name": "Hovli tandiri", "emoji": "🏡", "slug": "hovli"},
    {"name": "Kafe va oshxona tandirlari", "emoji": "🏪", "slug": "kafe"},
    {"name": "Maxsus buyurtma tandirlar", "emoji": "🔥", "slug": "maxsus"},
]


async def seed_categories() -> None:
    """Birinchi marta ishga tushganda standart kategoriyalarni qo'shadi"""
    async with AsyncSessionFactory() as session:
        repo = CategoryRepository(session)
        existing = await repo.get_all_ordered()

        if existing:
            return

        for idx, cat in enumerate(DEFAULT_CATEGORIES):
            await repo.create(
                name=cat["name"],
                emoji=cat["emoji"],
                slug=cat["slug"],
                order=idx,
            )

        await session.commit()
        logger.info("✅ Standart kategoriyalar qo'shildi")


async def main() -> None:
    logger.info("🚀 Bot ishga tushmoqda...")

    # Ma'lumotlar bazasini tayyorlash
    await create_tables()
    await seed_categories()

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewarelar
    dp.update.middleware(DbSessionMiddleware())
    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(AdminAuthMiddleware())

    # Routerlar
    dp.include_router(setup_routers())

    # Eski xabarlarni o'chirib, pollingni boshlash
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Bot to'xtatildi")
