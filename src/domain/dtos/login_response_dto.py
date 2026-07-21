from pydantic import BaseModel
from typing import Optional
from src.domain.dtos.user_dto import UserResponseDto

class LoginResponseDto(BaseModel):
    flag: bool
    message: str
    user: Optional[UserResponseDto] = None
