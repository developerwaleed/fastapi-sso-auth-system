from authlib.integrations.starlette_client import OAuth
from app.core.config import settings
from app.core.constants import OAUTH_PROVIDER_GOOGLE, OAUTH_PROVIDER_GITHUB
from typing import Dict, Optional
import httpx


# Initialize OAuth
oauth = OAuth()

# Configure Google OAuth
if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
    oauth.register(
        name=OAUTH_PROVIDER_GOOGLE,
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Configure GitHub OAuth
if settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET:
    oauth.register(
        name=OAUTH_PROVIDER_GITHUB,
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={
            'scope': 'user:email read:user'
        }
    )


async def get_google_user_info(token: Dict) -> Optional[Dict]:
    """
    Fetch user info from Google
    
    Args:
        token: OAuth token dictionary
        
    Returns:
        User info dictionary or None if error
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f"Bearer {token['access_token']}"}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching Google user info: {e}")
        return None


async def get_github_user_info(token: Dict) -> Optional[Dict]:
    """
    Fetch user info from GitHub
    
    Args:
        token: OAuth token dictionary
        
    Returns:
        User info dictionary or None if error
    """
    try:
        async with httpx.AsyncClient() as client:
            # Get user profile
            response = await client.get(
                'https://api.github.com/user',
                headers={
                    'Authorization': f"Bearer {token['access_token']}",
                    'Accept': 'application/vnd.github.v3+json'
                }
            )
            response.raise_for_status()
            user_data = response.json()
            
            # Get primary email if not public
            if not user_data.get('email'):
                email_response = await client.get(
                    'https://api.github.com/user/emails',
                    headers={
                        'Authorization': f"Bearer {token['access_token']}",
                        'Accept': 'application/vnd.github.v3+json'
                    }
                )
                email_response.raise_for_status()
                emails = email_response.json()
                primary_email = next((e for e in emails if e['primary']), None)
                if primary_email:
                    user_data['email'] = primary_email['email']
            
            return user_data
    except Exception as e:
        print(f"Error fetching GitHub user info: {e}")
        return None


def normalize_user_data(provider: str, user_info: Dict) -> Dict:
    """
    Normalize user data from different OAuth providers
    
    Args:
        provider: OAuth provider name
        user_info: Raw user info from provider
        
    Returns:
        Normalized user data dictionary
    """
    if provider == OAUTH_PROVIDER_GOOGLE:
        return {
            'email': user_info.get('email'),
            'full_name': user_info.get('name'),
            'avatar_url': user_info.get('picture'),
            'provider_user_id': user_info.get('sub'),  # Google uses 'sub' not 'id'
        }
    elif provider == OAUTH_PROVIDER_GITHUB:
        return {
            'email': user_info.get('email'),
            'full_name': user_info.get('name') or user_info.get('login'),
            'avatar_url': user_info.get('avatar_url'),
            'provider_user_id': str(user_info.get('id')),
        }
    else:
        return {}

