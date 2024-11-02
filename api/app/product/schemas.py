import base64
from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

from app.user.schemas import SRUser


class SGProduct(BaseModel):
    name: str
    price: float
    description: str
    quantity: int
    product_image: bytes  # Данные изображения сохраняются и передаются как bytes



class SCProduct(BaseModel):
    name: str
    description: str
    price: float
    product_image: bytes  # Изменено на bytes для хранения бинарных данных


class SUProduct(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    product_image: Optional[bytes] = None  # Оставляем как bytes, чтобы избежать декодирования в строку

    class Config:
        from_attributes = True


class SRProduct(SGProduct):
    id: int

    class Config:
        from_attributes = True
class SRProductList(BaseModel):
    id: int
    name: str
    price: float
    description: str
    quantity: int
    product_image: bytes | None = None  # Поле для изображения в формате Base64

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, product):
        """
        Метод для преобразования модели в схему с изображением в формате Base64.
        """
        product_data = cls.from_orm(product)
        if product.product_image:
            # Кодирование изображения в Base64 и преобразование в строку
            product_data.product_image = base64.b64encode(product.product_image).decode('utf-8')
        return product_data
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
