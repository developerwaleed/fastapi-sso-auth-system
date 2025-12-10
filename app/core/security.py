from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from app.core.config import settings
import secrets


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with expiration
    
    Args:
        data: Dictionary containing token payload
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload


def generate_api_key() -> str:
    """
    Generate a cryptographically secure API key
    
    Returns:
        URL-safe random string
    """
    return secrets.token_urlsafe(48)


def verify_token_payload(payload: dict, required_keys: List[str]) -> bool:
    """
    Verify that token payload contains required keys
    
    Args:
        payload: Decoded token payload
        required_keys: List of required keys
        
    Returns:
        True if all required keys are present
    """
    return all(key in payload for key in required_keys)

