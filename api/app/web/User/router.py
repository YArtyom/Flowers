from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.product.models import Basket
from app.user.dependencies import get_current_user
from app.user.models import User

router = APIRouter(
    prefix="/user",
    tags=["UserPages"]
)

templates = Jinja2Templates(directory="app/web/User")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/current-user/page", response_class=HTMLResponse)
async def current_user_page(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return templates.TemplateResponse("index.html", {"request": request, "user": current_user})

@router.get("/logout", response_class=HTMLResponse)
async def logout_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/basket", response_class=HTMLResponse)
async def render_basket(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Рендер корзины для текущего пользователя
    """
    # Запрос корзины пользователя
    query = select(Basket).filter(Basket.user_id == current_user.id, Basket.active_status == True)
    result = await session.execute(query)
    basket = result.scalar_one_or_none()

    # Если корзина не найдена, возвращаем страницу с пустой корзиной
    if not basket:
        return templates.TemplateResponse("index.html", {"request": request, "basket": None})

    # Рендер страницы с корзиной
    return templates.TemplateResponse("index.html", {"request": request, "basket": basket})