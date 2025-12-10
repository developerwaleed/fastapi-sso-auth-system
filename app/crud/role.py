from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.role import RoleCreate, RoleBase


class CRUDRole(CRUDBase[Role, RoleCreate, RoleBase]):
    """CRUD operations for Role model"""
    
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        """Get role by name"""
        return db.query(Role).filter(Role.name == name).first()
    
    def create_with_permissions(
        self, db: Session, *, obj_in: RoleCreate, permission_ids: List[int] = None
    ) -> Role:
        """Create role with permissions"""
        db_obj = Role(
            name=obj_in.name,
            description=obj_in.description
        )
        
        # Add permissions
        if permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            db_obj.permissions = permissions
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def add_permission(self, db: Session, *, role: Role, permission: Permission) -> Role:
        """Add permission to role"""
        if permission not in role.permissions:
            role.permissions.append(permission)
            db.commit()
            db.refresh(role)
        return role
    
    def remove_permission(self, db: Session, *, role: Role, permission: Permission) -> Role:
        """Remove permission from role"""
        if permission in role.permissions:
            role.permissions.remove(permission)
            db.commit()
            db.refresh(role)
        return role


role = CRUDRole(Role)

