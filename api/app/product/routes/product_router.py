import base64
import io
from typing import Optional, List

from PIL import Image
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Request, status, HTTPException, UploadFile, File, Response, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.product.models import Product
from app.product.repository import ProductRepository
from app.product.schemas import SCProduct, SRProduct, SUProduct, SRProductList
from app.repository.schemas import SBaseListResponse

from app.user.dependencies import get_current_user

router = APIRouter(
    prefix="/product",
    tags=["Product"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
        name: str,
        description: str,
        price: float,
        quantity: int,
        product_image: UploadFile = File(...),
        session: AsyncSession = Depends(get_session)
):
    # Чтение изображения как бинарных данных
    image_data = await product_image.read()

    if not isinstance(image_data, bytes):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Данные изображения не являются бинарными"
        )

    try:
        new_product = Product(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            product_image=image_data
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)

        return {
            "id": new_product.id,
            "name": new_product.name,
            "description": new_product.description,
            "price": new_product.price,
            "quantity": new_product.quantity
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании продукта: {str(e)}"
        )

@router.get("/", response_model=SBaseListResponse[SRProductList])
async def get_all_products(
    page: int = 1,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
):
    products = await ProductRepository.paginate(page=page, limit=limit)
    total = await ProductRepository.count()

    products_data = []
    for product in products:
        product_dict = SRProductList.from_orm(product).dict(exclude={"product_image"})
        products_data.append(product_dict)

    return {
        "data": products_data,
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/{product_id}/image")
async def get_product_image(
        product_id: int,
        session: AsyncSession = Depends(get_session)
):
    product = await ProductRepository.get_by_id(product_id)
    if not product or not product.product_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    return StreamingResponse(io.BytesIO(product.product_image), media_type="image/jpeg")

@router.get("/{product_id}", response_model=SRProduct)
async def get_product(
        product_id: int,
        session: AsyncSession = Depends(get_session)
):
    product = await ProductRepository.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    product_data = SRProduct.from_orm(product).dict()
    if product.product_image:
        product_data["product_image"] = base64.b64encode(product.product_image).decode('utf-8')

    return product_data


@router.put("/{product_id}", response_model=SRProduct, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    quantity: Optional[int] = Form(None),
    product_image: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    """
    Обновление информации о продукте, включая сравнение с текущими данными для внесения только измененных полей.
    """
    # Получаем текущие данные продукта
    existing_product = await ProductRepository.get_by_id(product_id)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    # Формируем данные для обновления, добавляя только измененные поля
    update_data = {}
    if name is not None and name != existing_product.name:
        update_data["name"] = name

    if description is not None and description != existing_product.description:
        update_data["description"] = description

    if price is not None and price != existing_product.price:
        update_data["price"] = price

    if quantity is not None and quantity != existing_product.quantity:
        update_data["quantity"] = quantity

    # Обработка изображения, если оно было загружено
    if product_image is not None:
        image_data = await product_image.read()
        if isinstance(image_data, bytes):
            update_data["product_image"] = image_data  # Сохраняем как бинарные данные
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid image format"
            )

    # Проверка, есть ли изменения
    if not update_data:
        return SRProduct.from_orm(existing_product)

    updated_product = await ProductRepository.update(product_id, update_data)

    # Обработка изображения для ответа (кодирование в Base64)
    product_data = SRProduct.from_orm(updated_product).dict()
    if updated_product.product_image:
        product_data["product_image"] = base64.b64encode(updated_product.product_image).decode('utf-8')

    return product_data



@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    delete_result = await ProductRepository.destroy(product_id, session)
    if delete_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return {
        "message": "Product deleted successfully"
    }
