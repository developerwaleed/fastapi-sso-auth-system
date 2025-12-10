from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.api_key import APIKey
from app.models.role import Role
from app.models.permission import Permission
from app.schemas.api_key import APIKeyCreate, APIKeyCreate


class CRUDAPIKey(CRUDBase[APIKey, APIKeyCreate, APIKeyCreate]):
    """CRUD operations for APIKey model"""
    
    def get_by_key(self, db: Session, *, key: str) -> Optional[APIKey]:
        """Get API key by key string"""
        return db.query(APIKey).filter(APIKey.key == key).first()
    
    def get_by_user(self, db: Session, *, user_id: int) -> List[APIKey]:
        """Get all API keys for a user"""
        return db.query(APIKey).filter(APIKey.user_id == user_id).all()
    
    def create_with_roles_permissions(
        self,
        db: Session,
        *,
        obj_in: APIKeyCreate,
        user_id: int,
        role_ids: List[int] = None,
        permission_ids: List[int] = None
    ) -> APIKey:
        """Create API key with roles and permissions"""
        db_obj = APIKey(
            user_id=user_id,
            key=APIKey.generate(),
            name=obj_in.name,
            description=obj_in.description,
            expires_at=obj_in.expires_at,
            is_active=True
        )
        
        # Add roles
        if role_ids:
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
            db_obj.roles = roles
        
        # Add permissions
        if permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            db_obj.permissions = permissions
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_last_used(self, db: Session, *, api_key: APIKey) -> APIKey:
        """Update last used timestamp"""
        api_key.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(api_key)
        return api_key
    
    def deactivate(self, db: Session, *, api_key: APIKey) -> APIKey:
        """Deactivate API key"""
        api_key.is_active = False
        db.commit()
        db.refresh(api_key)
        return api_key
    
    def activate(self, db: Session, *, api_key: APIKey) -> APIKey:
        """Activate API key"""
        api_key.is_active = True
        db.commit()
        db.refresh(api_key)
        return api_key
    
    def is_valid(self, api_key: APIKey) -> bool:
        """Check if API key is valid (active and not expired)"""
        if not api_key.is_active:
            return False
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return False
        return True


api_key = CRUDAPIKey(APIKey)

