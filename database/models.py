from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from .database import Base
from pydantic import BaseModel


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    reg = Column(Boolean, index=True)
    le = Column(Boolean, index=True)
    tiec = Column(Boolean, index=True)
    cahai = Column(Boolean, index=True)

class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, ForeignKey("acounts.user"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    apartment_number = Column(String, nullable=False, index=True)
    gender = Column(String, index=True)
    phone = Column(String, nullable=False, index=True)
    email = Column(String, index=True)

class Acount(Base):
    __tablename__ = "acounts"

    user = Column(String, primary_key=True, index=True)
    password = Column(String, index=True)

class AccountData(BaseModel):
    user: str
    password: str

class ResidentsData(BaseModel):
    username: str = None
    name: str = None
    apartment_number: str = None
    gender: str = None
    phone: str = None
    email: str = None