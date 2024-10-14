from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from . import models, schemas
from typing import List

from ...core.security import get_current_customer

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


# Создание продукта (требуется аутентификация администратора)
@router.post("/", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: schemas.ProductCreate,
        db: AsyncSession = Depends(get_db),
        current_customer=Depends(get_current_customer)
):
    # Добавьте проверку прав администратора
    db_product = models.Product(
        name=product.name,
        price=product.price,
        description=product.description,
        quantity=product.quantity
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


# Получение списка продуктов
@router.get("/", response_model=List[schemas.ProductOut])
async def read_products(
        skip: int = 0,
        limit: int = 10,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Product).offset(skip).limit(limit))
    products = result.scalars().all()
    return products


# Получение продукта по ID
@router.get("/{product_id}", response_model=schemas.ProductOut)
async def read_product(
        product_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalars().first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# Обновление продукта по ID (требуется аутентификация администратора)
@router.put("/{product_id}", response_model=schemas.ProductOut)
async def update_product(
        product_id: int,
        product_update: schemas.ProductUpdate,
        db: AsyncSession = Depends(get_db),
        current_customer=Depends(get_current_customer)
):
    # Добавьте проверку прав администратора
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalars().first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_update.name:
        product.name = product_update.name
    if product_update.price is not None:
        product.price = product_update.price
    if product_update.description:
        product.description = product_update.description
    if product_update.quantity is not None:
        product.quantity = product_update.quantity
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


# Удаление продукта по ID (требуется аутентификация администратора)
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
        product_id: int,
        db: AsyncSession = Depends(get_db),
        current_customer=Depends(get_current_customer)
):
    # Добавьте проверку прав администратора
    result = await db.execute(select(models.Product).where(models.Product.id == product_id))
    product = result.scalars().first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return
