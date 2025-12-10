from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.role import Role
from app.crud.user import user as user_crud
from app.crud.role import role as role_crud


class UserService:
    """Service for user operations"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User model instance
            
        Raises:
            HTTPException: If user not found
        """
        user = user_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return user_crud.get_multi(db, skip=skip, limit=limit)
    
    @staticmethod
    def assign_role_to_user(
        db: Session, user_id: int, role_id: int
    ) -> User:
        """
        Assign role to user
        
        Args:
            db: Database session
            user_id: User ID
            role_id: Role ID
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user or role not found
        """
        user = user_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        role = role_crud.get(db, id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return user_crud.add_role(db, user=user, role=role)
    
    @staticmethod
    def remove_role_from_user(
        db: Session, user_id: int, role_id: int
    ) -> User:
        """
        Remove role from user
        
        Args:
            db: Database session
            user_id: User ID
            role_id: Role ID
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user or role not found
        """
        user = user_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        role = role_crud.get(db, id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return user_crud.remove_role(db, user=user, role=role)

