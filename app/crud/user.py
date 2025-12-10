from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserBase


class CRUDUser(CRUDBase[User, UserCreate, UserBase]):
    """CRUD operations for User model"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email address"""
        return db.query(User).filter(User.email == email).first()
    
    def create_with_role(
        self, db: Session, *, obj_in: UserCreate, role_name: str = "user"
    ) -> User:
        """Create user with default role"""
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            is_active=True
        )
        
        # Assign default role
        role = db.query(Role).filter(Role.name == role_name).first()
        if role:
            db_obj.roles.append(role)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def add_role(self, db: Session, *, user: User, role: Role) -> User:
        """Add role to user"""
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        return user
    
    def remove_role(self, db: Session, *, user: User, role: Role) -> User:
        """Remove role from user"""
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
            db.refresh(user)
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser"""
        return user.is_superuser


user = CRUDUser(User)

