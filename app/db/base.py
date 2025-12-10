from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic to detect them
# These imports are done at the bottom to avoid circular imports
def import_models():
    """Import all models - call this only when needed (e.g., for Alembic)"""
    from app.models.user import User  # noqa
    from app.models.oauth import OAuthAccount  # noqa
    from app.models.api_key import APIKey  # noqa
    from app.models.role import Role  # noqa
    from app.models.permission import Permission  # noqa
    from app.models.associations import (  # noqa
        user_roles,
        role_permissions,
        apikey_roles,
        apikey_permissions
    )

