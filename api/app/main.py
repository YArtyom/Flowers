import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.modules.basket.routes import router as basket_router
from app.modules.basket_item.routes import router as basket_item_router
from app.modules.customer.routes import router as customer_router
from app.modules.order.routes import router as order_router
from app.modules.product.routes import router as product_router
from app.web.basket.routes import router as basket_router_web
from app.web.customer.routes import router as customer_router_web
from app.web.order.routes import router as order_router_web
from app.web.product.routes import router as product_router_web
templates = Jinja2Templates(directory="app/web/templates")

app = FastAPI(title="Цветочный магазин")

app.include_router(customer_router)
app.include_router(product_router)
app.include_router(basket_router)
app.include_router(order_router)
app.include_router(basket_item_router)

#Templates

app.include_router(customer_router_web)
app.include_router(product_router_web)
app.include_router(basket_router_web)
app.include_router(order_router_web)

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host='127.0.0.1')
