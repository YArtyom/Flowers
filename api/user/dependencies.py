from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError, ExpiredSignatureError
from app.user.repository import UserRepository
from app.config import settings

KEY = settings.KEY
ALGORITHM = settings.ALGORITHM


def get_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, _, token = auth_header.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    else:
        token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await UserRepository.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
