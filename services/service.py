import os
import hashlib
import json
import pytz
import numpy as np
import struct


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
            print(f"Embedding for {file} saved to {output_json_path}")
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
    
def process_embedding_bin(base_folder: str, embed_folder: str, specific_folder: str):
    """Process embeddings for a specific folder and save as .bin (float32)"""
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
            output_bin_path = os.path.join(embedded_data_subfolder, f"{file}.bin")
            with open(output_bin_path, "wb") as bin_file:
                # Convert embedding to numpy array float32
                embedding_array = np.array(embedding, dtype=np.float32)
                bin_file.write(embedding_array.tobytes())

        print("Embed successfully (binary)", specific_folder)

        utc_now = datetime.now(pytz.utc)
        vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        vietnam_time = utc_now.astimezone(vietnam_tz)

        result = {
            "info": f"Processed folder '{specific_folder}' to .bin format.",
            "processed_folder": specific_folder,
            "embeddings_saved_to": embed_folder,
            "timestamp": vietnam_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(json.dumps(result, indent=5, ensure_ascii=False))
        return result

    except Exception as e:
        print(f"Error processing folder {specific_folder}: {str(e)}")
        return None
    
def process_embedding_bin_allinone(base_folder: str, embed_base_folder: str, specific_folder: str):
    """Process embeddings for a specific folder and save into id_folder/id.bin"""

    if not os.path.exists(base_folder):
        print(f"Base folder '{base_folder}' does not exist.")
        return

    subfolder_path = os.path.join(base_folder, specific_folder)

    try:
        if not os.path.isdir(subfolder_path):
            raise Exception(f"Folder {specific_folder} does not exist.")

        # Chuẩn bị folder lưu embeddings
        output_folder = os.path.join(embed_base_folder, specific_folder)
        os.makedirs(output_folder, exist_ok=True)

        output_bin_path = os.path.join(output_folder, f"{specific_folder}.bin")

        embeddings, files = embed_images(subfolder_path)

        embeddings_array = np.array(embeddings, dtype=np.float32)

        with open(output_bin_path, "wb") as bin_file:
            bin_file.write(embeddings_array.tobytes())

        print(f"Embed successfully (all-in-one) {specific_folder}")
        print(f"Saved {len(files)} embeddings to {output_bin_path}")

        utc_now = datetime.now(pytz.utc)
        vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        vietnam_time = utc_now.astimezone(vietnam_tz)

        result = {
            "info": f"Processed folder '{specific_folder}' and saved {len(files)} embeddings into one bin.",
            "processed_folder": specific_folder,
            "embeddings_saved_to": output_bin_path,
            "timestamp": vietnam_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        print(result)
        return result

    except Exception as e:
        print(f"Error processing folder {specific_folder}: {str(e)}")
        return None
    
def save_embedding_with_header_auto_embed(
    base_folder: str,
    embed_base_folder: str,
    specific_folder: str,
    person_id: int,
    person_name: str
):
    """
    Embed all images inside specific_folder, then save to embed_base_folder/person_id/person_id.bin
    Format: [person_id][name_length][name_bytes][num_embeddings][embedding_size][embedding_data]
    """

    # Check base_folder exists
    if not os.path.exists(base_folder):
        print(f"Base folder '{base_folder}' does not exist.")
        return

    # Path to the subfolder
    subfolder_path = os.path.join(base_folder, specific_folder)

    try:
        if not os.path.isdir(subfolder_path):
            raise Exception(f"Folder {specific_folder} does not exist.")

        # Embed images
        embeddings, files = embed_images(subfolder_path)

        if len(embeddings) == 0:
            raise Exception(f"No valid images found in {specific_folder}")
            
        # Print first and last number of each embedding
        # for i, embedding in enumerate(embeddings):
        #     print(f"Embedding {i} for {files[i]}: First: {embedding[0]}, Last: {embedding[-1]}")

        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Prepare output folder
        person_folder = os.path.join(embed_base_folder, str(person_id))
        os.makedirs(person_folder, exist_ok=True)

        # Output file
        output_bin_path = os.path.join(person_folder, f"{person_id}.bin")

        with open(output_bin_path, 'wb') as f:
            # Person ID
            f.write(struct.pack('i', person_id))

            # Name Length and Name
            name_bytes = person_name.encode('utf-8')
            f.write(struct.pack('i', len(name_bytes)))
            f.write(name_bytes)

            # Number of Embeddings and Embedding Size
            if len(embeddings_array.shape) == 1:
                embeddings_array = embeddings_array.reshape(1, -1)

            num_embeddings, embedding_size = embeddings_array.shape

            f.write(struct.pack('i', num_embeddings))
            f.write(struct.pack('i', embedding_size))

            # Embedding Data
            f.write(embeddings_array.astype(np.float32).tobytes())

        print(f"Embed and save successfully: {output_bin_path}")

        # Return some info
        utc_now = datetime.now(pytz.utc)
        vietnam_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        vietnam_time = utc_now.astimezone(vietnam_tz)

        result = {
            "info": f"Processed and saved {num_embeddings} embeddings for '{person_name}' (ID {person_id})",
            "processed_folder": specific_folder,
            "output_bin": output_bin_path,
            "timestamp": vietnam_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

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