from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from . import models, schemas
from app.core.security import get_current_customer
from app.modules.basket.models import Basket
from app.modules.product.models import Product

router = APIRouter(
    prefix="/basket-items",
    tags=["basket-items"],
)

@router.post("/", response_model=schemas.BasketItemOut)
async def add_item_to_basket(
    item: schemas.BasketItemCreate,
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
        basket = Basket(customer_id=current_customer.id, price=0.0)
        db.add(basket)
        await db.commit()
        await db.refresh(basket)

    # Получаем продукт
    result = await db.execute(select(Product).where(Product.id == item.product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.quantity < item.quantity:
        raise HTTPException(status_code=400, detail="Not enough product in stock")

    # Добавляем товар в корзину
    basket_item = models.BasketItem(
        basket_id=basket.id,
        product_id=product.id,
        price=product.price * item.quantity,
        quantity=item.quantity
    )
    basket.price += basket_item.price
    db.add(basket_item)
    db.add(basket)
    await db.commit()
    await db.refresh(basket_item)
    return basket_item
