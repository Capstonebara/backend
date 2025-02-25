from sqlalchemy.orm import Session
from . import models


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