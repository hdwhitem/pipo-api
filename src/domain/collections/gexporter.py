from typing import Optional
from pydantic import BaseModel, Field
from src.domain.utils.py_object_id import PyObjectId


class GExporter(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    name: str = Field(..., alias="Name")
    address: str = Field(..., alias="Address")
    city: str = Field(..., alias="City")
    post_code: str = Field(..., alias="PostCode")
    tax_id: str = Field(..., alias="TaxId")
    phone: str = Field(..., alias="Phone")
    sign: str = Field(..., alias="Sign")
    bank_id: str = Field(..., alias="BankId")

    class Config:
        populate_by_name = True