# src/domain/collections/g_consignee.py
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from src.domain.utils.py_object_id import PyObjectId


class GConsignee(BaseModel):

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str = Field(..., max_length=70, alias="Name")
    tax_id: str = Field(..., max_length=25, alias="TaxId")
    email: Optional[EmailStr] = Field(default=None, max_length=100, alias="Email")
    address: str = Field(..., max_length=80, alias="Address")
    post_code: str = Field(..., max_length=10, alias="PostCode")
    city: str = Field(..., max_length=40, alias="City")
    country: str = Field(..., max_length=20, alias="Country")
    phone: str = Field(..., max_length=20, alias="Phone")
    client: bool = Field(default=False, alias="Client")
    
    created_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        alias="CreatedDate"
    )

    modified_date: Optional[datetime] = Field(
        default=None,
        alias="ModifiedDate"
    )

    class Config:
        populate_by_name = True