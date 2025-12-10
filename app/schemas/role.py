from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    permissions: List["PermissionResponse"] = []
    
    class Config:
        from_attributes = True


# Import here to avoid circular dependency
from app.schemas.permission import PermissionResponse  # noqa
RoleResponse.model_rebuild()

