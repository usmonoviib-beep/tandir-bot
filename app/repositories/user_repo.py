from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from datetime import datetime, timedelta

from app.models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            user.last_activity = datetime.utcnow()
            if username:
                user.username = username
            if full_name:
                user.full_name = full_name
            await self.session.flush()
            return user, False

        user = await self.create(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )
        return user, True

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def count_today(self) -> int:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.created_at >= today)
        )
        return result.scalar() or 0

    async def count_weekly(self) -> int:
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.created_at >= week_ago)
        )
        return result.scalar() or 0

    async def count_monthly(self) -> int:
        month_ago = datetime.utcnow() - timedelta(days=30)
        result = await self.session.execute(
            select(func.count(User.id)).where(User.created_at >= month_ago)
        )
        return result.scalar() or 0

    async def get_all_active_ids(self) -> List[int]:
        result = await self.session.execute(
            select(User.telegram_id).where(User.is_active == True)
        )
        return list(result.scalars().all())
