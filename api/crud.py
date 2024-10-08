from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User, Product, Basket, BasketItem
from schemas import BasketItemOut
from auth import get_password_hash
from fastapi import HTTPException, status
from user.schema import uAuth


# Создание пользователя
async def create_customer(db: AsyncSession, customer: uAuth):
    db_user = User(name=customer.name, mail=customer.mail, hashed_password=customer.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user



# Получение списка продуктов
async def get_products(db: AsyncSession):
    result = await db.execute(select(Product))
    return result.scalars().all()


# CRUD для корзины
async def get_active_basket(db: AsyncSession, customer_id: int):
    result = await db.execute(select(Basket).filter(Basket.customer_id == customer_id, Basket.active_status == True))
    return result.scalar()


async def create_basket(db: AsyncSession, customer_id: int):
    basket = Basket(customer_id=customer_id, price=0, active_status=True)
    db.add(basket)
    await db.commit()
    await db.refresh(basket)
    return basket


async def add_item_to_basket(db: AsyncSession, basket: Basket, product_id: int, quantity: int):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.quantity < quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough quantity in stock")

    basket_item = BasketItem(basket_id=basket.id, product_id=product_id, price=product.price, quantity=quantity)
    db.add(basket_item)
    basket.price += product.price * quantity
    await db.commit()
    await db.refresh(basket_item)

    return basket_item


async def get_basket_items(db: AsyncSession, basket_id: int):
    result = await db.execute(select(BasketItem).filter(BasketItem.basket_id == basket_id))
    return result.scalars().all()


async def remove_item_from_basket(db: AsyncSession, basket_item_id: int):
    result = await db.execute(select(BasketItem).filter(BasketItem.id == basket_item_id))
    item = result.scalar()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    basket = item.basket
    basket.price -= item.price * item.quantity

    await db.delete(item)
    await db.commit()

    return item
