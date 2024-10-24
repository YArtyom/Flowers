from datetime import datetime
from typing import List

from sqlalchemy import Integer, String, Float, Text, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Product(Base):

    name: Mapped[str] = mapped_column(String, index=True)
    price: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    product_image: Mapped[str] = mapped_column(String)

    # One to many
    basket_items: Mapped[List["BasketItem"]] = relationship(
        "BasketItem", back_populates="product", passive_deletes=True
    )


class Basket(Base):

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    total_price: Mapped[float] = mapped_column(Float)
    active_status: Mapped[bool] = mapped_column(Boolean, default=True)

    # Many to one
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"),
    )
    user: Mapped["User"] = relationship("User", back_populates="baskets")


    # One to many
    basket_items: Mapped[List["BasketItem"]] = relationship(
        "BasketItem", back_populates="basket", cascade="all, delete-orphan"
    )


class BasketItem(Base):

    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer)

    # Many to one
    basket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("baskets.id", ondelete="CASCADE"), nullable=False
    )
    basket: Mapped["Basket"] = relationship("Basket", back_populates="basket_items")

    # Many to one
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="basket_items", passive_deletes=True
    )