from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.repositories.order_repo import OrderRepository


class StatsService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.order_repo = OrderRepository(session)

    async def get_full_stats(self) -> dict:
        return {
            "users_total": await self.user_repo.count_total(),
            "users_today": await self.user_repo.count_today(),
            "users_weekly": await self.user_repo.count_weekly(),
            "users_monthly": await self.user_repo.count_monthly(),
            "orders_total": await self.order_repo.count_total(),
            "orders_by_product": await self.order_repo.count_by_product(),
        }
