from pydantic import BaseModel, UUID4
from app.enums import UserRole
from typing import Optional


class TokenRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID4
    username: str
    email: str
    role: UserRole


class UserUpdateRequest(BaseModel):
    email: str
    username: str


