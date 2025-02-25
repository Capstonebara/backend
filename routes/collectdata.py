from fastapi import APIRouter, BackgroundTasks, UploadFile, File
import os
import json
import zipfile
from datetime import datetime
import pytz
from services.extract_embedding import embed_images

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
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Create a subfolder with the same name as the zip file (without .zip)
            subfolder_name = os.path.splitext(zip_filename)[0]
            extract_path = os.path.join(pic_folder, subfolder_name)
            
            # Create subfolder if it doesn't exist
            if not os.path.exists(extract_path):
                os.makedirs(extract_path)
            
            # Extract all files
            zip_ref.extractall(extract_path)
            print(f"Successfully extracted {zip_filename} to {extract_path}")
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

@router.post("/embed")
async def embed(file: UploadFile = File(...), folder_name: str = None):
    # Create necessary folders if they don't exist
    zip_folder = os.path.join("data", "zips")
    pic_folder = os.path.join("data", "pics")
    embed_folder = os.path.join("data", "embeds")
    
    os.makedirs(zip_folder, exist_ok=True)
    
    # Use folder_name if provided, otherwise use filename
    zip_filename = f"{folder_name}.zip"
    
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
