from datetime import datetime

from pydantic import BaseModel
from typing import List

from app.user.schemas import SRUser


class SGProduct(BaseModel):
    name: str
    price: float
    description: str
    quantity: int
    product_image: str


class SCProduct(SGProduct):
    pass  # Все поля обязательны при создании
    # Можно и убрать, но и веса особого не имеет, так что можно оставить


class SUProduct(BaseModel):
    name: str | None
    price: float | None
    description: str | None
    quantity: int | None
    product_image: str | None


class SRProduct(SGProduct):
    id: int

    class Config:
        from_attributes = True

# Product
# ---------------------------------------------------------------------------------------------------------------------

class BasketItemUpdate(BaseModel):
    quantity: int
    basket_id: int
    class Config:
        from_attributes = True
class SGBasketItem(BaseModel):
    price: float
    quantity: int


class SCBasketItem(SGBasketItem):
    product_id: int
    basket_id: int


class SUBasketItem(BaseModel):
    price: float | None
    quantity: int | None


class SRBasketItem(SGBasketItem):
    id: int
    product: SRProduct

    class Config:
        from_attributes = True

# BasketItem
# ---------------------------------------------------------------------------------------------------------------------


class SGBasket(BaseModel):
    total_price: float
    active_status: bool


class SCBasket(SGBasket):
    user_id: int


class SUBasket(BaseModel):
    total_price: float | None
    active_status: bool | None


class SRBasket(SGBasket):
    id: int
    created_at: datetime
    basket_items: List[SRBasketItem] = []
    user: SRUser

    class Config:
        from_attributes = True

# Basket
# ---------------------------------------------------------------------------------------------------------------------
