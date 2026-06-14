from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.utils.logger import logger


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register_or_update(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
    ) -> tuple[User, bool]:
        user, is_new = await self.repo.get_or_create(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
        )
        if is_new:
            logger.info(f"Yangi foydalanuvchi: {telegram_id} | {full_name}")
        return user, is_new

    async def get_user(self, telegram_id: int) -> Optional[User]:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def get_all_active_ids(self):
        return await self.repo.get_all_active_ids()
