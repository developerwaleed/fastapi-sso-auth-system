from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class APIKeyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    role_ids: Optional[List[int]] = []
    permission_ids: Optional[List[int]] = []


class APIKeyResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    key: str
    is_active: bool
    expires_at: Optional[datetime] = None
    created_at: datetime
    roles: List["RoleResponse"] = []
    permissions: List["PermissionResponse"] = []
    
    class Config:
        from_attributes = True


class APIKeyListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    key: str
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Import here to avoid circular dependency
from app.schemas.role import RoleResponse  # noqa
from app.schemas.permission import PermissionResponse  # noqa
APIKeyResponse.model_rebuild()

