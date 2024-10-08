from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


DB_USER = 'postgres'
DB_PASS = 'postgres'
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'Flows'

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async_session_maker = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

class Base(DeclarativeBase):
    pass
