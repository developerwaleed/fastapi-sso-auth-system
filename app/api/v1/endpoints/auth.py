from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import LoginResponse, OAuthLoginURL
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.utils.oauth_providers import (
    oauth,
    get_google_user_info,
    get_github_user_info,
    normalize_user_data
)
from app.core.config import settings
from app.core.constants import OAUTH_PROVIDER_GOOGLE, OAUTH_PROVIDER_GITHUB
from app.api.deps import get_current_user_either
from app.models.user import User
import secrets
import httpx


router = APIRouter()


@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured"
        )
    
    # Use Authlib to generate the authorization URL (handles state automatically)
    # redirect_uri must match EXACTLY what's configured in Google Console
    return await oauth.google.authorize_redirect(request, settings.GOOGLE_REDIRECT_URI)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token (Authlib handles state validation automatically)
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info (Authlib includes it in the token for OpenID Connect)
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback: manually fetch user info if not included
            user_info = await get_google_user_info(token)
        
        # Convert Authlib UserInfo object to dict if needed
        if hasattr(user_info, '__dict__'):
            user_info_dict = dict(user_info)
        else:
            user_info_dict = user_info
        
        if not user_info_dict or not user_info_dict.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from Google"
            )
        
        # Normalize user data
        normalized_data = normalize_user_data(OAUTH_PROVIDER_GOOGLE, user_info_dict)
        
        # Create or get user
        user = AuthService.create_or_get_user_from_oauth(
            db,
            provider=OAUTH_PROVIDER_GOOGLE,
            email=normalized_data['email'],
            full_name=normalized_data['full_name'],
            avatar_url=normalized_data['avatar_url'],
            provider_user_id=normalized_data['provider_user_id'],
            access_token=token.get('access_token'),
            refresh_token=token.get('refresh_token'),
            provider_data=user_info_dict
        )
        
        # Generate JWT token
        access_token = AuthService.create_user_token(user)
        
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


@router.get("/github/login")
async def github_login(request: Request):
    """Initiate GitHub OAuth login"""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="GitHub OAuth is not configured"
        )
    
    # Store state in session manually for GitHub
    state = secrets.token_urlsafe(32)
    request.session['github_oauth_state'] = state
    
    # Generate authorization URL manually
    redirect_uri = settings.GITHUB_REDIRECT_URI
    authorization_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={settings.GITHUB_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=user:email%20read:user&"
        f"state={state}"
    )
    
    # Redirect to GitHub
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=authorization_url)


@router.get("/github/callback")
async def github_callback(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    try:
        # Validate state manually
        stored_state = request.session.get('github_oauth_state')
        if not stored_state or stored_state != state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
        # Clear the state from session
        request.session.pop('github_oauth_state', None)
        
        # Exchange code for access token manually
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                'https://github.com/login/oauth/access_token',
                headers={'Accept': 'application/json'},
                data={
                    'client_id': settings.GITHUB_CLIENT_ID,
                    'client_secret': settings.GITHUB_CLIENT_SECRET,
                    'code': code,
                    'redirect_uri': settings.GITHUB_REDIRECT_URI
                }
            )
            token_data = token_response.json()
            
            if 'error' in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth error: {token_data.get('error_description', token_data['error'])}"
                )
        
        # Create token dict for compatibility
        token = {
            'access_token': token_data['access_token'],
            'token_type': token_data.get('token_type', 'bearer'),
            'scope': token_data.get('scope', '')
        }
        
        # Get user info from GitHub API
        user_info = await get_github_user_info(token)
        
        if not user_info or not user_info.get('email'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user info from GitHub or email not available"
            )
        
        # Normalize user data
        normalized_data = normalize_user_data(OAUTH_PROVIDER_GITHUB, user_info)
        
        # Create or get user
        user = AuthService.create_or_get_user_from_oauth(
            db,
            provider=OAUTH_PROVIDER_GITHUB,
            email=normalized_data['email'],
            full_name=normalized_data['full_name'],
            avatar_url=normalized_data['avatar_url'],
            provider_user_id=normalized_data['provider_user_id'],
            access_token=token.get('access_token'),
            refresh_token=token.get('refresh_token'),
            provider_data=user_info
        )
        
        # Generate JWT token
        access_token = AuthService.create_user_token(user)
        
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
    current_user: User = Depends(get_current_user_either)
):
    """Get current authenticated user info"""
    return current_user

