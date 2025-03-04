from sqlalchemy.orm import Session
from . import models
import jwt
import datetime



def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_status(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first().reg

def update_registration_status(db: Session, email: str, status: int = 1):
    db_user = db.query(models.User).filter(models.User.email == email.lower()).first()
    if db_user:
        db_user.reg = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_registration_reset(db: Session, email: str, status: int = 0):
    db_user = db.query(models.User).filter(models.User.email == email.lower()).first()
    if db_user:
        db_user.reg = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def create_user(db: Session, name: str, email: str):
    db_user = models.User(name=name, email=email.lower(), reg=False)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user_by_email(db: Session, email: str):
    db_user = db.query(models.User).filter(models.User.email == email.lower()).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found"}

def update_registration_le_status(db: Session, user_id: int, status: int = 1):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.le = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_registration_le_reset(db: Session, user_id: int, status: int = 0):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.le = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_registration_tiec_status(db: Session, user_id: int, status: int = 1):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.tiec = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_registration_tiec_reset(db: Session, user_id: int, status: int = 0):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.tiec = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_registration_cahai_status(db: Session, user_id: int, status: int = 1):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.cahai = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_registration_cahai_reset(db: Session, user_id: int, status: int = 0):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.cahai = status
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

# Create account
def create_account(db: Session, username: str, password: str, pwd_context):
    # Check if username already exists
    existing_account = db.query(models.Acount).filter(models.Acount.user == username).first()
    if existing_account:
        return {"success": False, "message": "Username already exists"}
    
    # Hash the password
    hashed_password = pwd_context.hash(password)
    
    # Create new account
    db_account = models.Acount(user=username, password=hashed_password)
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return {"success": True, "message": "Account created successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

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
def decode_access_token(token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        return username
    except:
        return None
    
def get_phone_number(db:Session, username:str ,token:str, secret_key:str, algorithm:str):
    username_exists = decode_access_token(token, secret_key, algorithm)
    if not check_username_exists(db, username_exists):
        return None
    # Query all residents matching the username
    residents = db.query(models.Resident).filter(
        models.Resident.user_name == username
    ).all()
        
    if residents:
        # Return list of phone numbers
        return [resident.phone for resident in residents]
    return []