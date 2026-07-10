from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from src.domain.utils.py_object_id import PyObjectId

class GProformaNumber(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    count: int = 0
    created_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    class Config:
        populate_by_name = True