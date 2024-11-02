from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.user.auth import get_hashed_password, verify_password, create_access_token
from app.user.dependencies import get_current_user
from app.user.models import User
from app.user.repository import UserRepository
from app.user.schemas import SRUser, SCUser, SAuth, SUUserUpdate, CreateUser

router = APIRouter(
    prefix="/user",
    tags=["Users"],
)


@router.post("/register", response_model=SRUser, status_code=status.HTTP_201_CREATED)
async def register_user(data: CreateUser, session: AsyncSession = Depends(get_session)):
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


@router.post("/login")
async def login(data: SAuth, response: Response):
    """
    Вход в свой аккаунт
    """
    user = await UserRepository.get_by(email=data.email)
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(user.id)
    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"message": "Successfully logged in", "auth_token": token}


@router.get("/current-user", response_model=SRUser)
async def get_current_user_route(current_user: User = Depends(get_current_user)):
    """
    Получение текущего пользователя
    """
    return current_user


@router.put("/update_user/{user_id}", response_model=SRUser)
async def update_user(
    user_id: int,
    user_update: SUUserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Обновление данных пользователя
    """
    # Проверка, чтобы пользователь мог обновить только свои данные
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden to update another user's data"
        )

    # Получение пользователя по id
    query = select(User).filter(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Обновляем только те поля, которые указаны в запросе
    user_data = user_update.dict(exclude_unset=True)
    if "password" in user_data:
        user_data["hashed_password"] = get_hashed_password(user_data.pop("password"))

    for key, value in user_data.items():
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return SRUser.from_orm(user)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Автоматически удаляет текущего пользователя
    """
    query = select(User).filter(User.id == current_user.id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already deleted"
        )

    await session.delete(user)
    await session.commit()

    return {
        "message": "Successfully deleted"
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Выход с аккаунта текущего пользователя, удаление cookie с токеном.
    """
    response.delete_cookie("token")
    return {
        "message": "User logged out successfully"
    }
