import torch
import torchvision.transforms as transforms
from PIL import Image
from EdgeFaceKan import EdgeFaceKAN

class EmbeddingModel:
    def __init__(self, weight_path="/home/thainq/Desktop/webapp/webapp_backend/models/EdgeFaceKAN_mean_06_25_cos_512/model.pt"):
        # Load mô hình đã huấn luyện
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
        image_tensor = self.transform(image).unsqueeze(0)  # Thêm batch dimension

        
        with torch.no_grad():
            embedding = self.model(image_tensor)

        return embedding.numpy().flatten().tolist()  # Chuyển thành list để dễ sử dụng

if __name__ == "__main__":
    model = EmbeddingModel()
    embedding = model.embed("img/PXL_20250308_124731514.jpg")
    print(embedding)