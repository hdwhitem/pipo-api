from pydantic import BaseModel, Field, AliasChoices
from typing import Optional
from src.domain.utils.py_object_id import PyObjectId

class ColourDocument(BaseModel):
    id: Optional[PyObjectId] = Field(
            default=None, 
            validation_alias="_id", 
            alias="Id" 
        )
    name: str = Field(..., alias="Name")
    image: str = Field(..., alias="Image")
    type: Optional[int] = Field(default=None, alias="Type")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
