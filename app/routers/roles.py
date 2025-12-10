from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Role, Permission
from app.schemas import RoleCreate, RoleResponse, PermissionCreate, PermissionResponse
from app.auth import get_current_user_jwt_only, require_permissions


router = APIRouter(prefix="/roles", tags=["Roles & Permissions"])


@router.post("/permissions/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Create a new permission (JWT auth required)"""
    # Check if permission already exists
    existing = db.query(Permission).filter(Permission.name == permission.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    new_permission = Permission(
        name=permission.name,
        description=permission.description,
        resource=permission.resource,
        action=permission.action
    )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    return new_permission


@router.get("/permissions/", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """List all permissions (JWT auth required)"""
    permissions = db.query(Permission).all()
    return permissions


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Create a new role (JWT auth required)"""
    # Check if role already exists
    existing = db.query(Role).filter(Role.name == role.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    new_role = Role(
        name=role.name,
        description=role.description
    )
    
    # Add permissions to role
    if role.permission_ids:
        permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
        new_role.permissions = permissions
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return new_role


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """List all roles (JWT auth required)"""
    roles = db.query(Role).all()
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Get role details (JWT auth required)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.post("/{role_id}/permissions/{permission_id}", response_model=RoleResponse)
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_user_jwt_only),
    db: Session = Depends(get_db)
):
    """Add permission to role (JWT auth required)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)
    
    return role

