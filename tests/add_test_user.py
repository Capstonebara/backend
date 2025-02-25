import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import SessionLocal
from database import crud

from database.database import SessionLocal
from database import crud

def add_test_user():
    db = SessionLocal()
    try:
        # Test user data
        test_user = {
            "name": "TestUser",
            "email": "test@example.com"
        }
        
        # Check if user exists
        existing_user = crud.get_email(db, test_user["email"])
        if not existing_user:
            # Create new user
            new_user = crud.create_user(
                db=db, 
                name=test_user["name"], 
                email=test_user["email"]
            )
            print(f"Created user: {new_user.name} ({new_user.email})")
        else:
            print(f"User already exists: {test_user['email']}")
            
    finally:
        db.close()

if __name__ == "__main__":
    add_test_user()