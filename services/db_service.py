from sqlalchemy.orm import Session
from database import models
import os
import shutil
import glob

def get_id(db: Session, table: str):
    if table == "residents":
        existing_ids = [id[0] for id in db.query(models.Resident.id).order_by(models.Resident.id).all()]
    elif table == "accounts":
        existing_ids = [id[0] for id in db.query(models.Account.id).order_by(models.Account.id).all()]
    elif table == "logs":
        existing_ids = [id[0] for id in db.query(models.Logs.id).order_by(models.Logs.id).all()]
    next_id = None
    if existing_ids:
        for expected_id in range(1, existing_ids[-1] + 1):
            if expected_id not in existing_ids:
                next_id = expected_id
                break
    return next_id

def update_account_member(db: Session, account: models.Account):
    mem_count = len(db.query(models.Resident).filter(models.Resident.user_name == account.user).all())
    account.member = mem_count
    db.commit()

def delete_resident_image(resident_id: int):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if os.path.exists(base_path):
        for subfolder in os.listdir(base_path):
            subfolder_path = os.path.join(base_path, subfolder)
            if os.path.isdir(subfolder_path):
                user_path_patterns = [
                    os.path.join(subfolder_path, str(resident_id)),
                    os.path.join(subfolder_path, f"{resident_id}.*")
                ]
                for pattern in user_path_patterns:
                    matching_paths = glob.glob(pattern)
                    for path in matching_paths:
                        try:
                            if os.path.isfile(path):
                                os.remove(path)
                            else:
                                shutil.rmtree(path)
                        except Exception as e:
                            print(f"Error deleting {path}: {str(e)}")