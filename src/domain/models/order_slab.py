# src/domain/models/order_slab.py
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class OrderSlab(BaseModel):
    
    width: float = Field(..., alias="Width")
    height: float = Field(..., alias="Height")
    thickness: int = Field(..., alias="Thickness")
    finished: str = Field(..., alias="Finished")
    name: str = Field(..., alias="Name")
    qty: int = Field(..., alias="Qty")
    pallet_slabs: float = Field(..., alias="PalletSlabs")
    faces: str = Field(..., alias="Faces")
    price: float = Field(..., alias="Price")
    image: str = Field(..., alias="Image")
    area: Optional[float] = Field(default=None, alias="Area")
    sub_total: Optional[float] = Field(default=None, alias="SubTotal")

    model_config = ConfigDict(
            populate_by_name=True  # Permite instanciar usando tanto 'width' como 'Width'
        )