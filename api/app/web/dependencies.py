from fastapi import Request, Depends, HTTPException
from app.core.security import get_current_customer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from typing import Optional

from app.modules.customer.models import Customer


async def get_user(request: Request, db: AsyncSession = Depends(get_db)) -> Optional[Customer]:
    try:
        user = await get_current_customer(request, db)
    except HTTPException:
        user = None
    return user
