from typing import List, Optional
from pydantic import BaseModel, Field
from src.domain.models.order_slab import OrderSlab

class OrderRequestDto(BaseModel):
    pi_number: Optional[int] = Field(default=None, alias="PiNumber")
    currency: int = Field(..., alias="Currency")
    country_destination: str = Field(..., alias="CountryDestination")
    port_of_discharge: str = Field(..., alias="PortOfDischarge")
    terms_and_payment: str = Field(..., alias="TermsAndPayment")
    incoterms: Optional[str] = Field(default=None, alias="Incoterms")
    container_20ft: int = Field(default=0, alias="Container20ft")
    container_40ft: int = Field(default=0, alias="Container40ft")
    box_sticker: str = Field(..., alias="BoxSticker")
    box_design: str = Field(..., alias="BoxDesign")
    packing_note: str = Field(..., alias="PackingNote")
    consignee_id: str = Field(..., alias="ConsigneeId")
    supplier_id: str = Field(..., alias="SupplierId")
    hscode_id: Optional[str] = Field(default=None, alias="HscodeId")
    discount: float = Field(default=0.0, alias="Discount")
    ocean_freight: float = Field(default=0.0, alias="OceanFreight")
    slab: List[OrderSlab] = Field(default_factory=list, alias="Slab")

    class Config:
        populate_by_name = True
