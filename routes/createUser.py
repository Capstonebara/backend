from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database import models, crud
from database.database import SessionLocal, engine
from passlib.context import CryptContext

from pydantic import BaseModel

import secrets

users = APIRouter()
accounts = APIRouter()

# Tạo tất cả các bảng trong CSDL
models.Base.metadata.create_all(bind=engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# @users.post("/users/")
# def create_user(name: str, email: str, db: Session = Depends(get_db)):
#     return crud.create_user(db=db, name=name, email=email.lower())

# @users.delete("/users/")
# def delete_user(email: str, db: Session = Depends(get_db)):
#     result = crud.delete_user_by_email(db=db, email=email.lower())
#     return result

# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates

# # Set up Jinja2 templates
# templates = Jinja2Templates(directory="/home/capybara/be_webapp/app/templates/users")

# @users.get("/users-table", response_class=HTMLResponse)
# def get_users_table(db: Session = Depends(get_db)):
#     users = db.query(models.User).all()
    
#     return templates.TemplateResponse("users_table.html", {"request": {}, "users": users})


# Add this class for request validation
class Account(BaseModel):
    user: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@accounts.post("/register/")
def register_account(account: Account, db: Session = Depends(get_db)):
    return crud.create_account(
        db=db, 
        username=account.user, 
        password=account.password, 
        pwd_context=pwd_context
    )

@accounts.post("/login/")
def login(account: Account, db: Session = Depends(get_db)):
    verify = crud.verify_account(
        db=db, 
        username=account.user, 
        password=account.password, 
        pwd_context=pwd_context
    )

    if verify == "Account not found" or verify == "Incorrect password":
        return {
            "success": False,
            "message": verify
        }
    
    access_token = crud.create_access_token(
        username=account.user, 
        password=account.password, 
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES, 
        algorithm=ALGORITHM, 
        secret_key=SECRET_KEY
    )
    return {
        "access_token": access_token
    }