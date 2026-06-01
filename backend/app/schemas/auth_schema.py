from pydantic import BaseModel, EmailStr, Field
from app.schemas.user_schema import UserResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class RefreshResponse(BaseModel):
    access_token: str
