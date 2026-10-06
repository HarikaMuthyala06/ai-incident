from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class UserRole:
    ADMIN = "admin"
    ENGINEER = "engineer"

class UserBase(BaseModel):
    email: str
    username: str
    role: str = UserRole.ENGINEER  # admin or engineer
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
