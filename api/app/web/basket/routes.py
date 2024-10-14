from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.modules.basket.models import Basket
from app.modules.basket_item.models import BasketItem
from app.modules.product.models import Product
from app.core.security import get_current_customer
from app.common.templates import templates
from sqlalchemy.future import select

router = APIRouter(tags=['basket_pages'])

# Просмотр корзины
@router.get("/basket")
async def view_basket(
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
    if not basket:
        basket = Basket(customer_id=current_customer.id, price=0.0)
        db.add(basket)
        await db.commit()
        await db.refresh(basket)
    return templates.TemplateResponse("basket/view.html", {"request": request, "basket": basket, "user": current_customer})

# Добавление товара в корзину
@router.post("/basket/add")
async def add_to_basket(
    request: Request,
    product_id: int = Form(...),
    quantity: int = Form(...),
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
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if product.quantity < quantity:
        raise HTTPException(status_code=400, detail="Недостаточно товара на складе")
    # Проверяем, есть ли такой товар в корзине
    result = await db.execute(
        select(BasketItem).where(
            BasketItem.basket_id == basket.id,
            BasketItem.product_id == product.id
        )
    )
    basket_item = result.scalars().first()
    if basket_item:
        basket_item.quantity += quantity
        basket_item.price += product.price * quantity
    else:
        basket_item = BasketItem(
            basket_id=basket.id,
            product_id=product.id,
            price=product.price * quantity,
            quantity=quantity
        )
        db.add(basket_item)
    basket.price += product.price * quantity
    db.add(basket)
    await db.commit()
    return RedirectResponse(url="/basket", status_code=status.HTTP_302_FOUND)

# Удаление товара из корзины
@router.post("/basket/remove")
async def remove_from_basket(
    request: Request,
    item_id: int = Form(...),
    current_customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BasketItem).where(BasketItem.id == item_id)
    )
    basket_item = result.scalars().first()
    if not basket_item:
        raise HTTPException(status_code=404, detail="Товар не найден в корзине")
    # Проверяем, что корзина принадлежит текущему пользователю
    if basket_item.basket.customer_id != current_customer.id:
        raise HTTPException(status_code=403, detail="Нет доступа")
    basket_item.basket.price -= basket_item.price
    db.add(basket_item.basket)
    await db.delete(basket_item)
    await db.commit()
    return RedirectResponse(url="/basket", status_code=status.HTTP_302_FOUND)
