from typing import Optional
from pydantic import BaseModel, Field
from src.domain.utils.py_object_id import PyObjectId


class GSupplier(BaseModel):
    # Equivale a [BsonRepresentation(MongoDB.Bson.BsonType.ObjectId)]
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    supplier_id: str = Field(..., alias="SupplierId")
    name: str = Field(..., alias="Name")
    logo: str = Field(..., alias="Logo")
    exporter_id: str = Field(..., alias="ExporterId")
    manufacturer_id: str = Field(..., alias="ManufacturerId")

    class Config:
        populate_by_name = True