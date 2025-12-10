from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionBase


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionBase]):
    """CRUD operations for Permission model"""
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return db.query(Permission).filter(Permission.name == name).first()
    
    def get_by_resource_action(
        self, db: Session, *, resource: str, action: str
    ) -> Optional[Permission]:
        """Get permission by resource and action"""
        return db.query(Permission).filter(
            Permission.resource == resource,
            Permission.action == action
        ).first()


permission = CRUDPermission(Permission)

