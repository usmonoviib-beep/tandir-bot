from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.category import Category
from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_active(self) -> List[Category]:
        result = await self.session.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.order, Category.id)
        )
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        result = await self.session.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_all_ordered(self) -> List[Category]:
        result = await self.session.execute(
            select(Category).order_by(Category.order, Category.id)
        )
        return list(result.scalars().all())
