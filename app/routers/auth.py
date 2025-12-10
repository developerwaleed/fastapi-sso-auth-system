from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, OAuthAccount
from app.schemas import LoginResponse, UserResponse, OAuthLoginURL
from app.auth import create_access_token
from app.oauth import oauth, get_google_user_info, get_github_user_info, normalize_user_data
from app.config import settings
from datetime import timedelta
import secrets


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/google/login", response_model=OAuthLoginURL)
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    state = secrets.token_urlsafe(32)
    
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured"
        )
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    authorization_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"redirect_uri={redirect_uri}&"
        f"state={state}"
    )
    
    return OAuthLoginURL(authorization_url=authorization_url, state=state)


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info
        user_info = await get_google_user_info(token)
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from Google"
            )
        
        # Normalize user data
        normalized_data = normalize_user_data('google', user_info)
        
        # Find or create user
        user = db.query(User).filter(User.email == normalized_data['email']).first()
        
        if not user:
            # Create new user
            user = User(
                email=normalized_data['email'],
                full_name=normalized_data['full_name'],
                avatar_url=normalized_data['avatar_url'],
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user.id,
            OAuthAccount.provider == 'google'
        ).first()
        
        if not oauth_account:
            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider='google',
                provider_user_id=normalized_data['provider_user_id'],
                access_token=token.get('access_token'),
                refresh_token=token.get('refresh_token'),
                provider_data=user_info
            )
            db.add(oauth_account)
            db.commit()
        
        # Generate JWT token
        roles = [role.name for role in user.roles]
        permissions = []
        for role in user.roles:
            permissions.extend([perm.name for perm in role.permissions])
        
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "roles": roles,
                "permissions": list(set(permissions))
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Return token (in production, redirect to frontend with token)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.get("/github/login", response_model=OAuthLoginURL)
async def github_login(request: Request):
    """Initiate GitHub OAuth login"""
    state = secrets.token_urlsafe(32)
    
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured"
        )
    
    redirect_uri = settings.GITHUB_REDIRECT_URI
    authorization_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={settings.GITHUB_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=user:email&"
        f"state={state}"
    )
    
    return OAuthLoginURL(authorization_url=authorization_url, state=state)


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    try:
        # Exchange code for token
        token = await oauth.github.authorize_access_token(request)
        
        # Get user info
        user_info = await get_github_user_info(token)
        if not user_info or not user_info.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from GitHub or email not available"
            )
        
        # Normalize user data
        normalized_data = normalize_user_data('github', user_info)
        
        # Find or create user
        user = db.query(User).filter(User.email == normalized_data['email']).first()
        
        if not user:
            # Create new user
            user = User(
                email=normalized_data['email'],
                full_name=normalized_data['full_name'],
                avatar_url=normalized_data['avatar_url'],
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Check if OAuth account exists
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.user_id == user.id,
            OAuthAccount.provider == 'github'
        ).first()
        
        if not oauth_account:
            # Create OAuth account link
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider='github',
                provider_user_id=normalized_data['provider_user_id'],
                access_token=token.get('access_token'),
                refresh_token=token.get('refresh_token'),
                provider_data=user_info
            )
            db.add(oauth_account)
            db.commit()
        
        # Generate JWT token
        roles = [role.name for role in user.roles]
        permissions = []
        for role in user.roles:
            permissions.extend([perm.name for perm in role.permissions])
        
        access_token = create_access_token(
            data={
                "sub": user.id,
                "email": user.email,
                "roles": roles,
                "permissions": list(set(permissions))
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # Return token (in production, redirect to frontend with token)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    from app.auth import get_current_user_either
    user = await get_current_user_either(request=request, db=db)
    return user

