from fastapi import APIRouter, Request, Depends, Form, status, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.modules.product.models import Product
from app.modules.customer.models import Customer
from app.core.security import get_current_customer
from app.common.templates import templates
from sqlalchemy.future import select

router = APIRouter(tags=['product_pages'])

# Список товаров
@router.get("/products")
async def list_products(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    user = None
    try:
        user = await get_current_customer(request, db)
    except HTTPException:
        pass
    return templates.TemplateResponse("product/list.html", {"request": request, "products": products, "user": user})

# Детали товара
@router.get("/products/{product_id}")
async def product_detail(product_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    user = None
    try:
        user = await get_current_customer(request, db)
    except HTTPException:
        pass
    return templates.TemplateResponse("product/detail.html", {"request": request, "product": product, "user": user})

# Добавление товара (только для администратора)
@router.get("/products/create")
async def create_product_get(
    request: Request,
    current_customer: Customer = Depends(get_current_customer)
):
    if not current_customer.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    return templates.TemplateResponse("product/create.html", {"request": request, "user": current_customer})

@router.post("/products/create")
async def create_product_post(
    request: Request,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    quantity: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    if not current_customer.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    product = Product(
        name=name,
        price=price,
        description=description,
        quantity=quantity
    )
    db.add(product)
    await db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_302_FOUND)

# Редактирование товара (только для администратора)
@router.get("/products/{product_id}/edit")
async def edit_product_get(
    product_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    if not current_customer.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return templates.TemplateResponse("product/update.html", {"request": request, "product": product, "user": current_customer})

@router.post("/products/{product_id}/edit")
async def edit_product_post(
    product_id: int,
    request: Request,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    quantity: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    if not current_customer.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    product.name = name
    product.price = price
    product.description = description
    product.quantity = quantity
    db.add(product)
    await db.commit()
    return RedirectResponse(url=f"/products/{product_id}", status_code=status.HTTP_302_FOUND)

# Удаление товара (только для администратора)
@router.post("/products/{product_id}/delete")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer)
):
    if not current_customer.is_admin:
        raise HTTPException(status_code=403, detail="Нет доступа")
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    await db.delete(product)
    await db.commit()
    return RedirectResponse(url="/products", status_code=status.HTTP_302_FOUND)
