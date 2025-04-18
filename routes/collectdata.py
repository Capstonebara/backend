import os
import hashlib
import json
import shutil
import tempfile
import pytz
import zipfile
from fastapi.responses import FileResponse

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from datetime import datetime
from database import crud
from sqlalchemy.orm import Session
from database.database import SessionLocal
from services.extract_embedding import embed_images, extract_zip

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

def process_zip(zip_folder: str, pic_folder: str, zip_filename: str):
    """Process specific zip file and return the extracted folder path"""
    if not os.path.exists(zip_folder):
        print(f"Zip folder '{zip_folder}' does not exist.")
        return None
    
    if not os.path.exists(pic_folder):
        os.makedirs(pic_folder)
    
    zip_path = os.path.join(zip_folder, zip_filename)
    try:
        subfolder_name = extract_zip(zip_path, zip_filename, pic_folder)
        return subfolder_name    
    except Exception as e:
        print(f"Error processing {zip_filename}: {str(e)}")
        return None


def process_embedding(base_folder: str, embed_folder: str, specific_folder: str):
    """Process embeddings for a specific folder only"""
    if not os.path.exists(base_folder):
        print(f"Base folder '{base_folder}' does not exist.")
        return

    if not os.path.exists(embed_folder):
        os.makedirs(embed_folder)

    subfolder_path = os.path.join(base_folder, specific_folder)
    
    try:
        if not os.path.isdir(subfolder_path):
            raise Exception(f"Folder {specific_folder} does not exist")

        embedded_data_subfolder = os.path.join(embed_folder, specific_folder)
        if not os.path.exists(embedded_data_subfolder):
            os.makedirs(embedded_data_subfolder)

        embeddings, files = embed_images(subfolder_path)

        for embedding, file in zip(embeddings, files):
            output_json_path = os.path.join(embedded_data_subfolder, f"{file}.json")
            with open(output_json_path, "w") as json_file:
                json.dump(embedding, json_file)

        print("embed successfully", specific_folder)

        utc_now = datetime.now(pytz.utc)
        vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        vietnam_time = utc_now.astimezone(vietnam_tz)

        result = {
            "info": f"Processed folder '{specific_folder}'.",
            "processed_folder": specific_folder,
            "embeddings_saved_to": embed_folder,
            "timestamp": vietnam_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(json.dumps(result, indent=5, ensure_ascii=False))
        return result

    except Exception as e:
        print(f"Error processing folder {specific_folder}: {str(e)}")
        return None

def calc_md5(folder_path: str):
    md5 = hashlib.md5()
    for root, _, files in os.walk(folder_path):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    md5.update(chunk)
    return md5.hexdigest()

@router.post("/embed")
async def embed(file: UploadFile = File(...), folder_id: int = None):
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
        embedding_result = process_embedding(pic_folder, embed_folder, extracted_folder)
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

@router.get("/sync-metadata")
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


@router.get("/download-embeds/{id}")
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

