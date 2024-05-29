import subprocess
from pathlib import Path

# Define the path to the .env file
env_file_path = Path('id.env')

# Check if the .env file exists
if not env_file_path.exists():
    print("Error: .env file does not exist. Cannot retrieve container ID.")
else:
    # Read the container ID from the .env file
    with open(env_file_path, 'r') as file:
        lines = file.readlines()
        container_id = None
        for line in lines:
            if line.startswith('CONTAINER_ID='):
                container_id = line.strip().split('=')[1]
                break
    
    if container_id:
        
        # Check if the container is running
        if subprocess.check_output(
            f"docker inspect -f {{.State.Running}} {container_id}",
            shell=True
        ).decode("utf-8").strip() == "{.State.Running}":
            # Kill and remove the container
            print(f"Container {container_id} is running. Attempting to kill...")
            subprocess.call(f'docker kill {container_id}', shell=True)
            print(f"Container {container_id} has been killed.")
        else:
            print(f"Container {container_id} is not running.")

        # Clear the contents of the .env file even if the container wasn't running
        with open(env_file_path, 'w') as f:
            f.write('')  # Write an empty string to clear the file
        print(f".env file cleared.")

    else:
        print("Container ID not found in .env file.")
