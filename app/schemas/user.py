# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    """Used when user sends POST /register request"""
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    """Used when user sends POST /login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """What we send BACK to user — never expose password"""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    """JWT token response after successful login"""
    access_token: str
    token_type: str = "bearer"