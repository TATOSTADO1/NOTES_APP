from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )
    device_name: str | None = Field(default=None, max_length=100)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        value = value.strip().lower()
        if len(value) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_name: str | None = Field(default=None, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=40, max_length=512)
