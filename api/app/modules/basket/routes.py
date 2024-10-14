from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from . import models, schemas
from app.core.security import get_current_customer
from typing import List

router = APIRouter(
    prefix="/baskets",
    tags=["baskets"],
)

# Создание новой корзины
@router.post("/", response_model=schemas.BasketOut, status_code=status.HTTP_201_CREATED)
async def create_basket(
    basket_create: schemas.BasketCreate,
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    basket = models.Basket(
        customer_id=current_customer.id,
        price=0.0,
        active_status=basket_create.active_status
    )
    db.add(basket)
    await db.commit()
    await db.refresh(basket)
    return basket

# Получение списка всех корзин (требуется аутентификация администратора)
@router.get("/", response_model=List[schemas.BasketOut])
async def read_baskets(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    # Добавьте проверку прав администратора, если необходимо
    result = await db.execute(select(models.Basket).offset(skip).limit(limit))
    baskets = result.scalars().all()
    return baskets

# Получение корзины по ID
@router.get("/{basket_id}", response_model=schemas.BasketOut)
async def read_basket(
    basket_id: int,
    db: AsyncSession = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    result = await db.execute(select(models.Basket).where(models.Basket.id == basket_id))
    basket = result.scalars().first()
    if not basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    # Проверяем, имеет ли пользователь доступ к этой корзине
    if basket.customer_id != current_customer.id:
        # Добавьте проверку прав администратора, если необходимо
        raise HTTPException(status_code=403, detail="Not authorized to access this basket")
    return basket

# Обновление корзины по ID
@router.put("/{basket_id}", response_model=schemas.BasketOut)
async def update_basket(
    basket_id: int,
    basket_update: schemas.BasketUpdate,
    db: AsyncSession = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    result = await db.execute(select(models.Basket).where(models.Basket.id == basket_id))
    basket = result.scalars().first()
    if not basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    if basket.customer_id != current_customer.id:
        # Добавьте проверку прав администратора, если необходимо
        raise HTTPException(status_code=403, detail="Not authorized to update this basket")
    if basket_update.active_status is not None:
        basket.active_status = basket_update.active_status
    db.add(basket)
    await db.commit()
    await db.refresh(basket)
    return basket

# Удаление корзины по ID
@router.delete("/{basket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_basket(
    basket_id: int,
    db: AsyncSession = Depends(get_db),
    current_customer = Depends(get_current_customer)
):
    result = await db.execute(select(models.Basket).where(models.Basket.id == basket_id))
    basket = result.scalars().first()
    if not basket:
        raise HTTPException(status_code=404, detail="Basket not found")
    if basket.customer_id != current_customer.id:
        # Добавьте проверку прав администратора, если необходимо
        raise HTTPException(status_code=403, detail="Not authorized to delete this basket")
    await db.delete(basket)
    await db.commit()
    return

# Получение активной корзины текущего пользователя
@router.get("/active", response_model=schemas.BasketOut)
async def get_active_basket(
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Basket).where(
            models.Basket.customer_id == current_customer.id,
            models.Basket.active_status == True
        )
    )
    basket = result.scalars().first()
    if not basket:
        # Создаем новую корзину, если активная не найдена
        basket = models.Basket(customer_id=current_customer.id, price=0.0)
        db.add(basket)
        await db.commit()
        await db.refresh(basket)
    return basket
