import os
from fastapi import APIRouter, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from passlib.context import CryptContext


from database import models, crud
from database.database import SessionLocal, engine

load_dotenv()
auth = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="Bearer"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")


@auth.post("/login")
def login_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    result = crud.login(
        db=db,
        username=form_data.username,
        password=form_data.password,
        pwd_context=pwd_context,
        algorithm=ALGORITHM,
        secret_key=SECRET_KEY,
        access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    if result["success"]:
        response.headers["Authorization"] = f"Bearer {result['token']}"
        
    return {
        "success": result["success"],
        "message": result["message"]
    }

@auth.get("/checking_token")
def checking_token_expiration(
    token: str
):
    result = crud.check_token_expiration(
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return result

@auth.post("/register")
def register_account(account: models.AccountData, db: Session = Depends(get_db)):
    return crud.create_account(
        account=account,
        db=db,  
        pwd_context=pwd_context
    )


@auth.get("/change_password_admin")
def change_password_for_admin( username: str, new_password: str, db: Session = Depends(get_db)):
    return crud.change_password_for_admin(
        db=db,
        username=username,
        new_password=new_password,
        pwd_context=pwd_context
    )


@auth.get("/change_password_resident")
def change_password_for_resident( username: str, old_password: str, new_password: str, db: Session = Depends(get_db)):
    return crud.change_password_for_resident(
        db=db,
        username=username,
        old_password=old_password,
        new_password=new_password,
        pwd_context=pwd_context
    )   