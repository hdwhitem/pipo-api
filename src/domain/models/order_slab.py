# src/domain/models/order_slab.py
from pydantic import BaseModel
from typing import Optional

class OrderSlab(BaseModel):
    width: float
    height: float
    thickness: int
    finished: str
    name: str
    qty: int
    pallet_slabs: float
    faces: str
    price: float
    image: str
    area: Optional[float] = None
    sub_total: Optional[float] = None