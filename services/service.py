import os
import hashlib
import json
import pytz

from datetime import datetime

from services.extract_embedding import embed_images, extract_zip

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