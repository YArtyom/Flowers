from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
KEY = settings.KEY
ALGORITHM = settings.ALGORITHM
TOKEN_EXPIRE = settings.TOKEN_EXPIRE


def get_hashed_password(password: str):
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return password_context.verify(password, hashed_password)


def create_access_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE)
    to_encode = {"user_id": user_id, "exp": expire}
    return jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
