from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
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

class AccessToken(BaseModel):
    token: str

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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    verify = crud.verify_account(
        db=db,
        username=form_data.username,
        password=form_data.password,
        pwd_context=pwd_context
    )

    if verify == "Account not found" or verify == "Incorrect password":
        return {
            "success": False,
            "message": verify
        }
    
    access_token = crud.create_access_token(
        username=form_data.username, 
        password=form_data.password, 
        expires_delta=ACCESS_TOKEN_EXPIRE_MINUTES, 
        algorithm=ALGORITHM, 
        secret_key=SECRET_KEY
    )
    return {
        "success": True,
        "access_token": access_token
    }

@accounts.post("/accounts/me")  # Changed from GET to POST since we're using request body
def get_username_from_token(request: AccessToken):
    username = crud.decode_access_token(request.token, SECRET_KEY, ALGORITHM)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": username}

@accounts.post("/accounts/phone")
def get_phone_number_from_username(username:str, request: AccessToken, db: Session = Depends(get_db)):
    phone = crud.get_phone_number(db=db, username= username ,token=request.token, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    if not phone:
        raise HTTPException(status_code=401, detail="Invalid token or Username does not exist")
    return {"phone": phone}
    