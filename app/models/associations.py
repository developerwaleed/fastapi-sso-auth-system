"""Association tables for many-to-many relationships"""

from sqlalchemy import Column, Integer, ForeignKey, Table
from app.db.base import Base


user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)

apikey_roles = Table(
    'apikey_roles',
    Base.metadata,
    Column('apikey_id', Integer, ForeignKey('api_keys.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

apikey_permissions = Table(
    'apikey_permissions',
    Base.metadata,
    Column('apikey_id', Integer, ForeignKey('api_keys.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)

