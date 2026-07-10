from pydantic import BaseModel, Field
from typing import Optional, List
from src.domain.models.order_slab import OrderSlab
from src.domain.utils.py_object_id import PyObjectId

class GOrder(BaseModel):
    # Id de MongoDB mapeado desde _id
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    
    pi_number: Optional[int] = None
    currency: int
    country_destination: str
    port_of_discharge: str
    terms_and_payment: str
    incoterms: Optional[str] = None
    container20ft: int = 0
    container40ft: int = 0
    box_sticker: str
    box_design: str
    packing_note: str
    consignee_id: str
    supplier_id: Optional[str] = None
    hscode_id: Optional[str] = None
    discount: float = 0.0
    ocean_freight: float = 0.0
    slab: List[OrderSlab] = []

    class Config:
        populate_by_name = True # Permite mapear alias como _id e id indistintamente
        json_encoders = {PyObjectId: str}