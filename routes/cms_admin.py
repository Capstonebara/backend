from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response

from sqlalchemy.orm import Session

from passlib.context import CryptContext

from database import models, crud
from database.database import SessionLocal, engine

admin = APIRouter()

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create a new account for resident
@admin.post("/register/")
def register_account(account: models.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(
        account=account,
        db=db,  
        pwd_context=pwd_context
    )

# Get all residents data
@admin.get("/admin/users_info")
def get_residents_data_admin(db: Session = Depends(get_db)):
    return crud.get_all_residents_data(db=db)

# Create a new resident data:
@admin.post("/admin/create")
def create_resident_data_admin(user: models.ResidentsCreate, db: Session = Depends(get_db)):
    return crud.create_resident_data(user=user, db=db)

# Delete a resident data:
@admin.delete("/admin/delete")
def delete_resident_data_admin(resident_id: int, db: Session = Depends(get_db)):
    return crud.delete_resident_data_by_id(resident_id=resident_id, db=db)

