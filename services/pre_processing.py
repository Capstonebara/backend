import torch
# import torchvision
from torchvision import models

class ssdlite320_mobilenet_v3(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.model = models.detection.ssdlite320_mobilenet_v3_large(num_classes=2)

    def forward(self, images, targets=None):
        if self.training:
            outputs = self.model(images, targets)

            return outputs['bbox_regression'], outputs['classification']
        else:
            outputs = self.model(images) 
            
            boxes = [out["boxes"] for out in outputs]
            scores = [out["scores"] for out in outputs]
            labels = [out["labels"] for out in outputs]

            return boxes, scores, labels
        

import cv2
import torch
from torchvision import transforms

class FaceDetectionModel:
    def __init__(self, model_path: str, device: str = None, detection_threshold: float = 0.99):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.detection_threshold = detection_threshold
        self.model = ssdlite320_mobilenet_v3()
        checkpoint = torch.load(model_path, map_location=self.device)
        checkpoint = {k.replace("module.", ""): v for k, v in checkpoint.items()}
        self.model.load_state_dict(checkpoint)
        self.model.eval().to(self.device)
        
        # Preprocessing pipeline
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
    def detection_preprocess(self, image):
        # Resize and normalize the image
        image = cv2.resize(image, (320, 320))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.transform(image).unsqueeze(0).to(self.device)
        return image
    
    def detect_faces(self, image):
        # Preprocess the image
        orig_height, orig_width = image.shape[:2]
        image = self.detection_preprocess(image)
        
        # Perform detection
        with torch.no_grad():
            detections = self.model(image)
            
        # Post-process detections
        boxes = detections[0][0]
        scores = detections[1][0]
        
        # Filter out low-confidence detections
        mask = scores >= self.detection_threshold
        filtered_boxes = boxes[mask]
        
        # Scale boxes back to original image size
        scale_x = orig_width / 320
        scale_y = orig_height / 320
        
        if len(filtered_boxes) > 0:
            scaled_boxes = torch.stack([
                filtered_boxes[:, 0] * scale_x,
                filtered_boxes[:, 1] * scale_y,
                filtered_boxes[:, 2] * scale_x,
                filtered_boxes[:, 3] * scale_y,
            ], dim=1).tolist()
            return scaled_boxes
        return []
    

import cv2
import os
from pathlib import Path
from PIL import Image

class Preprocessor:
    def __init__(self, face_detector, min_brightness=50, max_brightness=200, min_sharpness=10.0, min_box_ratio=0.3):
        self.face_detector = face_detector
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness
        self.min_sharpness = min_sharpness
        self.min_box_ratio = min_box_ratio

    def compute_sharpness(self, gray_roi):
        laplacian = cv2.Laplacian(gray_roi, cv2.CV_64F)
        _, stddev = cv2.meanStdDev(laplacian)
        return float(stddev[0][0] ** 2)

    def compute_brightness(self, gray_roi):
        return float(cv2.mean(gray_roi)[0])

    def is_quality_acceptable(self, gray_roi):
        brightness = self.compute_brightness(gray_roi)
        sharpness = self.compute_sharpness(gray_roi)
        if brightness < self.min_brightness or brightness > self.max_brightness:
            print(f"⚠️ Brightness {brightness:.2f} out of range.")
            return False
        if sharpness < self.min_sharpness:
            print(f"⚠️ Sharpness {sharpness:.2f} below threshold.")
            return False
        return True

    def crop_and_save_faces(self, img_path: str, output_path: Path):
        image = cv2.imread(img_path)
        if image is None:
            print(f"❌ Could not read image: {img_path}")
            return

        img_h, img_w = image.shape[:2]
        img_area = img_w * img_h

        boxes = self.face_detector.detect_faces(image)

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            box_area = (x2 - x1) * (y2 - y1)

            if box_area < self.min_box_ratio * img_area:
                print(f"⚠️ Box {i} skipped: too small ({box_area}px).")
                continue

            gray = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
            if not self.is_quality_acceptable(gray):
                print(f"⚠️ Box {i} skipped: poor quality.")
                continue

            face_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_img = Image.fromarray(face_rgb).crop((x1, y1, x2, y2))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            face_img.save(output_path)
            print(f"✅ Face {i} saved to {output_path}")
            
from pathlib import Path

def preprocess_images(input_dir: str, output_dir: str):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    face_detector = FaceDetectionModel(model_path="services/mobilenet.pth", detection_threshold = 0.95, device="cpu") # replace with your actual detector
    preprocessor = Preprocessor(face_detector, min_brightness=50, max_brightness=200, min_sharpness=10.0)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                img_path = Path(root) / file
                rel_path = img_path.relative_to(input_dir)
                output_path = output_dir / rel_path.with_suffix('.jpg')

                print(f"🔍 Processing: {img_path}")
                preprocessor.crop_and_save_faces(str(img_path), output_path)