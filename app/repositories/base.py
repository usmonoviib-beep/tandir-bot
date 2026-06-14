from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import TypeVar, Generic, Type, Optional, List, Any

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs: Any) -> ModelType:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def update(self, obj_id: int, **kwargs: Any) -> Optional[ModelType]:
        await self.session.execute(
            update(self.model).where(self.model.id == obj_id).values(**kwargs)
        )
        await self.session.flush()
        return await self.get_by_id(obj_id)

    async def delete(self, obj_id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == obj_id)
        )
        await self.session.flush()
        return result.rowcount > 0
