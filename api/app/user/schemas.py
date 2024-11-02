from pydantic import BaseModel, EmailStr
from typing_extensions import Optional


class SGUser(BaseModel):
    name: str
    email: EmailStr

class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str

class SCUser(SGUser):
    password: str


class SUUserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]

    class Config:
        orm_mode = True


class SRUser(SGUser):
    id: int

    class Config:
        from_attributes = True


class SAuth(BaseModel):
    username: str
    password: str
    email: EmailStr
