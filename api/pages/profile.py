from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from main import get_current_user
from database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="template")

@router.get("/profile")
async def get_profile_page(request: Request, db: AsyncSession = Depends(get_db), token: str = Depends(get_current_user)):
    if not token:
        return templates.TemplateResponse("not_registered.html", {"request": request})
    return templates.TemplateResponse("profile.html", {"request": request, "user": token})
