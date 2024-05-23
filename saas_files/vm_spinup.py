import os
import pandas as pd
import subprocess
import sys

# Load the mapping.csv into a DataFrame
df = pd.read_csv('updated_dataframe.csv')

# Prompt the user for the customer ID
customer_id = sys.argv[1] #input("Enter the Customer ID (ex: customer_7) : ")

# Find the subnet for the given customer ID
subnet_info = df.loc[df['Customer_ID'] == customer_id, 'Subnet'].values
if not subnet_info:
    print(f"No subnet information found for Customer ID {customer_id}")
    exit()
subnet = subnet_info[0]
base_ip = subnet.split('/')[0]

# Calculate the starting and ending IP for DHCP
dhcp_start = base_ip.rsplit('.', 1)[0] + '.2'  # e.g., "10.0.0.2"
dhcp_end = base_ip.rsplit('.', 1)[0] + '.31'  # e.g., "10.0.0.31" for 30 IPs

# Prepare the networks directory
networks_dir = 'networks'
os.makedirs(networks_dir, exist_ok=True)

# Generate the network XML with NAT mode and DHCP range
network_xml = f"""
<network>
  <name>{customer_id}_network</name>
  <forward mode='nat'/>
  <bridge name='{customer_id}-sw'/>
  <ip address='{base_ip}' netmask='255.255.255.0'>
    <dhcp>
      <range start='{dhcp_start}' end='{dhcp_end}'/>
    </dhcp>
  </ip>
</network>
"""

# Save the XML to a file
network_xml_path = os.path.join(networks_dir, f'{customer_id}_network.xml')
with open(network_xml_path, 'w') as file:
    file.write(network_xml)

# Check if the network already exists
existing_networks = subprocess.getoutput("sudo virsh net-list --all")
if f"{customer_id}_network" not in existing_networks:
    # Network doesn't exist, define and start it
    os.system(f"sudo virsh net-define {network_xml_path}")
    os.system(f"sudo virsh net-start {customer_id}_network")
    print(f"Network {customer_id}_network defined and started successfully.")
else:
    print(f"Network {customer_id}_network already exists. Skipping definition and start.")

# Define and start the network using virsh (this requires libvirt and sudo privileges)
#os.system(f"sudo virsh net-define {network_xml_path}")
#os.system(f"sudo virsh net-start {customer_id}_network")

# print(f"Network for Customer ID {customer_id} defined and started successfully.")
'''
# Example of iterating to create 5 VMs for each type of name
vm_types = ['host', 'client', 'loc1', 'loc2', 'controller']
for _, row in df.iterrows():
    customer_id = row['Customer_ID']
    for vm_type in vm_types:
        vm_name = f"{customer_id}_{vm_type}"
        # Construct and run the command (this is a placeholder command; replace with your actual command)
        os.system(f"sudo python3 vm_create.py {vm_name} {customer_id}_network")
'''
# Find the specific row for the given customer ID
customer_row = df[df['Customer_ID'] == customer_id]

if customer_row.empty:
    print(f"No information found for Customer ID {customer_id}")
else:
    # Assuming subnet and network creation steps are here...

    # Create VMs only for the specified customer ID
    vm_types = ['host', 'client', 'loc1', 'loc2', 'controller']
    network_name = f"{customer_id}_network"
    for vm_type in vm_types:
        vm_name = f"{customer_id}_{vm_type}"
        # Construct and run the command
        os.system(f"sudo python3 vm_create.py {vm_name} {network_name}")

    print(f"VM creation commands executed for Customer ID {customer_id}.")
