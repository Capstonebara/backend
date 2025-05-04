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
    mem_count = len(db.query(models.Resident).filter(models.Resident.username == account.username).all())
    account.member = mem_count
    db.commit()

def delete_resident_image(resident_id: int):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    if not os.path.exists(base_path):
        return

    # Duyệt qua các folder như: pics, processed_pics, embeds, zips,...
    for subfolder in os.listdir(base_path):
        subfolder_path = os.path.join(base_path, subfolder)

        if not os.path.isdir(subfolder_path):
            continue

        target_path = os.path.join(subfolder_path, str(resident_id))

        try:
            # Xóa nếu là folder (processed_pics, pics, embeds)
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
                print(f"✅ Deleted folder: {target_path}")
            # Xóa nếu là file (ví dụ: zips/123.zip, embeds/123.bin)
            else:
                for path in glob.glob(f"{target_path}.*"):
                    os.remove(path)
                    print(f"✅ Deleted file: {path}")
        except Exception as e:
            print(f"❌ Error deleting {target_path}: {str(e)}")