from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import async_session


class BaseRepository:
    model = None

    @classmethod
    def build_joinedload(cls, include: str):
        parts = include.split('.')
        option = joinedload(getattr(cls, parts[0]))
        current_class = cls
        for i in range(len(parts)-1):
            current_class = getattr(current_class, parts[i]).property.mapper.class_
            option = option.joinedload(getattr(current_class, parts[i+1]))
        return option

    @classmethod
    async def get_all(cls):
        async with async_session() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_by_id(cls, id):
        async with async_session() as session:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_by(cls, **filters):
        async with async_session() as session:
            query = select(cls.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def create(cls, session: AsyncSession, **data):
        instance = cls.model(**data)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @classmethod
    async def update(cls, id, data: dict):
        async with async_session() as session:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)
            instance = result.scalar_one_or_none()
            if not instance:
                return None
            for key, value in data.items():
                setattr(instance, key, value)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def destroy(cls, id, session: AsyncSession):
        query = select(cls.model).filter_by(id=id)
        result = await session.execute(query)
        instance = result.scalar_one_or_none()

        if not instance:
            return None

        await session.delete(instance)
        await session.commit()
        return {
            "message": "Successfully deleted"
        }

    @classmethod
    async def paginate(cls, page: int, limit: int, filter=None, includes: List[str] = None):
        async with async_session() as session:
            query = select(cls.model).limit(limit).offset((page - 1) * limit)
            if includes:
                for include in includes:
                    query = query.options(cls.build_joinedload(include))
            if filter is not None:
                query = query.filter(filter)
            result = await session.execute(query)
            return result.unique().scalars().all()

    @classmethod
    async def count(cls, filter=None):
        async with async_session() as session:
            if filter is not None:
                query = select(func.count(cls.model.id)).filter(filter)
            else:
                query = select(func.count(cls.model.id))
            result = await session.execute(query)
            return result.scalar()
