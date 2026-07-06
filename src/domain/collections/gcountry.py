from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class Gcountry(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    code: str = Field(..., validation_alias="Code")
    name: str = Field(..., validation_alias="Name")
    image: str = Field(..., validation_alias="Image")

    class Config:
        populate_by_name = True