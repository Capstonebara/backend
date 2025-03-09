from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import models, crud
from database.database import SessionLocal, engine
from passlib.context import CryptContext

from pydantic import BaseModel
import os

import secrets

# Load environment variables
load_dotenv()

users = APIRouter()
accounts = APIRouter()
residents = APIRouter()

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

class ResidentsCreate(BaseModel):
    username: str
    name: str
    apartment_number: str
    gender: str
    phone: str
    email: str

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="Bearer"  # This will show up in Swagger UI
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = secrets.token_hex(32)


@accounts.post("/register/")
def register_account(account: Account, db: Session = Depends(get_db)):
    return crud.create_account(
        db=db, 
        username=account.user, 
        password=account.password, 
        pwd_context=pwd_context
    )

@accounts.post("/login/")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    
    # Set the token in header
    response.headers["Authorization"] = f"Bearer {access_token}"
    
    return {
        "success": True,
        "message": "Login successful"
    }


@accounts.get("/accounts/me")
def get_username_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = crud.decode_access_token(db=db, token=token, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username}

@accounts.get("/accounts/phone")
def get_phone_number_from_username(
    username: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    phone = crud.get_phone_number(
        db=db,
        username=username,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    if not phone:
        raise HTTPException(
            status_code=401,
            detail="Invalid token or Username does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"phone": phone}


@residents.get("/residents/users")
def get_all_information_user(
    username: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    data = crud.get_information_by_username(
        db=db,
        username=username,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    if not data:
        raise HTTPException(
            status_code=401,
            detail="Invalid token or Username does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return data

@residents.post("/residents/create")
def create_new_user(user: ResidentsCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    result = crud.create_new_user(
        user=user,
        db=db,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return result

@residents.delete("/residents/delete")
def delete_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    result = crud.delete_user_by_id(db=db, user_id=user_id, token=token, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    return result
    
    