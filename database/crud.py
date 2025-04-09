from sqlalchemy.orm import Session
from . import models
from services import auth_service, db_service
import datetime
import jwt
import os
import time
from dotenv import load_dotenv


load_dotenv()
DOMAIN = os.getenv("DOMAIN")

# WebApp 
# Login
def login(db: Session, username: str, password: str, pwd_context, algorithm: str, secret_key: str, access_token_expire_minutes: int):
    # Verify account
    account = db.query(models.Account).filter(models.Account.user == username).first()
    if not account:
        return {"success": False, "message": "Account not found"}
    
    if not pwd_context.verify(password, account.password):
        return {"success": False, "message": "Incorrect password"}

    
    # Create access token
    to_encode = {"sub": username, "password": password, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=access_token_expire_minutes)}
    access_token = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    #Login time
    account.last_login = int(datetime.datetime.now().timestamp())
    db.commit()
    
    return {
        "success": True,
        "message": "Login successful",
        "token": access_token
    }

#get phone number
def get_phone_number(db:Session, username:str ,token:str, secret_key:str, algorithm:str):
    username_exists = auth_service.decode_access_token(db=db, token=token, secret_key=secret_key, algorithm=algorithm)
    if not auth_service.check_username_exists(db, username_exists) or username_exists != username:
        return None
    # Query all residents matching the username
    residents = db.query(models.Resident).filter(
        models.Resident.user_name == username
    ).all()
        
    if residents:
        # Return list of phone numbers
        return [resident.phone for resident in residents]
    return []


# CMS
# Create account
def create_account(db: Session, account: models.AccountData, pwd_context):
    # Check if username already exists
    existing_account = db.query(models.Account).filter(models.Account.user == account.user).first()
    if existing_account:
        return {"success": False, "message": "Username already exists"} 
    # Hash the password
    hashed_password = pwd_context.hash(account.password)
    # get smallest ID
    id = db_service.get_id(db, "accounts")
    # Create new account
    db_account = models.Account(
        id=id,
        user=account.user,
        password=hashed_password, 
        status = True,
        member = len(db.query(models.Resident).filter(models.Resident.user_name == account.user).all()),
        created_time=int(datetime.datetime.now().timestamp()),  # Ensure timestamp is cast to an integer
        last_login=int(0)
    )
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return {"success": True, "message": "Account created successfully", "id": db_account.id}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
        
def get_all_accounts(db: Session):
    accounts = db.query(models.Account).all()
    info = []
    for account in accounts:
        data = {
            "id": account.id,
            "username": account.user,
            "status": account.status,
            "member": account.member,
            "created_time": account.created_time,
            "last_login": account.last_login
        }
        info.append(data)
    return info

def delete_account_by_id(db: Session, account_id: int):
    db_account = auth_service.check_id_exists(db, account_id, "accounts")
    if not db_account:
        return {"success": False, "message": "Account not found"}
    
    # Delete all residents associated with the account
    residents = db.query(models.Resident).filter(models.Resident.user_name == db_account.user).all()
    for resident in residents:
        try:
            db.delete(resident)
            db_service.delete_resident_image(resident.id)
        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"Error deleting resident {resident.id}: {str(e)}"}
    
    try:
        # Delete the account
        db.delete(db_account)
        db.commit()
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    
    return {"success": True, "message": "Account and associated residents deleted successfully"}


# Both
# get all residents infomation
def get_residents_data(role: str, db: Session, username: str = None, token: str = None, secret_key: str = None, algorithm: str = None):
    if role == "resident":
        if not auth_service.check_valid_token(db, token, secret_key, algorithm, username):
            return {"success": False, "message": "Invalid token"}
        residents = db.query(models.Resident).filter(models.Resident.user_name == username).all()
        if not residents:
            return {"success": False, "message": "User not found"}
    elif role == "admin":
        residents = db.query(models.Resident).all()

    info = []
    for resident in residents:

        photo_path = f'/data/pics/{resident.id}/main.jpg'
        if os.path.exists(f'./data/pics/{resident.id}'):
            photo_url = DOMAIN + photo_path
        else:
            photo_url = ""

        data = {
            "id": resident.id,
            "username": resident.user_name,
            "name": resident.name,
            "apartment": resident.apartment_number,
            "gender": resident.gender,
            "phone": resident.phone,
            "email": resident.email,
            "photoUrl": photo_url
        }
        info.append(data)
    return info
    
# Create resident
def create_new_resident(resident: models.ResidentsData, db: Session, role: str="resident", token: str = None, secret_key: str = None, algorithm: str = None):
    if role == "resident":
        # check valid token
        if not auth_service.check_valid_token(db, token, secret_key, algorithm, resident.username):
            return {"success": False, "message": "Invalid token"}
    
    id = db_service.get_id(db, "residents")
    account = auth_service.check_username_exists(db, resident.username)
    if not account:
        return {"success": False, "message": "Username does not exist. Create an account first."}

    # Create new user
    db_user = models.Resident(
        id=id,
        user_name=resident.username,
        name=resident.name,
        apartment_number=resident.apartment_number,
        gender=resident.gender,
        phone=resident.phone,
        email=resident.email.lower()
    )
    try:
        db.add(db_user)
        db.flush()
        db_service.update_account_member(db, account)
        return {"success": True, "message": "User created successfully", "id": db_user.id}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    
# Delete resident by ID
def delete_resident_by_id(db: Session, user_id: int, role:str="resident",token: str=None, secret_key: str=None, algorithm: str=None):
    db_user = auth_service.check_id_exists(db, user_id, "residents")
    if not db_user:
        return {"success": False, "message": "User not found"}

    if role == "resident":
        if not auth_service.check_valid_token(db, token, secret_key, algorithm, db_user.user_name):
            return {"success": False, "message": "Invalid token"}
        
    try:
        db.delete(db_user)
        db.flush()
        db_service.update_account_member(db, auth_service.check_username_exists(db,db_user.user_name))
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    db_service.delete_resident_image(user_id)
    return {"success": True, "message": "User deleted successfully"}

# Update Resident data by ID
def update_resident_data_by_id(db: Session, resident_id: int, user: models.ResidentsData, role="resident",token: str=None, secret_key: str=None, algorithm: str=None):
    db_user = auth_service.check_id_exists(db, resident_id, "residents")
    if not db_user:
        return {"success": False, "message": "User not found"}

    if role == "resident":
        if not auth_service.check_valid_token(db, token, secret_key, algorithm, db_user.user_name):
            return {"success": False, "message": "Invalid token"}

    
    try:
        # Convert Pydantic model to dict and exclude unset values
        update_data = user.dict(exclude_unset=True)
        
        # Map Pydantic field names to SQLAlchemy model field names
        field_mapping = {"username": "user_name"}
        
        # Update only the fields that were provided
        for key, value in update_data.items():
            field_name = field_mapping.get(key, key)
            setattr(db_user, field_name, value)
        
        db.commit()
        return {"success": True, "message": "User updated successfully"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    

def add_logs_to_db(db: Session, username: str, device_id: str, name: str, timestamp: int, type: str, apartment: str):

    id = db_service.get_id(db, "logs")

    db_log = models.Logs(
        id=id,
        username=username,
        device_id=device_id,
        name=name,
        timestamp=timestamp,
        type=type,
        apartment=apartment
    )
    try:
        db.add(db_log)
        db.commit()
        return db_log.id
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}

    
def recent_logs(db: Session, day: datetime.date = None):
    query = db.query(models.Logs)
    
    if day:
        start_of_day = datetime.datetime.combine(day, datetime.time.min)
        end_of_day = datetime.datetime.combine(day, datetime.time.max)
        query = query.filter(models.Logs.timestamp >= start_of_day.timestamp(), models.Logs.timestamp <= end_of_day.timestamp())
    
    logs = query.order_by(models.Logs.timestamp.desc()).all()
    info = []
    for log in logs:
        data = {
            "id": log.id,
            "device_id": log.device_id,
            "name": log.name,
            "photoUrl": log.photoUrl,
            "timestamp": log.timestamp,
            "type": log.type,
            "apartment": log.apartment
        }
        info.append(data)
    return info

def get_logs_by_day(db: Session):
    logs = db.query(models.Logs).order_by(models.Logs.timestamp.desc()).all()
    grouped_logs = {"Today": []}

    now = datetime.datetime.now()
    today_start = datetime.datetime.combine(now.date(), datetime.time.min)
    yesterday_start = today_start - datetime.timedelta(days=1)

    for log in logs:
        log_data = {
            "id": log.id,
            "name": log.name,
            "photoUrl": log.photoUrl if log.photoUrl else "/placeholder.svg?height=40&width=40",
            "timestamp": log.timestamp,
            "type": log.type,
            "apartment": log.apartment,
            "device": log.device_id
        }

        log_time = datetime.datetime.fromtimestamp(log.timestamp)
        if log_time >= today_start:
            grouped_logs["Today"].append(log_data)
        elif log_time >= yesterday_start:
            if "Yesterday" not in grouped_logs:
                grouped_logs["Yesterday"] = []
            grouped_logs["Yesterday"].append(log_data)
        else:
            day_key = log_time.strftime("%Y-%m-%d")
            if day_key not in grouped_logs:
                grouped_logs[day_key] = []
            grouped_logs[day_key].append(log_data)

    if "Yesterday" in grouped_logs and not grouped_logs["Yesterday"]:
        del grouped_logs["Yesterday"]

    return grouped_logs

def get_logs_by_username(db: Session, username: str, token: str = None, secret_key: str = None, algorithm: str = None):
    # Authenticate user
    if not auth_service.check_valid_token(db, token, secret_key, algorithm, username):
        return {"success": False, "message": "Invalid token"}
        
    # Filter logs by username and order by timestamp in descending order
    logs = db.query(models.Logs).filter(models.Logs.username == username).order_by(models.Logs.timestamp.desc()).all()
    
    grouped_logs = {"Today": []}

    now = datetime.datetime.now()
    today_start = datetime.datetime.combine(now.date(), datetime.time.min)
    yesterday_start = today_start - datetime.timedelta(days=1)

    for log in logs:
        log_data = {
            "id": log.id,
            "name": log.name,
            "photoUrl": log.photoUrl if log.photoUrl else "/placeholder.svg?height=40&width=40",
            "timestamp": log.timestamp,
            "type": log.type,
            "apartment": log.apartment,
            "device": log.device_id
        }

        log_time = datetime.datetime.fromtimestamp(log.timestamp)
        if log_time >= today_start:
            grouped_logs["Today"].append(log_data)
        elif log_time >= yesterday_start:
            if "Yesterday" not in grouped_logs:
                grouped_logs["Yesterday"] = []
            grouped_logs["Yesterday"].append(log_data)
        else:
            day_key = log_time.strftime("%Y-%m-%d")
            if day_key not in grouped_logs:
                grouped_logs[day_key] = []
            grouped_logs[day_key].append(log_data)

    if "Yesterday" in grouped_logs and not grouped_logs["Yesterday"]:
        del grouped_logs["Yesterday"]

    return grouped_logs

def recent_logs_by_username(username: str, db: Session, day: datetime.date = None, token: str = None, secret_key: str = None, algorithm: str = None):
    # Authenticate user
    if not auth_service.check_valid_token(db, token, secret_key, algorithm, username):
        return {"success": False, "message": "Invalid token"}
    
    # Filter logs by username and order by timestamp in descending order
    query = db.query(models.Logs).filter(models.Logs.username == username)
    
    if day:
        start_of_day = datetime.datetime.combine(day, datetime.time.min)
        end_of_day = datetime.datetime.combine(day, datetime.time.max)
        query = query.filter(models.Logs.timestamp >= start_of_day.timestamp(), models.Logs.timestamp <= end_of_day.timestamp())
    
    logs = query.order_by(models.Logs.timestamp.desc()).all()
    info = []
    for log in logs:
        data = {
            "id": log.id,
            "device_id": log.device_id,
            "name": log.name,
            "timestamp": log.timestamp,
            "type": log.type,
            "apartment": log.apartment,
            "captured": DOMAIN + f"/data/logs/{log.id}.jpg"
        }
        info.append(data)
    return info

def get_logs_total(db: Session):
    # Get today's logs totals
    total_account = db.query(models.Account).count()
    total_resident = db.query(models.Resident).count()
    
    # Get today's date range
    today = datetime.date.today()
    start_of_day = datetime.datetime.combine(today, datetime.time.min)
    end_of_day = datetime.datetime.combine(today, datetime.time.max)
    
    # Filter queries by today's date
    entry_query = db.query(models.Logs).filter(
        models.Logs.type == "entry",
        models.Logs.timestamp >= start_of_day.timestamp(),
        models.Logs.timestamp <= end_of_day.timestamp()
    )
    
    exit_query = db.query(models.Logs).filter(
        models.Logs.type == "exit",
        models.Logs.timestamp >= start_of_day.timestamp(),
        models.Logs.timestamp <= end_of_day.timestamp()
    )
    
    total_entry = entry_query.count()
    total_exit = exit_query.count()

    return {
        'total_account': total_account,
        'total_resident': total_resident,
        'total_entry': total_entry,
        'total_exit': total_exit
    }

def get_logs_by_username_ws(db: Session, username: str, token: str = None, secret_key: str = None, algorithm: str = None):
    # Authenticate user
    if not auth_service.check_valid_token(db, token, secret_key, algorithm, username):
        return {"success": False, "message": "Invalid token"}
        
    # Get today's logs totals
    total_resident = db.query(models.Resident).filter(models.Resident.user_name == username).count()

    # Get today's date range
    today = datetime.date.today()
    start_of_day = datetime.datetime.combine(today, datetime.time.min)
    end_of_day = datetime.datetime.combine(today, datetime.time.max)
    
    # Filter queries by today's date and get counts
    total_entry = db.query(models.Logs).filter(
        models.Logs.username == username,
        models.Logs.type == "entry",
        models.Logs.timestamp >= start_of_day.timestamp(),
        models.Logs.timestamp <= end_of_day.timestamp()
    ).count()
    
    total_exit = db.query(models.Logs).filter(
        models.Logs.username == username,
        models.Logs.type == "exit",
        models.Logs.timestamp >= start_of_day.timestamp(),
        models.Logs.timestamp <= end_of_day.timestamp()
    ).count()

    return {
        'total_resident': total_resident,
        'total_entry': total_entry,
        'total_exit': total_exit
    }


def captured_pics():
    photo_path = f'/data/pics/sample-log.jpg'
    photo_url = DOMAIN + photo_path
    return photo_url