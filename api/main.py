import shutil
from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from auth import create_access_token, authenticate_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from crud import create_customer, get_products, get_active_basket, create_basket, add_item_to_basket, get_basket_items, \
    remove_item_from_basket
from pages import basket, profile, home , auth
from schemas import BasketItemOut, BasketOut, ProductOut, CustomerOut
from database import async_session_maker, engine, Base, get_db
from fastapi.staticfiles import StaticFiles
from user.router import router as user_router
from user.schema import uAuth, Token

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Темплейты
app.include_router(home.router)
app.include_router(profile.router)
app.include_router(basket.router)
app.include_router(auth.router)

# регистрация пользователя
app.include_router(user_router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/products", response_model=List[ProductOut])
async def get_products_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_products(db)


@app.get("/basket", response_model=BasketOut)
async def get_basket(db: AsyncSession = Depends(get_db), token: str = Depends(uAuth)):
    current_user = await get_current_user(token, db)
    basket = await get_active_basket(db, current_user.id)
    if not basket:
        basket = await create_basket(db, current_user.id)
    items = await get_basket_items(db, basket.id)
    return {"id": basket.id, "customer_id": basket.customer_id, "price": basket.price,
            "active_status": basket.active_status, "items": items}


@app.post("/basket/add", response_model=BasketItemOut)
async def add_to_basket(product_id: int, quantity: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    current_user = await get_current_user(token, db)
    basket = await get_active_basket(db, current_user.id)
    if not basket:
        basket = await create_basket(db, current_user.id)
    basket_item = await add_item_to_basket(db, basket, product_id, quantity)
    return basket_item


@app.delete("/basket/remove/{basket_item_id}", response_model=BasketItemOut)
async def remove_from_basket(basket_item_id: int, db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    await get_current_user(token, db)
    basket_item = await remove_item_from_basket(db, basket_item_id)
    return basket_item


@app.post("/upload-photo/")
async def upload_photo(file: UploadFile = File(...)):
    file_location = f"static/images/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"info": f"File '{file.filename}' saved at '{file_location}'"}
