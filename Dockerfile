# Use the official Python image based on Debian Slim
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY request_docker.py /app/
COPY testing_image.jpg /app/

# Copy requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Create a volume to store results
VOLUME /results

# Run request_docker.py when the container launches
CMD ["python", "request_docker.py", "--image-url", "https://drive.google.com/uc?export=download&id=1VekyUJdAR1X1uyQBG9D7L9QdI16_29cq", "--image-path", "/app/testing_image.jpg", "--output-path", "/results/output.jpg"]
