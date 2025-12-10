from pydantic import BaseModel
from datetime import datetime


class OAuthAccountResponse(BaseModel):
    id: int
    provider: str
    provider_user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

