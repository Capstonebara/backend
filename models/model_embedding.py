import torch
# from facenet_pytorch import InceptionResnetV1  # FaceNet model
import torchvision.transforms as transforms
from .EdgeFaceKan import EdgeFaceKAN
import cv2

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
    def __init__(self, weight_path="models/kanface_06_25_128_custom.pth"):

        self.model = EdgeFaceKAN(num_features = 128, grid_size = 25, rank_ratio = 0.6, neuron_fun="mean")
        checkpoint = torch.load(weight_path, map_location=torch.device("cpu"))
        self.model.load_state_dict(checkpoint)
        self.model.eval()

        
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])

    def embed(self, image_path):
        
        image = cv2.imread(image_path)
        image = cv2.resize(image, (112, 112))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image_tensor = self.transform(image).unsqueeze(0)

        
        with torch.no_grad():
            embedding = self.model(image_tensor)

        return embedding.cpu().numpy().flatten().tolist()