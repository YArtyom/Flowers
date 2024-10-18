from fastapi import FastAPI
from app.user.routers import router as user_router
from app.product.routers import router as mini_router
from app.web.User.router import router as web_user_router
from app.web.ProductBasket.router import router as web_basket_router

app = FastAPI()

app.include_router(user_router)
app.include_router(mini_router)
app.include_router(web_user_router)
# app.include_router(web_basket_router)