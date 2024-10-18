from pydantic import BaseModel, EmailStr


class RegisterData(BaseModel):
    name: str
    email: str
    password: str
class LoginData(BaseModel):
    username: str
    password: str
    email:EmailStr
