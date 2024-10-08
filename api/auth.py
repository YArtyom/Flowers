from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db

from models import User

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate_user(db: AsyncSession, mail: str, password: str):
    result = await db.execute(select(User).filter(User.mail == mail))
    user = result.scalars().first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        mail: str = payload.get("sub")
        if mail is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).filter(User.mail == mail))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user
