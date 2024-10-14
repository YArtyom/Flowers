from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from . import models, schemas
from app.core.security import get_current_customer
from app.modules.basket.models import Basket

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("/", response_model=schemas.OrderOut)
async def create_order(
    order_create: schemas.OrderCreate,
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    # Получаем активную корзину
    result = await db.execute(
        select(Basket).where(
            Basket.customer_id == current_customer.id,
            Basket.active_status == True
        )
    )
    basket = result.scalars().first()
    if not basket:
        raise HTTPException(status_code=404, detail="No active basket found")

    # Создаем заказ
    order = models.Order(
        customer_id=current_customer.id,
        basket_id=basket.id,
        payment_method=order_create.payment_method
    )
    basket.active_status = False
    db.add(order)
    db.add(basket)
    await db.commit()
    await db.refresh(order)
    return order
