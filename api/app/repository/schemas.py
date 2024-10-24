from pydantic import BaseModel


class SBaseListResponse(BaseModel):
    page: int
    total: int
    limit: int
    data: list
