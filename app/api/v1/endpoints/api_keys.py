from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyListResponse
from app.services.api_key_service import APIKeyService
from app.api.deps import get_current_user_jwt_required


router = APIRouter()


@router.post("/", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Create a new API key (JWT required)"""
    return APIKeyService.create_api_key(
        db,
        user_id=current_user.id,
        api_key_data=api_key_data
    )


@router.get("/", response_model=List[APIKeyListResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """List all API keys for current user (JWT required)"""
    return APIKeyService.get_user_api_keys(db, user_id=current_user.id)


@router.get("/{api_key_id}", response_model=APIKeyResponse)
async def get_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Get specific API key details (JWT required)"""
    return APIKeyService.get_api_key(db, api_key_id=api_key_id, user_id=current_user.id)


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Delete an API key (JWT required)"""
    APIKeyService.delete_api_key(db, api_key_id=api_key_id, user_id=current_user.id)
    return None


@router.patch("/{api_key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Deactivate an API key (JWT required)"""
    return APIKeyService.toggle_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id, activate=False
    )


@router.patch("/{api_key_id}/activate", response_model=APIKeyResponse)
async def activate_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Activate an API key (JWT required)"""
    return APIKeyService.toggle_api_key(
        db, api_key_id=api_key_id, user_id=current_user.id, activate=True
    )

