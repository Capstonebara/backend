from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from database import models, crud
from database.database import SessionLocal, engine

users = APIRouter()

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