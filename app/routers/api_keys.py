from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, APIKey, Role, Permission
from app.schemas import APIKeyCreate, APIKeyResponse, APIKeyListResponse
from app.auth import get_current_user_jwt_only


router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Create a new API key (JWT authentication required)"""
    
    # Generate unique API key
    key = APIKey.generate_key()
    
    # Create API key
    api_key = APIKey(
        user_id=current_user.id,
        key=key,
        name=api_key_data.name,
        description=api_key_data.description,
        expires_at=api_key_data.expires_at,
        is_active=True
    )
    
    # Add roles
    if api_key_data.role_ids:
        roles = db.query(Role).filter(Role.id.in_(api_key_data.role_ids)).all()
        api_key.roles = roles
    
    # Add permissions
    if api_key_data.permission_ids:
        permissions = db.query(Permission).filter(Permission.id.in_(api_key_data.permission_ids)).all()
        api_key.permissions = permissions
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.get("/", response_model=List[APIKeyListResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """List all API keys for current user (JWT authentication required)"""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return api_keys


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Get specific API key details (JWT authentication required)"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return api_key


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Delete an API key (JWT authentication required)"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return None


@router.patch("/{api_key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Deactivate an API key (JWT authentication required)"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.patch("/{api_key_id}/activate", response_model=APIKeyResponse)
async def activate_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Activate an API key (JWT authentication required)"""
    api_key = db.query(APIKey).filter(
        APIKey.id == api_key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = True
    db.commit()
    db.refresh(api_key)
    
    return api_key

