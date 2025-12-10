"""
Dependencies for API endpoints

This module contains reusable dependencies for authentication and authorization.
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from jose import JWTError
from app.db.session import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.core.security import decode_access_token
from app.services.api_key_service import APIKeyService
from app.services.auth_service import AuthService
from app.schemas.auth import TokenData


# Security schemes
bearer_scheme = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user_from_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token
    
    Returns None if no token provided or invalid
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            AuthService.verify_user_active(user)
        
        return user
        
    except (JWTError, HTTPException):
        return None


async def get_current_user_from_apikey(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from API key
    
    Returns None if no API key provided or invalid
    """
    if not api_key:
        return None
    
    api_key_obj = APIKeyService.validate_api_key(db, key=api_key)
    
    if not api_key_obj or not api_key_obj.user_id:
        return None
    
    user = db.query(User).filter(User.id == api_key_obj.user_id).first()
    if user:
        AuthService.verify_user_active(user)
    
    return user


# Authentication dependencies for different requirements

async def get_current_user_jwt_required(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Require JWT authentication only"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_current_user_from_jwt(credentials, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_apikey_required(
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """Require API key authentication only"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    user = await get_current_user_from_apikey(api_key, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )
    
    return user


async def get_current_user_either(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """Allow either JWT or API key authentication"""
    # Try API key first
    if api_key:
        user = await get_current_user_from_apikey(api_key, db)
        if user:
            return user
    
    # Try JWT
    if credentials:
        user = await get_current_user_from_jwt(credentials, db)
        if user:
            return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid JWT token or API key required",
    )


# Authorization dependencies

def require_permissions(required_permissions: List[str]):
    """
    Dependency factory to check if user has required permissions
    
    Usage:
        @router.get("/endpoint", dependencies=[Depends(require_permissions(["users:read"]))])
    """
    async def permission_checker(
        credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
        api_key: Optional[str] = Security(api_key_header),
        db: Session = Depends(get_db)
    ):
        user_permissions = set()
        
        # Check API key permissions
        if api_key:
            api_key_obj = APIKeyService.validate_api_key(db, key=api_key)
            if api_key_obj:
                # Direct permissions
                user_permissions.update(p.name for p in api_key_obj.permissions)
                # Role-based permissions
                for role in api_key_obj.roles:
                    user_permissions.update(p.name for p in role.permissions)
        
        # Check JWT permissions
        if credentials and not user_permissions:
            try:
                payload = decode_access_token(credentials.credentials)
                user_permissions.update(payload.get("permissions", []))
            except JWTError:
                pass
        
        # Check if user has all required permissions
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {required_permissions}",
            )
        
        return True
    
    return permission_checker


def require_roles(required_roles: List[str]):
    """
    Dependency factory to check if user has required roles
    
    Usage:
        @router.get("/endpoint", dependencies=[Depends(require_roles(["admin"]))])
    """
    async def role_checker(
        credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
        api_key: Optional[str] = Security(api_key_header),
        db: Session = Depends(get_db)
    ):
        user_roles = set()
        
        # Check API key roles
        if api_key:
            api_key_obj = APIKeyService.validate_api_key(db, key=api_key)
            if api_key_obj:
                user_roles.update(r.name for r in api_key_obj.roles)
        
        # Check JWT roles
        if credentials and not user_roles:
            try:
                payload = decode_access_token(credentials.credentials)
                user_roles.update(payload.get("roles", []))
            except JWTError:
                pass
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required roles: {required_roles}",
            )
        
        return True
    
    return role_checker

