import argparse
import os
import requests
from pathlib import Path
from ultralytics import YOLO
from PIL import Image, ImageDraw

# Function to download the image if it does not exist
def download_image(url, dest_path):
    if not dest_path.exists():
        print(f"Downloading image from {url} to {dest_path}")
        response = requests.get(url)
        with open(dest_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Image already exists at {dest_path}")

# Function to draw bounding boxes and labels on the image
def draw_boxes(image_path, results, output_path):
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    for bbox in results[0].boxes:
        xy = [bbox.xyxy[0][0].item(), bbox.xyxy[0][1].item(), bbox.xyxy[0][2].item(), bbox.xyxy[0][3].item()]
        label = results[0].names[int(bbox.cls[0])]
        draw.rectangle(xy, outline="red", width=2)
        draw.text((xy[0], xy[1]), label, fill="red")
    image.save(output_path)
    print(f"Output image saved to {output_path}")

# Main function to handle inference and drawing
def main(image_url, image_path, output_path):
    # Download the image if it does not exist
    download_image(image_url, image_path)

    # Load the Triton Server model
    model = YOLO(f'http://triton:8000/yolo', task='detect')  

    # Run inference on the server
    results = model(str(image_path))

    # Draw bounding boxes and labels on the image
    draw_boxes(image_path, results, output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inference Script for Triton Server")
    parser.add_argument("--image-url", type=str, required=True, help="URL of the image to download")
    parser.add_argument("--image-path", type=Path, required=True, help="Path to save the downloaded image")
    parser.add_argument("--output-path", type=Path, required=True, help="Path to save the output image with bounding boxes")
    args = parser.parse_args()

    main(args.image_url, args.image_path, args.output_path)
