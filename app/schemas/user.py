from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List["RoleResponse"] = []
    
    class Config:
        from_attributes = True


# Import here to avoid circular dependency
from app.schemas.role import RoleResponse  # noqa
UserResponse.model_rebuild()

