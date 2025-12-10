from typing import Optional, Dict
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.oauth import OAuthAccount
from app.crud.user import user as user_crud
from app.schemas.user import UserCreate


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def create_user_token(user: User) -> str:
        """
        Create JWT token for user with roles and permissions
        
        Args:
            user: User model instance
            
        Returns:
            JWT token string
        """
        # Collect all permissions from user's roles
        permissions = set()
        for role in user.roles:
            for perm in role.permissions:
                permissions.add(perm.name)
        
        token_data = {
            "sub": user.id,
            "email": user.email,
            "roles": [role.name for role in user.roles],
            "permissions": list(permissions)
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return access_token
    
    @staticmethod
    def create_or_get_user_from_oauth(
        db: Session,
        *,
        provider: str,
        email: str,
        full_name: Optional[str],
        avatar_url: Optional[str],
        provider_user_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        provider_data: Optional[Dict] = None
    ) -> User:
        """
        Create or get existing user from OAuth data
        
        Args:
            db: Database session
            provider: OAuth provider name
            email: User email
            full_name: User full name
            avatar_url: User avatar URL
            provider_user_id: Provider's user ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            provider_data: Additional provider data
            
        Returns:
            User model instance
        """
        # Check if user exists by email
        user = user_crud.get_by_email(db, email=email)
        
        if not user:
            # Create new user with default 'user' role
            user_data = UserCreate(
                email=email,
                full_name=full_name or email.split("@")[0]
            )
            user = user_crud.create_with_role(
                db,
                obj_in=user_data,
                role_name="user"
            )
            user.avatar_url = avatar_url
            db.commit()
            db.refresh(user)
        
        # Check if OAuth account exists for this user and provider
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user.id,
            OAuthAccount.provider == provider
        ).first()
        
        if not oauth_account:
            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                provider_data=provider_data
            )
            db.add(oauth_account)
            db.commit()
        else:
            # Update existing OAuth account
            oauth_account.access_token = access_token
            if refresh_token:
                oauth_account.refresh_token = refresh_token
            if provider_data:
                oauth_account.provider_data = provider_data
            db.commit()
        
        return user
    
    @staticmethod
    def verify_user_active(user: User) -> None:
        """
        Verify that user is active
        
        Args:
            user: User model instance
            
        Raises:
            HTTPException: If user is not active
        """
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

