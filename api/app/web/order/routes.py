
from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.modules.order.models import Order
from app.modules.basket.models import Basket
from app.modules.basket_item.models import BasketItem
from app.modules.product.models import Product
from app.core.security import get_current_customer
from app.common.templates import templates
from sqlalchemy.future import select
from datetime import datetime

router = APIRouter(tags=['order_pages'])

# Оформление заказа
@router.get("/basket/checkout")
async def checkout_get(
    request: Request,
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Basket).where(
            Basket.customer_id == current_customer.id,
            Basket.active_status == True
        )
    )
    basket = result.scalars().first()
    if not basket or not basket.items:
        return RedirectResponse(url="/basket", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("basket/checkout.html", {"request": request, "basket": basket, "user": current_customer})

# Обработка оформления заказа
@router.post("/orders/create")
async def create_order(
    request: Request,
    payment_method: str = Form(...),
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Basket).where(
            Basket.customer_id == current_customer.id,
            Basket.active_status == True
        )
    )
    basket = result.scalars().first()
    if not basket or not basket.items:
        raise HTTPException(status_code=400, detail="Корзина пуста")
    # Создаем заказ
    order = Order(
        customer_id=current_customer.id,
        date=datetime.utcnow(),
        price=basket.price,
        payment_method=payment_method
    )
    db.add(order)
    # Обновляем количество товаров на складе
    for item in basket.items:
        result = await db.execute(select(Product).where(Product.id == item.product_id))
        product = result.scalars().first()
        if product.quantity < item.quantity:
            raise HTTPException(status_code=400, detail=f"Недостаточно товара {product.name} на складе")
        product.quantity -= item.quantity
        db.add(product)
    # Деактивируем корзину
    basket.active_status = False
    db.add(basket)
    await db.commit()
    return RedirectResponse(url="/orders", status_code=status.HTTP_302_FOUND)

# Просмотр заказов пользователя
@router.get("/orders")
async def list_orders(
    request: Request,
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.customer_id == current_customer.id)
    )
    orders = result.scalars().all()
    return templates.TemplateResponse("order/list.html", {"request": request, "orders": orders, "user": current_customer})
