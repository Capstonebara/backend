import torch
# from facenet_pytorch import InceptionResnetV1  # FaceNet model
from PIL import Image
import torchvision.transforms as transforms
from .EdgeFaceKan import EdgeFaceKAN

# Sử dụng mô hình pre-trained FaceNet
# class EmbeddingModel:
#     def __init__(self):
#         self.model = InceptionResnetV1(pretrained='vggface2').eval()  

#         self.transform = transforms.Compose([
#             transforms.Resize((160, 160)),  
#             transforms.ToTensor(),
#             transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#         ])

#     def embed(self, image_path):
#         image = Image.open(image_path).convert("RGB")
#         image_tensor = self.transform(image).unsqueeze(0) 

#         with torch.no_grad():
#             embedding = self.model(image_tensor)
#         return embedding.numpy().flatten().tolist()
    

# if __name__ == "__main__":
#     model = EmbeddingModel()
#     embedding = model.embed("img/PXL_20250308_124731514.jpg")
#     print(embedding)

class EmbeddingModel:
    def __init__(self, weight_path="models/EdgeFaceKAN_mean_06_25_cos_512/model.pt"):

        self.model = EdgeFaceKAN()
        checkpoint = torch.load(weight_path, map_location=torch.device("cpu"))
        self.model.load_state_dict(checkpoint)
        self.model.eval()

        
        self.transform = transforms.Compose([
            transforms.Resize((112, 112)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def embed(self, image_path):
        
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0)

        
        with torch.no_grad():
            embedding = self.model(image_tensor)

        return embedding.numpy().flatten().tolist()