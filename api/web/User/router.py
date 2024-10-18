import logging

from fastapi import APIRouter, Depends, Request, Form, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette import status
from starlette.status import HTTP_302_FOUND
from app.database import get_session
from app.user.repository import UserRepository
from app.user.auth import create_access_token, verify_password, get_hashed_password
from app.user.dependencies import get_current_user
from app.user.models import User
from app.user.schemas import SRUser, SCUser, SAuth
from app.web.User.Schemas import LoginData, RegisterData

router = APIRouter(
    prefix="/user",
    tags=["UsersPage"],
)

templates = Jinja2Templates(directory="app/web/User")

# GET метод для отображения страницы регистрации
@router.get("/register")
async def get_register_page(request: Request):
    """
    Отображение страницы регистрации
    """
    return templates.TemplateResponse("register.html", {"request": request})
logger = logging.getLogger(__name__)

@router.post("/register/func", response_model=SRUser, status_code=status.HTTP_201_CREATED)
async def register_user(data: SCUser, session: AsyncSession = Depends(get_session)):
    """
    Регистрация аккаунта
    """
    existing_user = await UserRepository.get_by(email=data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_hashed_password(data.password)
    user = await UserRepository.create(
        session=session,
        name=data.name,
        email=data.email,
        hashed_password=hashed_password,
    )
    return SRUser.from_orm(user)

# GET метод для отображения страницы входа
@router.get("/login")
async def get_login_page(request: Request):
    """
    Отображение страницы входа
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login/func")
async def login(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Вход в аккаунт
    """
    user = await UserRepository.get_by(email=email)
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect email or password"})

    token = create_access_token(user.id)
    response.set_cookie(key="token", value=token, httponly=True, secure=True, samesite="lax")
    return RedirectResponse("/user/profile", status_code=HTTP_302_FOUND)

# Профиль текущего пользователя
@router.get("/profile")
async def get_user_profile(request: Request, current_user: User = Depends(get_current_user)):
    """
    Отображение профиля текущего пользователя
    """
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

# Редактирование пользователя с использованием BaseRepository
@router.post("/edit")
async def update_user(
    name: str = Form(None),
    email: str = Form(None),
    password: str = Form(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Обновление данных пользователя
    """
    user_update = {"name": name, "email": email}
    if password:
        user_update["hashed_password"] = get_hashed_password(password)
    await UserRepository.update(current_user.id, user_update)
    return RedirectResponse("/user/profile", status_code=HTTP_302_FOUND)

# Удаление пользователя с использованием BaseRepository
@router.post("/delete")
async def delete_user(current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """
    Удаление аккаунта текущего пользователя
    """
    await UserRepository.destroy(current_user.id, session)
    return RedirectResponse("/", status_code=HTTP_302_FOUND)