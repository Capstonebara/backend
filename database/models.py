from sqlalchemy import Column, Integer, String, Boolean
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    reg = Column(Boolean, index=True)
    le = Column(Boolean, index=True)
    tiec = Column(Boolean, index=True)
    cahai = Column(Boolean, index=True)