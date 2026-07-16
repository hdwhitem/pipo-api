from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from src.domain.utils.py_object_id import PyObjectId

class GPasswordReset(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: str = Field(..., description="Email del usuario que solicita el cambio")
    code: str = Field(..., description="Código verificador de un solo uso")
    used: bool = Field(default=False)
    created_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: datetime = Field(..., description="Fecha de expiración del código")

    class Config:
        populate_by_name = True