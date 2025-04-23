from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .database import Base
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import DateTime

class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("accounts.username"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    apartment_number = Column(String, nullable=False, index=True)
    gender = Column(String, index=True)
    phone = Column(String, nullable=False, index=True)
    email = Column(String, index=True)

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, index=True)
    status = Column(Boolean, index=True)
    member = Column(Integer, index=True)
    created_time = Column(Integer, index=True)
    last_login = Column(Integer, index=True)

class AccountData(BaseModel):
    username: str
    password: str

class ResidentsData(BaseModel):
    username: str = None
    name: str = None
    apartment_number: str = None
    gender: str = None
    phone: str = None
    email: str = None


class Logs(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    device_id = Column(String, index=True)
    name = Column(String, index=True)
    timestamp = Column(Integer, index=True)
    type = Column(String, index=True)
    apartment = Column(String, index=True)
