from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Role
from app.schemas import UserResponse
from app.auth import get_current_user_jwt_only


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_jwt_only),
):
    """Get current user profile (JWT auth required)"""
    return current_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """List all users (JWT auth required)"""
    users = db.query(User).all()
    return users


@router.post("/{user_id}/roles/{role_id}", response_model=UserResponse)
async def assign_role_to_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Assign role to user (JWT auth required)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
        db.refresh(user)
    
    return user


@router.delete("/{user_id}/roles/{role_id}", response_model=UserResponse)
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Remove role from user (JWT auth required)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
        db.refresh(user)
    
    return user

