"""Auth module request/response schemas."""
from pydantic import BaseModel, Field, model_validator

from app.infrastructure.db.models import User


class GoogleLoginIn(BaseModel):
    id_token: str | None = Field(default=None, min_length=1)
    access_token: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_google_token(self) -> "GoogleLoginIn":
        if not self.id_token and not self.access_token:
            raise ValueError("id_token or access_token is required")
        return self


class RegisterIn(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(default=None, max_length=200)


class PasswordLoginIn(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: str
    email: str | None = None
    display_name: str | None = None


class AuthTokenOut(BaseModel):
    access_token: str
    user: UserOut


def to_user_out(user: User) -> UserOut:
    return UserOut(id=user.id, email=user.email, display_name=user.display_name)
