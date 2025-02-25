from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

# Kết nối đồng bộ (nếu không dùng async)
engine = create_engine(DATABASE_URL)

# Sử dụng MetaData để quản lý các bảng
metadata = MetaData()

# Base class để tạo các mô hình (models)
Base = declarative_base()

# Session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)