from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import models, crud
from database.database import SessionLocal, engine
from passlib.context import CryptContext

import os


load_dotenv()
residents = APIRouter()
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

@residents.get("/residents/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = crud.decode_access_token(db=db, token=token, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": username}

@residents.get("/residents/phone")
def get_user_phone_number(
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


@residents.get("/residents/users_info")
def get_user_info(
    username: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    info = crud.get_residents_data(
        role = "resident",
        db=db,
        username=username,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return info

@residents.post("/residents/create")
def create_resident_for_user(user:models.ResidentsData, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    result = crud.create_new_resident(
        role = "resident",
        resident=user,
        db=db,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return result

@residents.delete("/residents/delete")
def delete_resident_for_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    result = crud.delete_resident_by_id(db=db, user_id=user_id, token=token, secret_key=SECRET_KEY, algorithm=ALGORITHM)
    return result

@residents.put("/residents/update")
def update_resident_for_user(user_id: int, user: models.ResidentsData, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return crud.update_resident_data_by_id(
        role="resident",
        resident_id=user_id,
        user=user,
        db=db,
        token=token,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    