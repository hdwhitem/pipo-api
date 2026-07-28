from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")

class PagedResult(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    page_number: int
    page_size: int
