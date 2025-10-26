"""
Download YOLO model with proper PyTorch settings
"""
import torch
from ultralytics import YOLO

# Allow ultralytics models to be loaded
torch.serialization.add_safe_globals([
    'ultralytics.nn.tasks.DetectionModel',
    'ultralytics.nn.modules.Conv',
    'ultralytics.nn.modules.C2f',
    'ultralytics.nn.modules.SPPF',
    'ultralytics.nn.modules.Detect'
])

print("Downloading YOLOv8s model...")
model = YOLO('yolov8s.pt')
print("✅ Model downloaded and ready!")
print(f"Model file: yolov8s.pt")
print(f"Classes: {model.names}")
