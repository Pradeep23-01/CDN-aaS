import json
import os
import pandas as pd
import subprocess
import sys

# Load and parse the JSON data
with open('vm_info.json', 'r') as file:
    vm_info = json.load(file)

# Ask for the customer ID to make it dynamic
customer_id = sys.argv[1] #input("Enter the customer ID (e.g., 'customer_7'): ")
'''
# Get the IPs from Infra?
df = pd.read_csv("updated_dataframe.csv")

def extract_container_names(df, customer_id):
    # Locate the row with the specified Customer ID
    row = df[df['Customer_ID'] == customer_id]

    # Check if the row is not empty
    if not row.empty:
        container_details = row['vm_details'].iloc[0]  # Assume 'vm_details' now holds container info
        container_info = json.loads(container_details)  # Parse the JSON data

        # Extract container names dynamically constructed with the customer_id
        container_host = f"{customer_id}_host"
        container_loc1 = f"{customer_id}_loc1"
        container_loc2 = f"{customer_id}_loc2"
        container_controller = f"{customer_id}_controller"

        return container_host, container_loc1, container_loc2, container_controller
    else:
        return None
'''

import subprocess
import re

def extract_container_names(customer_id):
    # Execute Docker command to get all containers
    try:
        result = subprocess.run(['sudo', 'docker', 'ps', '--all', '--format', '{{.Names}}'],
                                capture_output=True, text=True, check=True)
        # Filter container names starting with the customer_id
        pattern = re.compile(f"^{customer_id}_\\w+")
        container_names = [name for name in result.stdout.splitlines() if pattern.match(name)]

        # Create a dictionary with default None for expected roles
        container_roles = {'host': None, 'loc1': None, 'loc2': None, 'controller': None, 'client': None}
        for name in container_names:
            role = name.split('_')[-1]  # Assumes name format "customerID_role"
            if role in container_roles:
                container_roles[role] = name

        # Return values directly unpackable to variables
        return (container_roles['host'], container_roles['loc1'],
                container_roles['loc2'], container_roles['controller'], container_roles['client'])
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute docker command: {e}")
        return (None, None, None, None)

# Example usage
#customer_id = "customer_18"
container_host, container_loc1, container_loc2, container_controller, container_client = extract_container_names(customer_id)
print(f"Host: {container_host}, Loc1: {container_loc1}, Loc2: {container_loc2}, Controller: {container_controller}")

# Use the function to get container names
#container_host, container_loc1, container_loc2, container_controller = extract_container_names(df, customer_id)

# Directory to copy and user is not needed as we're working with Docker
if not (container_host and container_loc1 and container_loc2 and container_controller):
    print("Error: Could not find all required container names.")
else:
    # Directory where files are located
    directory_to_copy = f'/home/vmadm/saas_d/storage/{customer_id}'  # directory for storage
    containers = [container_host, container_loc1, container_loc2]
    for container in containers:
        subprocess.run(f"sudo docker cp {directory_to_copy} {container}:/home/".split(), check=True)
        print(f"Copied files to container {container}")

    # Additional step to copy specific .py files to the controller container
    controller_to_copy = "/home/vmadm/saas_d/storage/controller/"
    files_to_copy = ["get_server1.py", "details.py", "ssh_start.py"]
    for file_name in files_to_copy:
        local_path = os.path.join(controller_to_copy, file_name)
        if not os.path.exists(local_path):
            print(f"File not found: {local_path}")
            continue

        subprocess.run(f"sudo docker cp {local_path} {container_controller}:/home/".split(), check=True)
        print(f"Copied {file_name} to container {container_controller}")
    subprocess.run(f"sudo docker cp {controller_to_copy}/details.py {container_client}:/home/".split(), check=True)
    subprocess.run(f"sudo docker cp {controller_to_copy}/get_url.py {container_client}:/home/".split(), check=True)
    subprocess.run(f"sudo docker cp {controller_to_copy}/log.py {container_client}:/home/".split(), check=True)
     #print(f"Copied {file_name} to container {container_controller}")

