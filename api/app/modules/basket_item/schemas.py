from pydantic import BaseModel
from typing import Optional
from app.modules.product.schemas import ProductOut

class BasketItemBase(BaseModel):
    price: float
    quantity: int

class BasketItemCreate(BaseModel):
    product_id: int
    quantity: int

class BasketItemUpdate(BaseModel):
    quantity: Optional[int] = None

class BasketItemOut(BasketItemBase):
    id: int
    product: ProductOut

    class Config:
        orm_mode = True
