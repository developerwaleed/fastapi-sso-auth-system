from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
from app.core.constants import DEFAULT_PERMISSIONS, DEFAULT_ROLES

# Import models after Base is defined to avoid circular imports
from app.models.permission import Permission
from app.models.role import Role


def init_db(db: Session) -> None:
    """
    Initialize database with default data
    
    Args:
        db: Database session
    """
    # Import all models first
    from app.models import *  # noqa
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create default permissions
    for perm_data in DEFAULT_PERMISSIONS:
        perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not perm:
            perm = Permission(
                name=perm_data["name"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                description=f"{perm_data['action'].title()} {perm_data['resource']}"
            )
            db.add(perm)
    
    db.commit()
    
    # Create default roles with permissions
    users_read = db.query(Permission).filter(Permission.name == "users:read").first()
    users_write = db.query(Permission).filter(Permission.name == "users:write").first()
    users_delete = db.query(Permission).filter(Permission.name == "users:delete").first()
    posts_read = db.query(Permission).filter(Permission.name == "posts:read").first()
    posts_write = db.query(Permission).filter(Permission.name == "posts:write").first()
    posts_delete = db.query(Permission).filter(Permission.name == "posts:delete").first()
    analytics_read = db.query(Permission).filter(Permission.name == "analytics:read").first()
    
    # Admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin",
            description="Administrator with full access"
        )
        admin_role.permissions = [
            users_read, users_write, users_delete,
            posts_read, posts_write, posts_delete,
            analytics_read
        ]
        db.add(admin_role)
    
    # User role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_role = Role(
            name="user",
            description="Regular user with basic access"
        )
        user_role.permissions = [users_read, posts_read, posts_write]
        db.add(user_role)
    
    # Viewer role
    viewer_role = db.query(Role).filter(Role.name == "viewer").first()
    if not viewer_role:
        viewer_role = Role(
            name="viewer",
            description="Viewer with read-only access"
        )
        viewer_role.permissions = [users_read, posts_read]
        db.add(viewer_role)
    
    db.commit()

