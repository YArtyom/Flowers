from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from . import models, schemas
from app.core.security import (
    get_password_hash,
    create_access_token,
    get_current_customer,
    authenticate_customer,
    ACCESS_TOKEN_EXPIRE_MINUTES, OAuth2PasswordRequestFormName, authenticate_customer_by_name,
)
from typing import List
from datetime import timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)

@router.post("/", response_model=schemas.CustomerWithToken, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: schemas.CustomerCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = get_password_hash(customer.password)
    db_customer = models.Customer(
        name=customer.name,
        mail=customer.mail,
        hashed_password=hashed_password
    )
    db.add(db_customer)
    try:
        await db.commit()
        await db.refresh(db_customer)
        # Генерируем access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_customer.name}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "user": db_customer}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


# Получение токена для аутентификации
# app/modules/customer/routes.py

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestFormName = Depends(),
    db: AsyncSession = Depends(get_db)
):
    customer = await authenticate_customer_by_name(form_data.name, form_data.password, db)
    if not customer:
        raise HTTPException(status_code=400, detail="Incorrect name or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Получение текущего аутентифицированного пользователя
@router.get("/me/get/", response_model=schemas.CustomerOut)
async def read_current_customer(current_customer: models.Customer = Depends(get_current_customer)):
    return current_customer

# Обновление текущего пользователя
@router.put("/me/update", response_model=schemas.CustomerOut)
async def update_customer(
    customer_update: schemas.CustomerUpdate,
    current_customer: models.Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    if customer_update.name:
        current_customer.name = customer_update.name
    if customer_update.mail:
        current_customer.mail = customer_update.mail
    if customer_update.password:
        current_customer.hashed_password = get_password_hash(customer_update.password)
    try:
        db.add(current_customer)
        await db.commit()
        await db.refresh(current_customer)
        return current_customer
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

# Удаление текущего пользователя
@router.delete("/me/delete/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    current_customer: models.Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    await db.delete(current_customer)
    await db.commit()
    return

# ***Новые CRUD операции для пользователя***

# Получение списка всех пользователей (требуется аутентификация администратора)
@router.get("/", response_model=List[schemas.CustomerOut])
async def read_customers(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)
):
    # Добавьте проверку прав администратора, если необходимо
    result = await db.execute(select(models.Customer).offset(skip).limit(limit))
    customers = result.scalars().all()
    return customers

# Получение пользователя по ID (требуется аутентификация администратора)
@router.get("/{customer_id}", response_model=schemas.CustomerOut)
async def read_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)
):
    # Добавьте проверку прав администратора, если необходимо
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Обновление пользователя по ID (требуется аутентификация администратора)
@router.put("/{customer_id}", response_model=schemas.CustomerOut)
async def update_customer_by_id(
    customer_id: int,
    customer_update: schemas.CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)
):
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer_update.name:
        customer.name = customer_update.name
    if customer_update.mail:
        customer.mail = customer_update.mail
    if customer_update.password:
        customer.hashed_password = get_password_hash(customer_update.password)
    try:
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

# Удаление пользователя по ID (требуется аутентификация администратора)
@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_by_id(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_customer: models.Customer = Depends(get_current_customer)
):
    # Добавьте проверку прав администратора, если необходимо
    result = await db.execute(select(models.Customer).where(models.Customer.id == customer_id))
    customer = result.scalars().first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await db.delete(customer)
    await db.commit()
    return
