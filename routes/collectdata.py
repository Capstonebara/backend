from fastapi import APIRouter, BackgroundTasks, UploadFile, File
import os
import json
import zipfile
from datetime import datetime
import pytz
from services.extract_embedding import embed_images

router = APIRouter()

def process_zip(zip_folder: str, pic_folder: str):
    """Process all zip files in the zip_folder and extract them to pic_folder"""
    if not os.path.exists(zip_folder):
        print(f"Zip folder '{zip_folder}' does not exist.")
        return
    
    if not os.path.exists(pic_folder):
        os.makedirs(pic_folder)
    
    processed_files = []
    errors = []
    
    # Process each zip file in the folder
    for zip_file in os.listdir(zip_folder):
        if zip_file.endswith('.zip'):
            zip_path = os.path.join(zip_folder, zip_file)
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Create a subfolder with the same name as the zip file (without .zip)
                    subfolder_name = os.path.splitext(zip_file)[0]
                    extract_path = os.path.join(pic_folder, subfolder_name)
                    
                    # Create subfolder if it doesn't exist
                    if not os.path.exists(extract_path):
                        os.makedirs(extract_path)
                    
                    # Extract all files
                    zip_ref.extractall(extract_path)
                    processed_files.append(zip_file)
                    print(f"Successfully extracted {zip_file} to {extract_path}")
                    
            except Exception as e:
                errors.append({"file": zip_file, "error": str(e)})
                print(f"Error processing {zip_file}: {str(e)}")
    
    return {
        "processed_files": processed_files,
        "errors": errors
    }


def process_embedding(base_folder: str, embed_folder: str):
    if not os.path.exists(base_folder):
        print(f"Base folder '{base_folder}' does not exist.")
        return

    if not os.path.exists(embed_folder):
        os.makedirs(embed_folder)

    processed_folders = []
    skipped_folders = []
    errors = []

    existing_embeds = set(os.listdir(embed_folder))

    for subfolder in os.listdir(base_folder):
        subfolder_path = os.path.join(base_folder, subfolder)

        if os.path.isdir(subfolder_path) and subfolder not in existing_embeds:
            try:
                if not os.path.isdir(subfolder_path):
                    continue

                embedded_data_subfolder = os.path.join(embed_folder, subfolder)
                if not os.path.exists(embedded_data_subfolder):
                    os.makedirs(embedded_data_subfolder)

                embeddings, files = embed_images(subfolder_path)

                for embedding, file in zip(embeddings, files):
                    output_json_path = os.path.join(embedded_data_subfolder, f"{file}.json")
                    with open(output_json_path, "w") as json_file:
                        json.dump(embedding, json_file)

                print("embed successfully", subfolder)
                processed_folders.append(subfolder)
            except Exception as e:
                errors.append({"folder": subfolder, "error": str(e)})
        else:
            print("skipped folder", subfolder)
            skipped_folders.append(subfolder)

    utc_now = datetime.now(pytz.utc)
    vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    vietnam_time = utc_now.astimezone(vietnam_tz)

    result = {
        "info": f"Processed new subfolders in '{base_folder}'.",
        "processed_folders": processed_folders,
        "skipped_folders": skipped_folders,
        "errors": errors,
        "embeddings_saved_to": embed_folder,
        "timestamp": vietnam_time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    print(json.dumps(result, indent=5, ensure_ascii=False))

@router.post("/embed")
async def embed(file: UploadFile = File(...)):
    # Create necessary folders if they don't exist
    zip_folder = os.path.join("data", "zips")
    pic_folder = os.path.join("data", "pics")
    embed_folder = os.path.join("data", "embeds")
    
    os.makedirs(zip_folder, exist_ok=True)
    
    # Save uploaded zip file
    zip_path = os.path.join(zip_folder, file.filename)
    try:
        with open(zip_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        # print(f"Error saving zip file: {str(e)}")
        return {
            "ok": False,
            "message": "error save zip"
        }
    
    # Process zip file
    try:
        zip_result = process_zip(zip_folder, pic_folder)
        if not zip_result or zip_result.get("errors"):
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
    
    # Generate embeddings
    try:
        process_embedding(pic_folder, embed_folder)
    except Exception as e:
        print(f"Error in process_embedding: {str(e)}")
        return {
            "ok": False,
            "message": "error process_embedding"
        }
    
    return {
        "ok": True,
        "message": "done"
    }
