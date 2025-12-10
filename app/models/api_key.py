from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.core.security import generate_api_key


class APIKey(Base):
    """API Key model for programmatic access"""
    
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    key = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    roles = relationship(
        "Role",
        secondary="apikey_roles",
        back_populates="api_keys",
        lazy="selectin"
    )
    permissions = relationship(
        "Permission",
        secondary="apikey_permissions",
        back_populates="api_keys",
        lazy="selectin"
    )
    
    @staticmethod
    def generate():
        """Generate a new API key"""
        return generate_api_key()
    
    def __repr__(self):
        return f"<APIKey {self.name}>"
    
    @property
    def all_permissions(self):
        """Get all permissions (direct + from roles)"""
        perms = list(self.permissions)
        for role in self.roles:
            perms.extend(role.permissions)
        return list(set(perms))  # Remove duplicates

