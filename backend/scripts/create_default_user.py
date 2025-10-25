"""
Create a default user for single-user setup.
Run this script once to initialize the database with a default user.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uuid import UUID
from app.db.base import SessionLocal
from app.models.user import User

# Use a consistent UUID for the default user
DEFAULT_USER_ID = UUID("e6bca6a4-5e3b-4877-837b-750a55f1e527")
DEFAULT_USER_EMAIL = "default@pettraining.local"


def create_default_user():
    """Create the default user if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.id == DEFAULT_USER_ID).first()
        
        if existing_user:
            print(f"✓ Default user already exists: {existing_user.email}")
            return existing_user
        
        # Create new default user
        user = User(
            id=DEFAULT_USER_ID,
            email=DEFAULT_USER_EMAIL,
            role="owner"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✓ Created default user: {user.email} (ID: {user.id})")
        return user
        
    except Exception as e:
        print(f"✗ Error creating default user: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_default_user()
