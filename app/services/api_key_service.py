from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.api_key import APIKey
from app.crud.api_key import api_key as api_key_crud
from app.schemas.api_key import APIKeyCreate


class APIKeyService:
    """Service for API key operations"""
    
    @staticmethod
    def create_api_key(
        db: Session,
        *,
        user_id: int,
        api_key_data: APIKeyCreate
    ) -> APIKey:
        """
        Create new API key for user
        
        Args:
            db: Database session
            user_id: Owner user ID
            api_key_data: API key creation data
            
        Returns:
            Created API key
        """
        return api_key_crud.create_with_roles_permissions(
            db,
            obj_in=api_key_data,
            user_id=user_id,
            role_ids=api_key_data.role_ids,
            permission_ids=api_key_data.permission_ids
        )
    
    @staticmethod
    def get_user_api_keys(db: Session, user_id: int) -> List[APIKey]:
        """Get all API keys for user"""
        return api_key_crud.get_by_user(db, user_id=user_id)
    
    @staticmethod
    def get_api_key(db: Session, api_key_id: int, user_id: int) -> APIKey:
        """
        Get API key by ID for user
        
        Args:
            db: Database session
            api_key_id: API key ID
            user_id: Owner user ID
            
        Returns:
            API key
            
        Raises:
            HTTPException: If API key not found or not owned by user
        """
        api_key = api_key_crud.get(db, id=api_key_id)
        if not api_key or api_key.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        return api_key
    
    @staticmethod
    def delete_api_key(db: Session, api_key_id: int, user_id: int) -> None:
        """
        Delete API key
        
        Args:
            db: Database session
            api_key_id: API key ID
            user_id: Owner user ID
            
        Raises:
            HTTPException: If API key not found or not owned by user
        """
        api_key = api_key_crud.get(db, id=api_key_id)
        if not api_key or api_key.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        api_key_crud.remove(db, id=api_key_id)
    
    @staticmethod
    def toggle_api_key(
        db: Session, api_key_id: int, user_id: int, activate: bool
    ) -> APIKey:
        """
        Activate or deactivate API key
        
        Args:
            db: Database session
            api_key_id: API key ID
            user_id: Owner user ID
            activate: True to activate, False to deactivate
            
        Returns:
            Updated API key
            
        Raises:
            HTTPException: If API key not found or not owned by user
        """
        api_key = api_key_crud.get(db, id=api_key_id)
        if not api_key or api_key.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        if activate:
            return api_key_crud.activate(db, api_key=api_key)
        else:
            return api_key_crud.deactivate(db, api_key=api_key)
    
    @staticmethod
    def validate_api_key(db: Session, key: str) -> Optional[APIKey]:
        """
        Validate API key and update last used timestamp
        
        Args:
            db: Database session
            key: API key string
            
        Returns:
            API key if valid, None otherwise
        """
        api_key = api_key_crud.get_by_key(db, key=key)
        
        if not api_key:
            return None
        
        if not api_key_crud.is_valid(api_key):
            return None
        
        # Update last used timestamp
        api_key_crud.update_last_used(db, api_key=api_key)
        
        return api_key

