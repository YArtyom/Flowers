from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from crud import create_customer
from main import authenticate_user, create_access_token
from database import get_db
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="template")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.get("/register")
def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user(request: Request, name: str = Form(...), email: str = Form(...),
                        password: str = Form(...), db: AsyncSession = Depends(get_db)):
    customer_data = {
        "name": name,
        "mail": email,
        "password": password
    }
    await create_customer(db, customer_data)
    return RedirectResponse("/login", status_code=302)
@router.get("/login")
def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_user(request: Request, email: str = Form(...), password: str = Form(...),
                     db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.mail}, expires_delta=access_token_expires)
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response
