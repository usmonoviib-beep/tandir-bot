from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repo import ProductRepository
from app.repositories.category_repo import CategoryRepository
from app.models.product import Product
from app.models.category import Category
from app.utils.logger import logger


class ProductService:
    def __init__(self, session: AsyncSession):
        self.product_repo = ProductRepository(session)
        self.category_repo = CategoryRepository(session)

    async def get_categories(self) -> List[Category]:
        return await self.category_repo.get_active()

    async def get_all_categories(self) -> List[Category]:
        return await self.category_repo.get_all_ordered()

    async def get_category(self, category_id: int) -> Optional[Category]:
        return await self.category_repo.get_by_id(category_id)

    async def get_products_by_category(self, category_id: int) -> List[Product]:
        return await self.product_repo.get_by_category(category_id)

    async def get_all_products(self) -> List[Product]:
        return await self.product_repo.get_all_active()

    async def get_product(self, product_id: int) -> Optional[Product]:
        return await self.product_repo.get_with_category(product_id)

    async def get_all_for_admin(self) -> List[Product]:
        return await self.product_repo.get_all_for_admin()

    async def add_product(
        self,
        category_id: int,
        name: str,
        description: Optional[str] = None,
        price: Optional[float] = None,
        size: Optional[str] = None,
        capacity: Optional[str] = None,
        delivery_info: Optional[str] = None,
    ) -> Product:
        product = await self.product_repo.create(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            size=size,
            capacity=capacity,
            delivery_info=delivery_info,
        )
        logger.info(f"Yangi mahsulot qo'shildi: {product.id} | {name}")
        return product

    async def update_product(self, product_id: int, **kwargs) -> Optional[Product]:
        product = await self.product_repo.update(product_id, **kwargs)
        logger.info(f"Mahsulot yangilandi: {product_id}")
        return product

    async def delete_product(self, product_id: int) -> bool:
        result = await self.product_repo.delete(product_id)
        if result:
            logger.info(f"Mahsulot o'chirildi: {product_id}")
        return result

    async def add_photo(self, product_id: int, file_id: str) -> Optional[Product]:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return None
        photos = product.get_photos()
        photos.append(file_id)
        product.set_photos(photos)
        await self.product_repo.session.flush()
        return product

    async def set_video(self, product_id: int, file_id: str) -> Optional[Product]:
        return await self.product_repo.update(product_id, video_id=file_id)

    async def add_category(self, name: str, emoji: str, slug: str) -> Category:
        return await self.category_repo.create(name=name, emoji=emoji, slug=slug)
