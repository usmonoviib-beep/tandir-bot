from sqlalchemy import String, Integer, ForeignKey, BigInteger, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

from .base import Base, TimestampMixin


class OrderStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    customer_name: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        default=OrderStatus.NEW.value,
        nullable=False
    )
    admin_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="orders")
    product: Mapped["Product"] = relationship("Product", back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.status}>"
