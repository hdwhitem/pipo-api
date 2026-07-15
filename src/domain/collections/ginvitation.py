from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
from src.domain.utils.py_object_id import PyObjectId

class GInvitation(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    code: str = Field(..., description="Código único de invitación aleatorio")
    
    used: bool = Field(default=False, description="Indica si el código ya fue utilizado")
    
    created_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación del código"
    )
    expires_at: datetime = Field(
        ..., 
        description="Fecha límite en la que el código dejará de ser válido"
    )

    class Config:
        populate_by_name = True