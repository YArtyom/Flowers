from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.database import get_session
from app.product.repository import ProductRepository, BasketRepository, BasketItemRepository
from app.user.dependencies import get_current_user
from app.user.models import User

router = APIRouter(
    prefix="/basket",
    tags=["BasketPages"],
)

templates = Jinja2Templates(directory="app/web/ProductBasket")

# Отображение всех продуктов с возможностью добавления в корзину
@router.get("/product")
async def get_products(request: Request, session: AsyncSession = Depends(get_session)):
    """
    Получение всех продуктов и отображение с кнопкой добавления в корзину
    """
    products = await ProductRepository.get_all()
    return templates.TemplateResponse("list.html", {"request": request, "products": products})

# Создание нового продукта с использованием BaseRepository
@router.post("/product/create")
async def create_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    product_image: str = Form(...),
    session: AsyncSession = Depends(get_session)
):
    """
    Создание нового продукта
    """
    await ProductRepository.create(session, name=name, price=price, description=description, quantity=quantity, product_image=product_image)
    return RedirectResponse("/basket/product", status_code=HTTP_302_FOUND)

# Добавление продукта в корзину
@router.post("/add")
async def add_product_to_basket(
    product_id: int,
    quantity: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Добавление продукта в корзину
    """
    await BasketRepository.add_item_to_basket(session, user_id=current_user.id, product_id=product_id, quantity=quantity)
    return RedirectResponse("/basket", status_code=HTTP_302_FOUND)

# Отображение корзины пользователя
@router.get("/")
async def get_basket(request: Request, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    """
    Отображение корзины пользователя
    """
    basket_items, total_price = await BasketRepository.get_basket_items_by_user(session, user_id=current_user.id)
    return templates.TemplateResponse("details.html", {"request": request, "basket_items": basket_items, "total_price": total_price})

# Обновление количества товара в корзине
@router.post("/update")
async def update_basket_item(
    product_id: int,
    quantity: int = Form(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Обновление количества товара в корзине
    """
    await BasketItemRepository.update_quantity(session, user_id=current_user.id, product_id=product_id, quantity=quantity)
    return RedirectResponse("/basket", status_code=HTTP_302_FOUND)

# Удаление товара из корзины
@router.post("/remove")
async def remove_product_from_basket(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Удаление товара из корзины
    """
    await BasketItemRepository.remove_item_from_basket(session, user_id=current_user.id, product_id=product_id)
    return RedirectResponse("/basket", status_code=HTTP_302_FOUND)

# Очистка корзины
@router.post("/clear")
async def clear_basket(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Полная очистка корзины
    """
    await BasketRepository.clear_basket(session, user_id=current_user.id)
    return RedirectResponse("/basket", status_code=HTTP_302_FOUND)
