from app.product.models import Product, Basket, BasketItem
from app.repository.base import BaseRepository


class ProductRepository(BaseRepository):
    model = Product


class BasketRepository(BaseRepository):
    model = Basket


class BasketItemRepository(BaseRepository):
    model = BasketItem
