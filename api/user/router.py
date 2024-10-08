from datetime import timedelta

from fastapi import APIRouter, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth import ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash, authenticate_user
from crud import create_customer
from database import get_db
from user.rep import UserRepository
from user.schema import uAuth, Token
from user.tools import get_hashed_pass, verify_pass, auth_user, create_access_token, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post('/register')
async def register_user(user_data: uAuth):
    user = await UserRepository.create(name=user_data.name,mail=user_data.mail , hashed_password=get_hashed_pass(user_data.password))
    return {
            "message": get_hashed_pass(user_data.password),
            "is_verified": verify_pass(user_data.password, get_hashed_pass(user_data.password)),
    }

@router.post("/login")
async def login(data: uAuth, response: Response):
    user = await auth_user(data.name, data.password)
    token = create_access_token(user.id)
    response.set_cookie("access_token", token)
    return {
        "message": f"User {user.name} logged in successfully",
    }

@router.get("/current_user")
async def current_user(user=Depends(get_current_user)):
    return user