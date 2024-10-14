from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.modules.basket_item.schemas import BasketItemOut

class BasketBase(BaseModel):
    created_at: datetime
    price: float
    active_status: bool

class BasketCreate(BaseModel):
    pass

class BasketUpdate(BaseModel):
    active_status: Optional[bool] = None

class BasketOut(BasketBase):
    id: int
    items: List[BasketItemOut] = []

    class Config:
        orm_mode = True
