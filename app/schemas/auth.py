from pydantic import BaseModel
from typing import Optional, List


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class OAuthLoginURL(BaseModel):
    authorization_url: str
    state: str


# Import here to avoid circular dependency
from app.schemas.user import UserResponse  # noqa
LoginResponse.model_rebuild()

