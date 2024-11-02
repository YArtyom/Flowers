from typing import TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar("T")  # Обобщенный тип для параметризации

class SBaseListResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    limit: int