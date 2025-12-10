from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.api.deps import get_current_user_jwt_required


router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_jwt_required)
):
    """Get current user profile (JWT required)"""
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """List all users (JWT required)"""
    return UserService.get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Get user by ID (JWT required)"""
    return UserService.get_user_by_id(db, user_id=user_id)


@router.post("/{user_id}/roles/{role_id}", response_model=UserResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Assign role to user (JWT required)"""
    return UserService.assign_role_to_user(db, user_id=user_id, role_id=role_id)


@router.delete("/{user_id}/roles/{role_id}", response_model=UserResponse)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Remove role from user (JWT required)"""
    return UserService.remove_role_from_user(db, user_id=user_id, role_id=role_id)

