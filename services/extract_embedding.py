import os
import zipfile, json
from models.model_embedding import EmbeddingModel

# Khởi tạo hàm giải nén file zip
def extract_zip(zip_path, extract_to):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# Khởi tạo hàm embedding ảnh
def embed_images(extracted_dir):
    embedding_model = EmbeddingModel()  
    results = []
    files_ = []

    for root, dirs, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):  
                image_path = os.path.join(root, file)
                embedding = embedding_model.embed(image_path)  
                results.append(embedding)
                files_.append(file)

    return results,files