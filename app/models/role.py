from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Role(Base):
    """Role model for grouping permissions"""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles"
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
        lazy="selectin"
    )
    api_keys = relationship(
        "APIKey",
        secondary="apikey_roles",
        back_populates="roles"
    )
    
    def __repr__(self):
        return f"<Role {self.name}>"

