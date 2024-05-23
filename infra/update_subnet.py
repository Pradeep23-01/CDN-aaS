import sqlite3
import json
import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found. Please log in.")
        return None

def update_subnet():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    vpc_name = input("Enter the VPC name containing the subnet: ")
    subnet_name = input("Enter the existing subnet name you wish to update: ")
    new_subnet_name = input("Enter the new subnet name: ")
    new_description = input("Enter the new description for the subnet (optional): ")

    # Assume that a playbook exists for subnet updates, requiring these details
    subnet_details = {
        'tenant_uuid': tenant_uuid,
        'vpc_name': vpc_name,
        'old_subnet_name': subnet_name,
        'new_subnet_name': new_subnet_name
    }

    temp_file_path = "subnet_update_details.json"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(subnet_details, temp_file)

    playbook_command = ["ansible-playbook", "path/to/update_subnet.yml", "-e", f"@{temp_file_path}"]
    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print("Subnet update playbook executed successfully.")
        # Update the local database with the new subnet name and description
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("UPDATE subnets SET subnet_name=?, description=? WHERE tenant_uuid=? AND subnet_name=? AND vpc_name=?",
                  (new_subnet_name, new_description, tenant_uuid, subnet_name, vpc_name))
        conn.commit()
        conn.close()
        print("Subnet updated successfully in the database.")
    else:
        print("Failed to update subnet. Error:", result.stderr)

    os.remove(temp_file_path)

if __name__ == "__main__":
    update_subnet()
