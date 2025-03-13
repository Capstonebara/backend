from sqlalchemy.orm import Session
from . import models
import jwt
import datetime
from pydantic import BaseModel
import os
import shutil
import glob

# WebApp
# create access token    
def create_access_token(username:str, password:str, expires_delta: int, algorithm: str, secret_key: str):
    to_encode = {"sub": username, "password": password, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_delta)}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

# verify account
def verify_account(db:Session, username:str, password:str, pwd_context):
    account = db.query(models.Acount).filter(models.Acount.user == username).first()
    if not account:
        return "Account not found"
    
    if not pwd_context.verify(password, account.password):
        return "Incorrect password"

def check_username_exists(db:Session, username:str):
    account = db.query(models.Acount).filter(models.Acount.user == username).all()
    if account:
        return True
    return False

# decode access token    
def decode_access_token(db:Session, token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if not check_username_exists(db, username):
            return None
        return username
    except:
        return None
    
#get phone number
def get_phone_number(db:Session, username:str ,token:str, secret_key:str, algorithm:str):
    username_exists = decode_access_token(db=db, token=token, secret_key=secret_key, algorithm=algorithm)
    if not check_username_exists(db, username_exists) or username_exists != username:
        return None
    # Query all residents matching the username
    residents = db.query(models.Resident).filter(
        models.Resident.user_name == username
    ).all()
        
    if residents:
        # Return list of phone numbers
        return [resident.phone for resident in residents]
    return []

# get all information resident
def get_information_by_username(db: Session, username: str, token: str, secret_key: str, algorithm: str):
    username_exists = decode_access_token(db=db, token=token, secret_key=secret_key, algorithm=algorithm)
    if not check_username_exists(db, username_exists) or username_exists != username:
        return []

    residents = db.query(models.Resident).filter(models.Resident.user_name == username).all()
    if not residents:
        return []

    users = []
    for resident in residents:
        user = {
            "id": resident.id,
            "username": resident.user_name,
            "name": resident.name,
            "apartment": resident.apartment_number,
            "gender": resident.gender,
            "phone": resident.phone,
            "email": resident.email,
            "photoUrl": "/placeholder.svg?height=40&width=40"
        }
        users.append(user)
    
    return users
    
# create user
def create_new_resident(user: models.ResidentsCreate, db: Session, token: str, secret_key: str, algorithm: str):
    # Decode the token to get the username
    username_exists = decode_access_token(db=db, token=token, secret_key=secret_key, algorithm=algorithm)
    if not check_username_exists(db, username_exists):
        return {"success": False, "message": "Invalid token"}
    
    # Get all existing IDs
    existing_ids = [id[0] for id in db.query(models.Resident.id).order_by(models.Resident.id).all()]
    
    # Find the smallest available ID
    next_id = None
    if existing_ids:
        for expected_id in range(1, existing_ids[-1] + 1):
            if expected_id not in existing_ids:
                next_id = expected_id
                break

    # Create new user
    db_user = models.Resident(
        id=next_id,
        user_name=user.username,
        name=user.name,
        apartment_number=user.apartment_number,
        gender=user.gender,
        phone=user.phone,
        email=user.email.lower()
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"success": True, "message": "User created successfully", "id": db_user.id}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    
# delete user
def delete_resident_by_id(db: Session, user_id: int, token: str, secret_key: str, algorithm: str):
    username_exists = decode_access_token(db=db, token=token, secret_key=secret_key, algorithm=algorithm)
    if not check_username_exists(db, username_exists):
        return {"success": False, "message": "Invalid token"}
    
    # Get base data directory path
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    
    db_user = db.query(models.Resident).filter(models.Resident.id == user_id).first()
    if db_user:
        if os.path.exists(base_path):
            for subfolder in os.listdir(base_path):
                subfolder_path = os.path.join(base_path, subfolder)
                if os.path.isdir(subfolder_path):
                    user_path_patterns = [
                        os.path.join(subfolder_path, str(user_id)),  # Direct match
                        os.path.join(subfolder_path, f"{user_id}.*")  # Files with extensions
                    ]
                    for pattern in user_path_patterns:
                        matching_paths = glob.glob(pattern)
                        for path in matching_paths:
                            try:
                                if os.path.isfile(path):
                                    os.remove(path)
                                else:
                                    shutil.rmtree(path)
                            except Exception as e:
                                print(f"Error deleting {path}: {str(e)}")
    
        if username_exists != db_user.user_name:
            return {"success": False, "message": "Unauthorized"}
        db.delete(db_user)
        db.commit()
        return {"success": True, "message": "User deleted successfully"}
    else:
        return {"success": False, "message": "User not found"}
    
# CMS
# Create account
def create_account(db: Session, account: models.AccountCreate, pwd_context):
    # Check if username already exists
    existing_account = db.query(models.Acount).filter(models.Acount.user == account.user).first()
    if existing_account:
        return {"success": False, "message": "Username already exists"}
    
    # Hash the password
    hashed_password = pwd_context.hash(account.password)
    
    # Create new account
    db_account = models.Acount(user=account.user, password=hashed_password)
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return {"success": True, "message": "Account created successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    
# Get all residents data
def get_all_residents_data(db:Session):
    residents = db.query(models.Resident).all()
    info = []
    for resident in residents:
        data = {
            "id": resident.id,
            "username": resident.user_name,
            "name": resident.name,
            "apartment": resident.apartment_number,
            "gender": resident.gender,
            "phone": resident.phone,
            "email": resident.email,
            "photoUrl": "/placeholder.svg?height=40&width=40"
        }
        info.append(data)
    return info

# Create Resident info
def create_resident_data(user:models.ResidentsCreate, db:Session):
    # Get all existing IDs
    existing_ids = [id[0] for id in db.query(models.Resident.id).order_by(models.Resident.id).all()]
    
    # Find the smallest available ID
    next_id = None
    if existing_ids:
        for expected_id in range(1, existing_ids[-1] + 1):
            if expected_id not in existing_ids:
                next_id = expected_id
                break
    if not check_username_exists(db, user.username):
        return {"success": False, "message": "Username does not exist. Create an account first."}
    
    # Create new user
    db_user = models.Resident(
        id=next_id,
        user_name=user.username,
        name=user.name,
        apartment_number=user.apartment_number,
        gender=user.gender,
        phone=user.phone,
        email=user.email.lower()
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"success": True, "message": "User created successfully", "id": db_user.id}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

# Delete Resident data by ID
def delete_resident_data_by_id(db: Session, resident_id: int):
    db_user = db.query(models.Resident).filter(models.Resident.id == resident_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"success": True, "message": "User deleted successfully"}
    else:
        return {"success": False, "message": "User not found"}