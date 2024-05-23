import sqlite3
import json
import subprocess
import os
import ipaddress
import uuid

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found. Please log in again.")
        return None

def get_vpc_details(tenant_uuid, vpc_name):
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT vpc_id, subnet_mask FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    result = c.fetchone()
    conn.close()
    return result if result else None

def validate_subnet_within_vpc(vpc_prefix, subnet_prefix):
    return ipaddress.ip_network(subnet_prefix).subnet_of(ipaddress.ip_network(vpc_prefix))

def create_subnet():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    vpc_name = input("Enter VPC name: ")
    subnet_name = input("Enter Subnet name: ")
    subnet_prefix = input("Enter subnet prefix (e.g., 192.168.1.0/26): ")
    dhcp_start = input("Enter the start of DHCP range (e.g., 192.168.1.50): ")
    dhcp_end = input("Enter the end of DHCP range (e.g., 192.168.1.100): ")

    vpc_details = get_vpc_details(tenant_uuid, vpc_name)
    if not vpc_details:
        print("Specified VPC does not exist.")
        return

    vpc_id, vpc_prefix = vpc_details
    if not validate_subnet_within_vpc(vpc_prefix, subnet_prefix):
        print("Subnet prefix is not within the VPC's IP range.")
        return

    subnet_id = str(uuid.uuid4())  # Generate a unique subnet ID
    subnet_details = {
        'subnet_id': subnet_id,
        'tenant_uuid': tenant_uuid,
        'vpc_id': vpc_id,
        'subnet_name': subnet_name,
        'subnet_prefix': subnet_prefix,
        'dhcp_start': dhcp_start,
        'dhcp_end': dhcp_end,
    }

    temp_file_path = "subnet_details.json"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(subnet_details, temp_file)

    playbook_path = os.path.join(os.getcwd(), "create_subnet.yml")
    playbook_command = ["ansible-playbook", playbook_path, "-i", "localhost,", "-e", f"@{temp_file_path}"]
    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Subnet creation playbook executed successfully.")
        # Insert subnet details into the database
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO subnets (subnet_id, tenant_uuid, vpc_id, subnet_name, subnet_prefix) 
            VALUES (?, ?, ?, ?, ?)
            """, (subnet_id, tenant_uuid, vpc_id, subnet_name, subnet_prefix))
        conn.commit()
        conn.close()
        print("Subnet created successfully.")
    else:
        print("Failed to execute subnet creation playbook. Error:", result.stderr)

    os.remove(temp_file_path)

if __name__ == "__main__":
    create_subnet()
