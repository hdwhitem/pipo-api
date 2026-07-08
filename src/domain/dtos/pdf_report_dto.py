from pydantic import BaseModel, Field

class SimpleReportDto(BaseModel):
    name: str = Field(..., example="Hernán Blanco")
    pi_number: str = Field(..., example="PI-2026-001")
    qty: int = Field(..., example=150)
    total: float = Field(..., example=2450.75)