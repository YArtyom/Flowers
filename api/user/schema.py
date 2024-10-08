from pydantic import BaseModel, EmailStr


class uAuth(BaseModel):
    name: str
    mail: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
