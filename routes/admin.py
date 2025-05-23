from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import models, crud
from database.database import SessionLocal

admin = APIRouter()

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Get all residents data
@admin.get("/admin/residents_info")
def get_residents_for_admin(db: Session = Depends(get_db)):
    return crud.get_residents_data(role = "admin", db=db)

# Create a new resident data:
@admin.post("/admin/create_resident")
def create_resident_for_admin(user: models.ResidentsData, db: Session = Depends(get_db)):
    return crud.create_new_resident(role = "admin", resident=user, db=db)

# Delete a resident data:
@admin.delete("/admin/delete_resident")
def delete_resident_for_admin(resident_id: int, db: Session = Depends(get_db)):
    return crud.delete_resident_by_id(role = "admin", user_id=resident_id, db=db)

# Update a resident data:
@admin.put("/admin/update_resident")
def update_resident_for_admin(resident_id: int, user: models.ResidentsData, db: Session = Depends(get_db)):
    return crud.update_resident_data_by_id(resident_id=resident_id, user=user, db=db, role="admin")

# Get all accounts
@admin.get("/admin/all_accounts")
def get_all_accounts_for_admin(db: Session = Depends(get_db)):
    return crud.get_all_accounts(db=db)

# Get account by id
@admin.delete("/admin/delete_account")
def delete_account_for_admin(account_id: int, db: Session = Depends(get_db)):
    return crud.delete_account_by_id(db=db, account_id=account_id)

@admin.put("/admin/update_account")
def update_account_status_for_admin(username: str, db: Session = Depends(get_db)):
    return crud.config_status_user(db=db, username=username)