from ultralytics import YOLO
import os
from pathlib import Path

# Load a model
model = YOLO('model/yolov8n.pt')  # load an official model

# Ensure the model directory exists
os.makedirs('model', exist_ok=True)

# Export the model to ONNX format and save it in the 'model' folder
onnx_file = model.export(format='onnx', opset=15, dynamic=True, save_dir='model')



# Define paths
triton_repo_path = Path('tmp') / 'triton_repo'
triton_model_path = triton_repo_path / 'yolo'

# Create directories
(triton_model_path / '1').mkdir(parents=True, exist_ok=True)

# Move ONNX model to Triton Model path
Path(onnx_file).rename(triton_model_path / '1' / 'model.onnx')

# Create config file
(triton_model_path / 'config.pbtxt').touch()