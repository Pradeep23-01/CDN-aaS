import os
import pandas as pd
import subprocess
import sys

import ipaddress


# Ask prabhu and get the allocated VPC details and save it or use it directly
# Load the mapping.csv into a DataFrame
df = pd.read_csv('updated_dataframe.csv')

# Prompt the user for the customer ID
customer_id = sys.argv[1]  # Retrieve customer ID from command line argument
'''
# Find the subnet and gateway for the given customer ID
subnet_info = df.loc[df['Customer_ID'] == customer_id, 'Subnet'].values
gateway_info = df.loc[df['Customer_ID'] == customer_id, 'Gateway'].values
if not subnet_info or not gateway_info:
    print(f"No network information found for Customer ID {customer_id}")
    exit()
subnet = subnet_info[0]
gateway = gateway_info[0]
'''
def find_customer_info(df, customer_id):
    # Find the row for the given customer ID
    customer_row = df.loc[df['Customer_ID'] == customer_id]
    if customer_row.empty:
        print(f"No information found for Customer ID {customer_id}")
        return None, None
    else:
        # Extract the subnet
        subnet = customer_row['Subnet'].values[0]
        # Calculate the gateway as the first IP in the subnet
        network = ipaddress.ip_network(subnet)
        gateway = str(network[1])  # network[0] is the network address, network[1] is the first usable IP
        return subnet, gateway

subnet, gateway = find_customer_info(df, customer_id)

# Prepare the networks directory to save configurations (if needed)
networks_dir = 'networks'
os.makedirs(networks_dir, exist_ok=True)

# Docker network creation
network_name = f"{customer_id}_network"
create_network_command = f"sudo docker network create --driver bridge --subnet {subnet} --gateway {gateway} {network_name}"
if subprocess.getoutput(f"sudo docker network ls | grep {network_name}"):
    print(f"Network {network_name} already exists. Skipping creation.")
else:
    subprocess.run(create_network_command.split(), check=True)
    print(f"Network {network_name} created successfully.")

# Example of iterating to create containers for each type of container name
container_types = ['host', 'client', 'loc1', 'loc2', 'controller']
for container_type in container_types:
    container_name = f"{customer_id}_{container_type}"
    # Run containers in the newly created network
    docker_run_command = f"sudo docker run -d --name {container_name} --network {network_name} router2c"
    subprocess.run(docker_run_command.split(), check=True)
    print(f"Container {container_name} started in {network_name}.")

print(f"Container creation commands executed for Customer ID {customer_id}.")
