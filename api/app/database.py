import inflect
from sqlalchemy import Integer
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import settings

DB_USER = settings.DB_USER
DB_PASS = settings.DB_PASS
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL)

async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

p = inflect.engine()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)

    @declared_attr
    def __tablename__(cls) -> str:
        return p.plural(cls.__name__.lower())
