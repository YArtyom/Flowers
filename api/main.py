import shutil
from datetime import timedelta
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from auth import create_access_token, authenticate_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from crud import create_customer, get_products, get_active_basket, create_basket, add_item_to_basket, get_basket_items, \
    remove_item_from_basket
from schemas import BasketItemOut, BasketOut, ProductOut, CustomerOut, CustomerCreate
from database import engine, Base, get_db, init_db
from pages.router import routerS as rout_pages
from fastapi.staticfiles import StaticFiles
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.include_router(rout_pages)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.post("/register", response_model=CustomerOut)
async def register(customer: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await create_customer(db, customer)


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.mail}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/products", response_model=List[ProductOut])
async def get_products(db: AsyncSession = Depends(get_db)):
    return await get_products(db)

@app.get("/basket", response_model=BasketOut)
async def get_basket(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
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
