from pydantic import BaseModel, ConfigDict, Field

class BankItemDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="Id")
    bank_name: str = Field(..., alias="BankName")
    currency_account: str = Field(..., alias="CurrencyAccount")