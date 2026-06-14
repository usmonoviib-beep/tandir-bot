from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.models.product import Product
from .base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(Product, session)

    async def get_by_category(self, category_id: int) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.category_id == category_id, Product.is_active == True)
            .order_by(Product.order, Product.id)
        )
        return list(result.scalars().all())

    async def get_all_active(self) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.is_active == True)
            .options(selectinload(Product.category))
            .order_by(Product.order, Product.id)
        )
        return list(result.scalars().all())

    async def get_with_category(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.category))
        )
        return result.scalar_one_or_none()

    async def get_all_for_admin(self) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .order_by(Product.category_id, Product.order, Product.id)
        )
        return list(result.scalars().all())
