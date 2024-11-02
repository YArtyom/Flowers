from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.product.models import Basket, BasketItem
from app.product.repository import BasketRepository, ProductRepository, BasketItemRepository
from app.product.schemas import SRBasket, SCBasket, SUBasket, SRBasketItem, SCBasketItem, BasketItemUpdate
from app.repository.schemas import SBaseListResponse
from app.user.dependencies import get_current_user

import base64

router = APIRouter(
    prefix="/basket",
    tags=["Basket"],
)


@router.get("/user-basket-id", status_code=status.HTTP_200_OK)
async def get_user_basket_id(
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Возвращает ID корзины для текущего пользователя или создает новую, если она не существует.
    """
    query = select(Basket).filter(Basket.user_id == current_user.id, Basket.active_status == True)
    result = await session.execute(query)
    basket = result.scalar_one_or_none()

    if basket:
        return {"basket_id": basket.id}

    new_basket = await BasketRepository.create(
        session=session,
        user_id=current_user.id,
        active_status=True,
        total_price=0.0,
        created_at=datetime.utcnow()
    )
    await session.commit()

    return {"basket_id": new_basket.id}

@router.post("/", response_model=SRBasket, status_code=status.HTTP_201_CREATED)
async def get_or_create_basket(
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Получение или создание новой корзины для текущего пользователя.
    """
    query = select(Basket).options(
        selectinload(Basket.basket_items).selectinload(BasketItem.product),
        selectinload(Basket.user)
    ).filter(Basket.user_id == current_user.id, Basket.active_status == True)
    result = await session.execute(query)
    basket = result.scalar_one_or_none()

    if basket:
        # Удаляем элементы корзины, у которых отсутствует связанный продукт
        basket.basket_items = [item for item in basket.basket_items if item.product is not None]

        # Обрабатываем изображения продуктов перед возвратом ответа
        for item in basket.basket_items:
            if item.product and item.product.product_image:
                item.product.product_image = base64.b64encode(item.product.product_image).decode('utf-8')
        return SRBasket.from_orm(basket)

    new_basket = await BasketRepository.create(
        session=session,
        user_id=current_user.id,
        active_status=True,
        total_price=0.0,
        created_at=datetime.utcnow()
    )
    await session.commit()

    query = select(Basket).options(
        selectinload(Basket.basket_items).selectinload(BasketItem.product),
        selectinload(Basket.user)
    ).filter(Basket.id == new_basket.id)
    result = await session.execute(query)
    basket = result.scalar_one()
    basket.basket_items = [item for item in basket.basket_items if item.product is not None]

    # Обрабатываем изображения продуктов перед возвратом ответа
    for item in basket.basket_items:
        if item.product and item.product.product_image:
            item.product.product_image = base64.b64encode(item.product.product_image).decode('utf-8')

    return SRBasket.from_orm(basket)



@router.post("/items", response_model=SRBasketItem, status_code=status.HTTP_201_CREATED)
async def add_or_update_item_in_basket(
    item_data: SCBasketItem,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Добавление товара в корзину текущего пользователя или обновление количества.
    """
    query = select(Basket).filter(Basket.user_id == current_user.id, Basket.active_status == True)
    result = await session.execute(query)
    basket = result.scalar_one_or_none()

    if not basket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active basket not found"
        )

    query = select(BasketItem).filter(BasketItem.basket_id == basket.id, BasketItem.product_id == item_data.product_id)
    result = await session.execute(query)
    basket_item = result.scalar_one_or_none()

    product = await ProductRepository.get_by_id(item_data.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if basket_item:
        basket_item.quantity += item_data.quantity
        basket.total_price += product.price * item_data.quantity
    else:
        basket_item = await BasketItemRepository.create(
            session=session,
            basket_id=basket.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            price=product.price
        )
        basket.total_price += product.price * item_data.quantity

    await session.commit()

    query = select(BasketItem).options(selectinload(BasketItem.product)).filter(BasketItem.id == basket_item.id)
    result = await session.execute(query)
    updated_basket_item = result.scalar_one()

    basket_item_data = SRBasketItem.from_orm(updated_basket_item).dict()
    if updated_basket_item.product and updated_basket_item.product.product_image:
        basket_item_data['product']['product_image'] = base64.b64encode(
            updated_basket_item.product.product_image
        ).decode('utf-8')

    return basket_item_data


@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def remove_item_from_basket(
    item_id: int,
    quantity: int = 1,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Поштучное удаление товара из корзины текущего пользователя.
    """
    query = select(Basket).filter(Basket.user_id == current_user.id, Basket.active_status == True)
    result = await session.execute(query)
    basket = result.scalar_one_or_none()

    if not basket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active basket not found"
        )

    item = await BasketItemRepository.get_by_id(item_id)
    if not item or item.basket_id != basket.id or item.quantity < quantity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in this basket or insufficient quantity"
        )

    basket.total_price -= item.price * quantity
    if item.quantity > quantity:
        item.quantity -= quantity
        session.add(item)
        await session.commit()
        await session.refresh(item)
    else:
        await BasketItemRepository.destroy(item_id, session)

    await session.commit()

    return {
        "message": "Item quantity updated successfully" if item.quantity > quantity else "Item removed from basket successfully"
    }


@router.put("/checkout", status_code=status.HTTP_200_OK)
async def checkout_basket(
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Изменение статуса корзины на неактивный (оформление заказа).
    """
    query = select(Basket).options(selectinload(Basket.basket_items)).filter(
        Basket.user_id == current_user.id, Basket.active_status == True
    )
    result = await session.execute(query)
    basket = result.scalar_one_or_none()

    if not basket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active basket not found"
        )

    for item in basket.basket_items:
        product = await ProductRepository.get_by_id(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )

        product.quantity -= item.quantity
        session.add(product)

    basket.active_status = False
    await session.commit()

    return {
        "message": "Basket checked out successfully"
    }

#
# @router.put("/items/{item_id}", response_model=SRBasketItem, status_code=status.HTTP_200_OK)
# async def updBasItem(
#     item_id: int,
#     item_data: BasketItemUpdate,
#     session: AsyncSession = Depends(get_session),
#     current_user: str = Depends(get_current_user)
# ):
#     """
#     Обновление количества товара в корзине с указанием корзины (basket_id).
#     """
#     query = select(Basket).filter(Basket.id == item_data.basket_id, Basket.user_id == current_user.id, Basket.active_status == True)
#     result = await session.execute(query)
#     basket = result.scalar_one_or_none()
#
#     if not basket:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
#
#     query = select(BasketItem).filter(BasketItem.id == item_id, BasketItem.basket_id == basket.id)
#     result = await session.execute(query)
#     basket_item = result.scalar_one_or_none()
#
#     if not basket_item:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар в корзине не найден")
#
#     basket_item.quantity = item_data.quantity
#     basket.total_price = sum(item.price * item.quantity for item in basket.basket_items)
#
#     await session.commit()
#
#     updated_basket_item_data = SRBasketItem.from_orm(basket_item).dict()
#     if basket_item.product and basket_item.product.product_image:
#         updated_basket_item_data['product']['product_image'] = base64.b64encode(
#             basket_item.product.product_image
#         ).decode('utf-8')
#
#     return updated_basket_item_data
