from fastapi import APIRouter, Depends
from app.models import User
from app.auth import (
    get_current_user_jwt_only,
    get_current_user_apikey_only,
    get_current_user_either,
    require_permissions,
    require_roles
)

router = APIRouter(prefix="/demo", tags=["Demo Endpoints"])


@router.get("/jwt-only")
async def jwt_only_endpoint(
    current_user: User = Depends(get_current_user_jwt_only)
):
    """
    This endpoint requires JWT authentication only.
    API keys will NOT work here.
    """
    return {
        "message": "Success! You accessed this endpoint with JWT token",
        "user_id": current_user.id,
        "email": current_user.email,
        "auth_type": "JWT"
    }


@router.get("/apikey-only")
async def apikey_only_endpoint(
    current_user: User = Depends(get_current_user_apikey_only)
):
    """
    This endpoint requires API Key authentication only.
    JWT tokens will NOT work here.
    """
    return {
        "message": "Success! You accessed this endpoint with API Key",
        "user_id": current_user.id,
        "email": current_user.email,
        "auth_type": "API_KEY"
    }


@router.get("/either-auth")
async def either_auth_endpoint(
    current_user: User = Depends(get_current_user_either)
):
    """
    This endpoint allows EITHER JWT or API Key authentication.
    Both will work here.
    """
    return {
        "message": "Success! You accessed this endpoint with either JWT or API Key",
        "user_id": current_user.id,
        "email": current_user.email,
        "auth_type": "JWT_OR_API_KEY"
    }


@router.get("/admin-only")
async def admin_only_endpoint(
    current_user: User = Depends(get_current_user_either),
    _: bool = Depends(require_roles(["admin"]))
):
    """
    This endpoint requires 'admin' role.
    Works with both JWT and API Key, but must have admin role.
    """
    return {
        "message": "Success! You have admin role",
        "user_id": current_user.id,
        "email": current_user.email,
        "roles": [role.name for role in current_user.roles]
    }


@router.get("/read-users-permission")
async def read_users_permission_endpoint(
    current_user: User = Depends(get_current_user_either),
    _: bool = Depends(require_permissions(["users:read"]))
):
    """
    This endpoint requires 'users:read' permission.
    Works with both JWT and API Key, but must have the specific permission.
    """
    return {
        "message": "Success! You have users:read permission",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/write-users-permission")
async def write_users_permission_endpoint(
    current_user: User = Depends(get_current_user_either),
    _: bool = Depends(require_permissions(["users:write"]))
):
    """
    This endpoint requires 'users:write' permission.
    Works with both JWT and API Key, but must have the specific permission.
    """
    return {
        "message": "Success! You have users:write permission",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/public")
async def public_endpoint():
    """
    This is a public endpoint - no authentication required.
    """
    return {
        "message": "This is a public endpoint - no authentication required",
        "status": "public"
    }

