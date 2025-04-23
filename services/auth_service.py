from sqlalchemy.orm import Session
from database import models
import jwt
import datetime
# import os
# import shutil
# import glob
def check_username_exists(db: Session, username: str):
    account = db.query(models.Account).filter(models.Account.username == username).first()
    return account if account else False

def check_id_exists(db: Session, id: int, table: str):
    if table == "residents":
        user = db.query(models.Resident).filter(models.Resident.id == id).first()
    elif table == "accounts":
        user = db.query(models.Account).filter(models.Account.id == id).first()
    return user if user else False

def decode_access_token(db: Session, token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if not check_username_exists(db, username):
            return None
        return username
    except:
        return None

def check_valid_token(db: Session, token: str, secret_key: str, algorithm: str, username: str):
    username_exists = decode_access_token(db=db, token=token, secret_key=secret_key, algorithm=algorithm)
    if not check_username_exists(db, username_exists) or username_exists != username:
        return False
    return True