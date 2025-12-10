"""
Seed script to populate database with initial data for testing
"""
from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.api_key import APIKey
from sqlalchemy.orm import Session


def create_permissions(db: Session):
    """Create default permissions"""
    permissions = [
        Permission(name="users:read", description="Read user data", resource="users", action="read"),
        Permission(name="users:write", description="Write user data", resource="users", action="write"),
        Permission(name="users:delete", description="Delete users", resource="users", action="delete"),
        Permission(name="posts:read", description="Read posts", resource="posts", action="read"),
        Permission(name="posts:write", description="Write posts", resource="posts", action="write"),
        Permission(name="posts:delete", description="Delete posts", resource="posts", action="delete"),
        Permission(name="analytics:read", description="Read analytics", resource="analytics", action="read"),
    ]
    
    for perm in permissions:
        existing = db.query(Permission).filter(Permission.name == perm.name).first()
        if not existing:
            db.add(perm)
            print(f"Created permission: {perm.name}")
    
    db.commit()


def create_roles(db: Session):
    """Create default roles with permissions"""
    # Get permissions
    users_read = db.query(Permission).filter(Permission.name == "users:read").first()
    users_write = db.query(Permission).filter(Permission.name == "users:write").first()
    users_delete = db.query(Permission).filter(Permission.name == "users:delete").first()
    posts_read = db.query(Permission).filter(Permission.name == "posts:read").first()
    posts_write = db.query(Permission).filter(Permission.name == "posts:write").first()
    posts_delete = db.query(Permission).filter(Permission.name == "posts:delete").first()
    analytics_read = db.query(Permission).filter(Permission.name == "analytics:read").first()
    
    # Admin role - all permissions
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
        print("Created role: admin")
    
    # User role - basic permissions
    user_role = db.query(Role).filter(Role.name == "user").first()
    if not user_role:
        user_role = Role(
            name="user",
            description="Regular user with basic access"
        )
        user_role.permissions = [users_read, posts_read, posts_write]
        db.add(user_role)
        print("Created role: user")
    
    # Viewer role - read-only
    viewer_role = db.query(Role).filter(Role.name == "viewer").first()
    if not viewer_role:
        viewer_role = Role(
            name="viewer",
            description="Viewer with read-only access"
        )
        viewer_role.permissions = [users_read, posts_read]
        db.add(viewer_role)
        print("Created role: viewer")
    
    db.commit()


def create_test_users(db: Session):
    """Create test users"""
    # Test user 1
    test_user1 = db.query(User).filter(User.email == "admin@example.com").first()
    if not test_user1:
        test_user1 = User(
            email="admin@example.com",
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            test_user1.roles.append(admin_role)
        db.add(test_user1)
        print("Created user: admin@example.com")
    
    # Test user 2
    test_user2 = db.query(User).filter(User.email == "user@example.com").first()
    if not test_user2:
        test_user2 = User(
            email="user@example.com",
            full_name="Regular User",
            is_active=True
        )
        user_role = db.query(Role).filter(Role.name == "user").first()
        if user_role:
            test_user2.roles.append(user_role)
        db.add(test_user2)
        print("Created user: user@example.com")
    
    db.commit()
    return test_user1, test_user2


def create_test_api_keys(db: Session, user: User):
    """Create test API keys"""
    # Check if API key already exists
    existing_key = db.query(APIKey).filter(APIKey.name == "Test Admin API Key").first()
    if not existing_key:
        api_key = APIKey(
            user_id=user.id,
            key=APIKey.generate_key(),
            name="Test Admin API Key",
            description="API key with admin permissions for testing",
            is_active=True
        )
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            api_key.roles.append(admin_role)
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        print(f"\nCreated API Key: {api_key.name}")
        print(f"Key: {api_key.key}")
        print("Save this key - it won't be shown again!\n")
        return api_key


def seed_database():
    """Main seed function"""
    db = SessionLocal()
    try:
        print("Seeding database with initial data...\n")
        
        create_permissions(db)
        create_roles(db)
        admin_user, regular_user = create_test_users(db)
        create_test_api_keys(db, admin_user)
        
        print("\nDatabase seeded successfully!")
        print("\nTest Users Created:")
        print("1. admin@example.com (Admin role)")
        print("2. user@example.com (User role)")
        print("\nYou can login with these users via Google/GitHub OAuth")
        print("or use the generated API key for testing.\n")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

