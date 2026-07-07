from pydantic import BaseModel, Field
from typing import Optional

class Guser(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    UserName: str
    UserLastName: str
    UserEmail: str
    UserPassword: str

    class Config:
        populate_by_name = True