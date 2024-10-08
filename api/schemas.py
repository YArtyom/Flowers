from pydantic import BaseModel, EmailStr
from typing import List, Optional


class CustomerOut(BaseModel):
    id: int
    name: str
    mail: EmailStr

    class Config:
        orm_mode = True

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    description: str
    quantity: int

    class Config:
        orm_mode = True

class BasketItemOut(BaseModel):
    id: int
    product: ProductOut
    quantity: int
    price: float

    class Config:
        orm_mode = True

class BasketOut(BaseModel):
    id: int
    customer_id: int
    price: float
    active_status: bool
    items: List[BasketItemOut] = []

    class Config:
        orm_mode = True
