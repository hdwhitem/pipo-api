from pydantic import BaseModel, EmailStr, Field, model_validator

class RegisterUserDto(BaseModel):
    name: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=4)
    emailConfirmed: str

    @model_validator(mode="after")
    def verify_email_match(self):
        if self.email != self.emailConfirmed:
            raise ValueError("Los correos electrónicos no coinciden")
        return self