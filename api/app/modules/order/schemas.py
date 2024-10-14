from pydantic import BaseModel
from datetime import datetime
from app.modules.basket.schemas import BasketOut

class OrderBase(BaseModel):
    payment_method: str

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    created_at: datetime
    basket: BasketOut

    class Config:
        orm_mode = True
