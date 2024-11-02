from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.user.routers import router as user_router
from app.product.routers import router as mini_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(mini_router)