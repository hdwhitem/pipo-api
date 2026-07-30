from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# DTO para el endpoint de Listar (solo devuelve Name, SupplierId, ExporterId e Id)
class SupplierListItemDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="Id")
    name: str = Field(..., alias="Name")
    supplier_id: str = Field(..., alias="SupplierId")
    exporter_id: Optional[str] = Field(None, alias="ExporterId")

# DTO para Crear / Editar Supplier
class SupplierCreateUpdateDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(..., alias="Name")
    logo: Optional[str] = Field(None, alias="Logo")
    exporter_id: Optional[str] = Field(None, alias="ExporterId")
    supplier_id: str = Field(..., alias="SupplierId")
    manufacturer_id: Optional[str] = Field(None, alias="ManufacturerId")