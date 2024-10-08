from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from main import get_current_user
from database import get_db
from crud import get_active_basket, get_basket_items

router = APIRouter()
templates = Jinja2Templates(directory="template")


@router.get("/basket")
async def get_basket_page(request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(get_current_user)):
    if not token:
        return templates.TemplateResponse("not_registered.html", {"request": request})

    basket = await get_active_basket(db, token.id)
    items = await get_basket_items(db, basket.id) if basket else []

    return templates.TemplateResponse("basket.html", {"request": request, "basket": basket, "items": items})
