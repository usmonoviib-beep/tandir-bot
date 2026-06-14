from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repo import OrderRepository
from app.repositories.user_repo import UserRepository
from app.models.order import Order, OrderStatus
from app.utils.logger import logger


class OrderService:
    def __init__(self, session: AsyncSession):
        self.order_repo = OrderRepository(session)
        self.user_repo = UserRepository(session)

    async def create_order(
        self,
        telegram_id: int,
        product_id: int,
        customer_name: str,
        customer_phone: str,
    ) -> Order:
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if not user:
            raise ValueError(f"Foydalanuvchi topilmadi: {telegram_id}")

        order = await self.order_repo.create(
            user_id=user.id,
            product_id=product_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            status=OrderStatus.NEW.value,
        )
        logger.info(f"Yangi buyurtma: #{order.id} | {customer_name} | product={product_id}")
        return order

    async def get_all_orders(self) -> List[Order]:
        return await self.order_repo.get_all_with_relations()

    async def get_order(self, order_id: int) -> Optional[Order]:
        return await self.order_repo.get_with_relations(order_id)

    async def get_orders_by_status(self, status: str) -> List[Order]:
        return await self.order_repo.get_by_status(status)

    async def update_status(self, order_id: int, status: str) -> Optional[Order]:
        order = await self.order_repo.update(order_id, status=status)
        logger.info(f"Buyurtma holati yangilandi: #{order_id} -> {status}")
        return order

    async def count_total(self) -> int:
        return await self.order_repo.count_total()

    async def count_by_product(self) -> List[dict]:
        return await self.order_repo.count_by_product()
