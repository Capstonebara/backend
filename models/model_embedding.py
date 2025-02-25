import torch
from facenet_pytorch import InceptionResnetV1  # FaceNet model
from PIL import Image
import torchvision.transforms as transforms

# Sử dụng mô hình pre-trained FaceNet
class EmbeddingModel:
    def __init__(self):
        self.model = InceptionResnetV1(pretrained='vggface2').eval()  

        self.transform = transforms.Compose([
            transforms.Resize((160, 160)),  
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def embed(self, image_path):
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0) 

        with torch.no_grad():
            embedding = self.model(image_tensor)
        return embedding.numpy().flatten().tolist()
