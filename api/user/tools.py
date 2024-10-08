import datetime

from fastapi import HTTPException, Request, Depends
from jose import jwt, ExpiredSignatureError
from passlib.context import CryptContext

from user.rep import UserRepository
from user.schema import uAuth

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_pass(password: str) -> str:
    return password_context.hash(password)


def verify_pass(password: str, hashed_password: str):
    return password_context.verify(password, hashed_password)



async def auth_user(name: str, password: str):
    user = await UserRepository.get_by_username(name=name)
    if not verify_pass(password, user.hashed_password) or user.name is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return user

def create_access_token(user_id: int):
    expired_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    token = jwt.encode({
        'user_id': user_id,
        'exp': expired_at
    }, "secret_key")
    return token

def get_token(request:Request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.cookies.get('access_token')
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token

async def get_current_user(token=Depends(get_token)):
    try:
        decoded_token = jwt.decode(token, "secret_key", algorithms=['HS256'])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек, пожалуйста, авторизуйтесь заново")
    user = await UserRepository.get_by_id(decoded_token['user_id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


