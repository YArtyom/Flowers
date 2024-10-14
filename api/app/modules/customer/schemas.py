from pydantic import BaseModel, EmailStr
from typing import Optional

class CustomerBase(BaseModel):
    name: str
    mail: EmailStr

class CustomerCreate(CustomerBase):
    password: str

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    mail: Optional[EmailStr] = None
    password: Optional[str] = None

class CustomerOut(CustomerBase):
    id: int

    class Config:
        orm_mode = True
class CustomerWithToken(BaseModel):
    access_token: str
    token_type: str
    user: CustomerOut
