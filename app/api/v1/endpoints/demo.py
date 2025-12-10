from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.deps import (
    get_current_user_jwt_required,
    get_current_user_apikey_required,
    get_current_user_either,
    require_permissions,
    require_roles
)


router = APIRouter()


@router.get("/public")
async def public_endpoint():
    """
    Public endpoint - no authentication required
    """
    return {
        "message": "This is a public endpoint - no authentication required",
        "status": "public"
    }


@router.get("/jwt-only")
async def jwt_only_endpoint(
    current_user: User = Depends(get_current_user_jwt_required)
):
    """
    JWT authentication ONLY - API keys will NOT work
    """
    return {
        "message": "Success! You accessed this endpoint with JWT token",
        "user_id": current_user.id,
        "email": current_user.email,
        "auth_type": "JWT"
    }


@router.get("/apikey-only")
async def apikey_only_endpoint(
    current_user: User = Depends(get_current_user_apikey_required)
):
    """
    API Key authentication ONLY - JWT tokens will NOT work
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
    Either JWT or API Key authentication - both work
    """
    return {
        "message": "Success! You accessed this endpoint with either JWT or API Key",
        "user_id": current_user.id,
        "email": current_user.email,
        "auth_type": "JWT_OR_API_KEY"
    }


@router.get("/admin-only", dependencies=[Depends(require_roles(["admin"]))])
async def admin_only_endpoint(
    current_user: User = Depends(get_current_user_either)
):
    """
    Requires 'admin' role - works with both JWT and API Key
    """
    return {
        "message": "Success! You have admin role",
        "user_id": current_user.id,
        "email": current_user.email,
        "roles": [role.name for role in current_user.roles]
    }


@router.get("/read-users-permission", dependencies=[Depends(require_permissions(["users:read"]))])
async def read_users_permission_endpoint(
    current_user: User = Depends(get_current_user_either)
):
    """
    Requires 'users:read' permission - works with both JWT and API Key
    """
    return {
        "message": "Success! You have users:read permission",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/write-users-permission", dependencies=[Depends(require_permissions(["users:write"]))])
async def write_users_permission_endpoint(
    current_user: User = Depends(get_current_user_either)
):
    """
    Requires 'users:write' permission - works with both JWT and API Key
    """
    return {
        "message": "Success! You have users:write permission",
        "user_id": current_user.id,
        "email": current_user.email
    }

