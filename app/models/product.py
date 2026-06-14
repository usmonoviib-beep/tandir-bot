from sqlalchemy import String, Text, Float, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from .base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capacity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    delivery_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Media - JSON list of file_id lar
    photos: Mapped[Optional[str]] = mapped_column(Text, nullable=True)   # JSON list
    video_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relations
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}>"

    def get_photos(self) -> List[str]:
        import json
        if not self.photos:
            return []
        try:
            return json.loads(self.photos)
        except Exception:
            return []

    def set_photos(self, photo_ids: List[str]) -> None:
        import json
        self.photos = json.dumps(photo_ids)
