import os
import shutil
import tempfile
import zipfile
from fastapi.responses import FileResponse

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from database import crud
from sqlalchemy.orm import Session
from database.database import SessionLocal
from services.service import process_zip, process_embedding, calc_md5, process_embedding_bin, process_embedding_bin_allinone, save_embedding_with_header_auto_embed

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

service = APIRouter()

@service.post("/embed")
async def embed(file: UploadFile = File(...), folder_id: int = None, db: Session = Depends(get_db)):
    # Create necessary folders if they don't exist
    zip_folder = os.path.join("data", "zips")
    pic_folder = os.path.join("data", "pics")
    embed_folder = os.path.join("data", "embeds")
    
    os.makedirs(zip_folder, exist_ok=True)
    
    # Use folder_name if provided, otherwise use filename
    zip_filename = f"{folder_id}.zip"
    # Save uploaded zip file
    zip_path = os.path.join(zip_folder, zip_filename)
    try:
        with open(zip_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        return {
            "ok": False,
            "message": "error save zip"
        }
    
    # Process zip file
    try:
        extracted_folder = process_zip(zip_folder, pic_folder, zip_filename)
        if not extracted_folder:
            return {
                "ok": False,
                "message": "error process_zip"
            }
    except Exception as e:
        print(f"Error in process_zip: {str(e)}")
        return {
            "ok": False,
            "message": "error process_zip"
        }
    
    # Generate embeddings only for the extracted folder
    try:

        # get name by id
        resident = crud.get_resident_by_id(folder_id, db)
        
        # embedding_result = process_embedding(pic_folder, embed_folder, extracted_folder)
        embedding_result = save_embedding_with_header_auto_embed(pic_folder, embed_folder, extracted_folder, int(folder_id), resident.name)

        if not embedding_result:
            return {
                "ok": False,
                "message": "error process_embedding"
            }
    except Exception as e:
        print(f"Error in process_embedding: {str(e)}")
        return {
            "ok": False,
            "message": "error process_embedding"
        }
    
    return {
        "ok": True,
        "message": "done",
        "processed_folder": extracted_folder
    }

@service.get("/sync-metadata")
def get_sync_metadata(db: Session = Depends(get_db)):
    base_path = "data/embeds"
    folders = os.listdir(base_path)
    result = []

    for folder in folders:
        if folder.isdigit():
            folder_path = os.path.join(base_path, folder)
            if os.path.isdir(folder_path):
                resident = crud.get_resident_by_id(int(folder), db)
                if resident:
                    md5 = calc_md5(folder_path)
                    result.append({
                        "id": folder,
                        "name": resident.name,
                        "md5": md5,
                    })

    return result


@service.get("/download-embeds/{id}")
def download_single_embed(id: int, db: Session = Depends(get_db)):
    base_path = f"data/embeds/{id}"
    if not os.path.exists(base_path):
        raise HTTPException(status_code=404, detail="Embed folder not found")

    resident = crud.get_resident_by_id(id, db)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    folder_name = f"{id}_[{resident.name}]"

    temp_dir = tempfile.mkdtemp()
    temp_folder_path = os.path.join(temp_dir, folder_name)
    shutil.copytree(base_path, temp_folder_path)

    zip_path = os.path.join(temp_dir, f"{folder_name}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_folder_path):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, temp_folder_path)
                zipf.write(abs_path, arcname=os.path.join(folder_name, rel_path))

    return FileResponse(path=zip_path, filename=f"{folder_name}.zip", media_type="application/zip")

