"""
Quick script to create a test user and API key for testing without OAuth
"""
import sys
sys.path.insert(0, '.')

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.api_key import APIKey
from app.models.permission import Permission

def create_test_user_and_key():
    db = SessionLocal()
    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            # Create test user
            test_user = User(
                email="test@example.com",
                full_name="Test User",
                is_active=True,
                is_superuser=False
            )
            
            # Assign admin role
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                test_user.roles.append(admin_role)
            
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created test user: {test_user.email}")
        else:
            print(f"ℹ️  Test user already exists: {test_user.email}")
        
        # Create API key for this user
        api_key = APIKey(
            user_id=test_user.id,
            key=APIKey.generate(),
            name="Test API Key",
            description="API key for testing without OAuth",
            is_active=True
        )
        
        # Add admin role to API key
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role:
            api_key.roles.append(admin_role)
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        print("\n" + "="*60)
        print("🎉 TEST API KEY CREATED!")
        print("="*60)
        print(f"\nAPI Key: {api_key.key}")
        print(f"\nUser: {test_user.email}")
        print(f"Roles: {[role.name for role in test_user.roles]}")
        print("\n📋 Copy this API key and use it in Postman:")
        print(f"\nX-API-Key: {api_key.key}")
        print("\n" + "="*60)
        print("\n✅ You can now test all endpoints that accept API key authentication!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user_and_key()

