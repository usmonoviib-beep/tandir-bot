from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from config.settings import settings
from app.models.base import Base
from app.utils.logger import logger


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    poolclass=NullPool if "sqlite" in settings.DATABASE_URL else None,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_tables() -> None:
    """Jadvallarni yaratish (birinchi ishga tushirishda)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Ma'lumotlar bazasi jadvallari tayyor")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection uchun sessiya"""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
