from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from app.database import get_db
from app.common.templates import templates
from app.core.security import (
    get_password_hash,
    create_access_token,
    verify_password,
    get_current_customer,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.modules.customer.models import Customer
from sqlalchemy.future import select

router = APIRouter(tags=['customer_pages'])

# Registration page
@router.get("/register/page")
async def register_get(request: Request):
    return templates.TemplateResponse("customer/register.html", {"request": request})

# Registration handler
@router.post("/register")
async def register_post(
    request: Request,
    name: str = Form(...),
    mail: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    hashed_password = get_password_hash(password)
    db_customer = Customer(
        name=name,
        mail=mail,
        hashed_password=hashed_password
    )
    db.add(db_customer)
    try:
        await db.commit()
        await db.refresh(db_customer)
        # Generate access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_customer.mail}, expires_delta=access_token_expires
        )
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    except IntegrityError:
        await db.rollback()
        return templates.TemplateResponse("customer/register.html", {"request": request, "error": "Email or name already registered"})

# Login page
@router.get("/login/page")
async def login_get(request: Request):
    return templates.TemplateResponse("customer/login.html", {"request": request})

# Login handler
@router.post("/login")
async def login_post(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Customer).where(Customer.name == name))
    customer = result.scalars().first()
    if not customer or not verify_password(password, customer.hashed_password):
        return templates.TemplateResponse("customer/login.html", {"request": request, "error": "Incorrect name or password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer.mail}, expires_delta=access_token_expires
    )
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

# Logout
@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# Profile page
@router.get("/profile/page")
async def profile(
    request: Request,
    current_customer = Depends(get_current_customer)
):
    return templates.TemplateResponse("customer/profile.html", {"request": request, "user": current_customer})

# Edit Profile page
@router.get("/profile/edit")
async def edit_profile_get(
    request: Request,
    current_customer = Depends(get_current_customer)
):
    return templates.TemplateResponse("customer/edit_profile.html", {"request": request, "user": current_customer})

# Edit Profile handler
@router.post("/profile/edit")
async def edit_profile_post(
    request: Request,
    name: str = Form(...),
    mail: str = Form(...),
    password: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    current_customer.name = name
    current_customer.mail = mail
    if password:
        current_customer.hashed_password = get_password_hash(password)
    try:
        db.add(current_customer)
        await db.commit()
        return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    except IntegrityError:
        await db.rollback()
        return templates.TemplateResponse("customer/edit_profile.html", {"request": request, "user": current_customer, "error": "Email or name already registered"})
