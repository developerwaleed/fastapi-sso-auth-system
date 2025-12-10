from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.user import User
from app.schemas.role import RoleCreate, RoleResponse
from app.schemas.permission import PermissionCreate, PermissionResponse
from app.crud.role import role as role_crud
from app.crud.permission import permission as permission_crud
from app.api.deps import get_current_user_jwt_required


router = APIRouter()


# Permission endpoints

@router.post("/permissions/", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission: PermissionCreate,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Create a new permission (JWT required)"""
    existing = permission_crud.get_by_name(db, name=permission.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    return permission_crud.create(db, obj_in=permission)


@router.get("/permissions/", response_model=List[PermissionResponse])
async def list_permissions(
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """List all permissions (JWT required)"""
    return permission_crud.get_multi(db)


# Role endpoints

@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Create a new role (JWT required)"""
    existing = role_crud.get_by_name(db, name=role.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    return role_crud.create_with_permissions(
        db, obj_in=role, permission_ids=role.permission_ids
    )


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """List all roles (JWT required)"""
    return role_crud.get_multi(db)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Get role details (JWT required)"""
    role = role_crud.get(db, id=role_id)
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
    current_user: User = Depends(get_current_user_jwt_required),
    db: Session = Depends(get_db)
):
    """Add permission to role (JWT required)"""
    role = role_crud.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    permission = permission_crud.get(db, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    return role_crud.add_permission(db, role=role, permission=permission)

