from pydantic import BaseModel, EmailStr


class SGUser(BaseModel):
    name: str
    email: EmailStr


class SCUser(SGUser):
    password: str


class SUUser(BaseModel):
    name: str | None
    email: EmailStr | None
    password: str


class SRUser(SGUser):
    id: int

    class Config:
        from_attributes = True


class SAuth(BaseModel):
    username: str
    password: str
    email: EmailStr

