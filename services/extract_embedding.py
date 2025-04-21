import os
import zipfile, json
from models.model_embedding import EmbeddingModel

#extract zip file
def extract_zip(zip_path, zip_filename, pic_folder):
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

#embed images
def embed_images(extracted_dir):
    embedding_model = EmbeddingModel()  
    results = []
    files_ = []

    for root, dirs, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                 # Skip files named main.jpg, main.png, etc.
                if file.startswith('main.'):
                    continue
                image_path = os.path.join(root, file)
                embedding = embedding_model.embed(image_path)  
                results.append(embedding)
                files_.append(file)

    return results,files