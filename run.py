import subprocess
import time
from pathlib import Path
from tritonclient.http import InferenceServerClient
import contextlib

# Define paths
triton_repo_path = Path('tmp/triton_repo').absolute() # Get absolute path
env_file_path = Path('id.env')  # Define path to the .env file

# Define image
tag = "nvcr.io/nvidia/tritonserver:22.04-py3"  # 6.4 GB

def pull_docker_image(image_tag):
    # Check if image exists
    try:
        subprocess.run(f'docker image inspect {image_tag}', shell=True, check=True)
        print(f"Image {image_tag} already exists. No need to pull.")
    except subprocess.CalledProcessError:
        print(f"Image {image_tag} not found. Pulling from registry...")
        subprocess.run(f'docker pull {image_tag}', shell=True)

# Pull the image
pull_docker_image(tag)

# Function to create a Docker network if it does not exist
def create_docker_network(network_name):
    try:
        subprocess.run(f'docker network inspect {network_name}', shell=True, check=True)
        print(f"Network {network_name} already exists.")
    except subprocess.CalledProcessError:
        print(f"Network {network_name} not found. Creating it...")
        subprocess.run(f'docker network create {network_name}', shell=True, check=True)
        print(f"Network {network_name} created.")

# Create Docker network if it does not exist
network_name = "triton"
create_docker_network(network_name)


# Check if the .env file exists, if not, create it
if not env_file_path.exists():
    env_file_path.touch()
    print(f"Created new .env file at {env_file_path}")


# Run the Triton server and capture the container ID
container_id = subprocess.check_output(
    f"docker run -d --rm --network {network_name} -v {triton_repo_path.as_posix()}:/models -p 8000:8000 {tag} tritonserver --model-repository=/models",
    shell=True
).decode("utf-8").strip()

print("Triton Server container ID:", container_id)

# Check if the container is running
if subprocess.check_output(
    f"docker inspect -f {{.State.Running}} {container_id}",
    shell=True
).decode("utf-8").strip() == "{.State.Running}":
    # Write the container ID to the .env file
    with open(env_file_path, 'w') as f:
        f.write(f'CONTAINER_ID={container_id}\n')
    print(f"Container ID written to {env_file_path}")
else:
    print("Container is not running. Check the container setup.")

# Create a client to interact with the Triton Inference Server
triton_client = InferenceServerClient(url="localhost:8000", verbose=False, ssl=False)

# Wait for the Triton server to be ready
print("Waiting for Triton Server to be ready...")
for _ in range(10):
    try:
        if triton_client.is_server_ready():
            print("Triton Server is ready.")
            break
    except Exception as e:
        print("Waiting for server to start...", e)
    time.sleep(5)
else:
    print("Failed to connect to Triton Server.")
    exit(1)

# Check if the model 'yolo' is loaded and ready
model_name = 'yolo'
print(f"Checking if model {model_name} is ready...")
for _ in range(10):
    try:
        if triton_client.is_model_ready(model_name):
            print(f"Model {model_name} is ready for inference.")
            break
    except Exception as e:
        print(f"Waiting for model {model_name} to be ready...", e)
    time.sleep(1)
else:
    print(f"Model {model_name} is not ready or not found.")
    exit(1)
