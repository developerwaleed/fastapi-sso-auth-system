from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Permission(Base):
    """Permission model for fine-grained access control"""
    
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    resource = Column(String(50), nullable=True, index=True)  # e.g., 'users', 'posts'
    action = Column(String(50), nullable=True, index=True)    # e.g., 'read', 'write'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )
    api_keys = relationship(
        "APIKey",
        secondary="apikey_permissions",
        back_populates="permissions"
    )
    
    def __repr__(self):
        return f"<Permission {self.name}>"

