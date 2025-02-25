from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from database import models, crud
from database.database import SessionLocal, engine

authen = APIRouter()

# Tạo tất cả các bảng trong CSDL
models.Base.metadata.create_all(bind=engine)

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@authen.get("/auth/{email}")
def read_user(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_email(db, email=email.lower())
    if db_user is None:
        return {
            "status": False
        }
    
    reg = crud.get_status(db, email=email.lower())

    return {
        "idx": db_user.id,
        "status": True,
        "reg": reg
    }


# @authen.post("/update-reg/{email}")
# def update_reg(email: str, db: Session = Depends(get_db)):
#     updated_user = crud.update_registration_status(db, email=email.lower(), status=1)
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {
#         "status": True,
#         "message": "Registration status updated successfully",
#         "user": {
#             "email": updated_user.email,
#             "reg": updated_user.reg
#         }
#     }

# @authen.post("/reset-reg/{email}")
# def update_reg(email: str, db: Session = Depends(get_db)):
#     updated_user = crud.update_registration_reset(db, email=email.lower(), status=0)
#     if not updated_user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return {
#         "status": True,
#         "message": "Reset Registration status updated successfully",
#         "user": {
#             "email": updated_user.email,
#             "reg": updated_user.reg
#         }
#     }       

# @authen.post("/update-status/{user_id}")
# def update_le_hoi(user_id: int, status: str, db: Session = Depends(get_db)):
#     if status == "le":
#         updated_user = crud.update_registration_le_status(db, user_id=user_id)
#         if not updated_user:
#             raise HTTPException(status_code=404, detail="User not found")
#         # Reset other statuses
#         updated_user = crud.update_registration_tiec_reset(db, user_id=user_id)
#         updated_user = crud.update_registration_cahai_reset(db, user_id=user_id)
#         return {
#             "status": True,
#             "message": "Lễ status updated successfully",
#             "user": {
#                 "id": updated_user.id,
#                 "email": updated_user.email,
#                 "le": updated_user.le
#             }
#         }
    
#     elif status == "tiec":
#         updated_user = crud.update_registration_tiec_status(db, user_id=user_id)
#         if not updated_user:
#             raise HTTPException(status_code=404, detail="User not found")
#         # Reset other statuses
#         updated_user = crud.update_registration_le_reset(db, user_id=user_id)
#         updated_user = crud.update_registration_cahai_reset(db, user_id=user_id)
#         return {
#             "status": True,
#             "message": "Tiệc status updated successfully",
#             "user": {
#                 "id": updated_user.id,
#                 "email": updated_user.email,
#                 "tiec": updated_user.tiec
#             }
#         }
    
#     elif status == "cahai":
#         updated_user = crud.update_registration_cahai_status(db, user_id=user_id)
#         if not updated_user:
#             raise HTTPException(status_code=404, detail="User not found")
#         # Reset other statuses
#         updated_user = crud.update_registration_le_reset(db, user_id=user_id)
#         updated_user = crud.update_registration_tiec_reset(db, user_id=user_id)
#         return {
#             "status": True,
#             "message": "Cả hai status updated successfully",
#             "user": {
#                 "id": updated_user.id,
#                 "email": updated_user.email,
#                 "cahai": updated_user.cahai
#             }
#         }
    
    # else:
    #     raise HTTPException(status_code=400, detail="Invalid status value")