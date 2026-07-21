from pydantic import BaseModel
class UserResponseDto(BaseModel):
    name: str
    email: str
