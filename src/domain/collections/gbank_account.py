from typing import Optional
from pydantic import BaseModel, Field
from src.domain.utils.py_object_id import PyObjectId


class GBankAccount(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    beneficiary: str = Field(..., alias="Beneficiary")
    bank_name: str = Field(..., alias="BankName")
    currency_account: str = Field(..., alias="CurrencyAccount")
    bank_account_no: str = Field(..., alias="BankAccountNo")
    swift_code: str = Field(..., alias="SwiftCode")
    intermediary_bank: str = Field(..., alias="IntermediaryBank")

    class Config:
        populate_by_name = True