from pydantic import BaseModel, Field
from typing import Optional, List
from src.domain.models.order_slab import OrderSlab
from src.domain.utils.py_object_id import PyObjectId

class OrderDocument(BaseModel):
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
    supplier_id: str
    exporter_id: Optional[str] = None
    bank_id: Optional[str] = None
    hscode_id: Optional[str] = None
    discount: float = 0.0
    ocean_freight: float = 0.0
    slab: List[OrderSlab] = Field(default_factory=list)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
