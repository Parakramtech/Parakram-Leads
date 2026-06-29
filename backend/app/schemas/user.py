from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleAuth(BaseModel):
    credential: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    auth_provider: str

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
