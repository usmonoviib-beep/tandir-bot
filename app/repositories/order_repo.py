from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.order import Order, OrderStatus
from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, session: AsyncSession):
        super().__init__(Order, session)

    async def get_all_with_relations(self) -> List[Order]:
        result = await self.session.execute(
            select(Order)
            .options(selectinload(Order.user), selectinload(Order.product))
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> List[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.status == status)
            .options(selectinload(Order.user), selectinload(Order.product))
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_with_relations(self, order_id: int) -> Optional[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.user), selectinload(Order.product))
        )
        return result.scalar_one_or_none()

    async def count_total(self) -> int:
        result = await self.session.execute(select(func.count(Order.id)))
        return result.scalar() or 0

    async def count_by_product(self) -> List[dict]:
        from app.models.product import Product
        result = await self.session.execute(
            select(Product.name, func.count(Order.id).label("count"))
            .join(Order, Order.product_id == Product.id)
            .group_by(Product.id, Product.name)
            .order_by(func.count(Order.id).desc())
        )
        return [{"name": row.name, "count": row.count} for row in result.all()]
