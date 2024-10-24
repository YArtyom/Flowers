from fastapi import APIRouter
from app.product.routes.product_router import router as product_router
from app.product.routes.basket_router import router as basket_router

router = APIRouter(prefix="/app")

router.include_router(product_router)
router.include_router(basket_router)
