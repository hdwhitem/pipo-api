from pydantic import BaseModel, EmailStr, Field

class LoginDto(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)