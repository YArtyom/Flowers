from sqlalchemy import select
from database import async_session_maker

class BaseRepository:
    model = None

    @classmethod
    async def get_by_username(cls, **filters):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls):
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_by_id(cls, id):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def create(cls, **data):
        async with async_session_maker() as session:
            db_obj = cls.model(**data)
            session.add(db_obj)
            await session.commit()
            return db_obj

    @classmethod
    async def update(cls, id, data: dict):
        async with async_session_maker() as session:
            db_obj = await cls.get_by_id(id, session)
            if not db_obj:
                raise ValueError(f"Not Found {cls.__name__}")
            for key, value in data.items():
                setattr(db_obj, key, value)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj

    @classmethod
    async def delete(cls, id):
        async with async_session_maker() as session:
            db_obj = await cls.get_by_id(id, session)
            if not db_obj:
                raise ValueError(f"Not Found {cls.__name__}")
            session.delete(db_obj)
            await session.commit()
