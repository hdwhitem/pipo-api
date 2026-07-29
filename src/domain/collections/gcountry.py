from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class Gcountry(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="Id")
    code: str = Field(..., alias="Code")
    name: str = Field(..., alias="Name")
    image: str = Field(..., alias="Image")

    class Config:
        populate_by_name = True