import sqlite3
import json
import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found. Ensure you're logged in.")
        return None

def delete_vpc():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    vpc_name = input("Enter the name of the VPC you wish to delete: ")

    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()

    # Check if the VPC exists
    c.execute("SELECT vpc_id FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    vpc = c.fetchone()

    if not vpc:
        print(f"No VPC named '{vpc_name}' found.")
        conn.close()
        return

    vpc_id = vpc[0]

    # Prepare VPC details for deletion
    vpc_details = {
        'vpc_id': vpc_id,
        'tenant_uuid': tenant_uuid,
        'vpc_name': vpc_name,
    }

    temp_file_path = "vpc_delete_details.json"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(vpc_details, temp_file)

    # Execute the playbook to delete the VPC
    playbook_command = ["sudo", "ansible-playbook", "/home/vmadm/project/delete_vpc.yml", "-e", f"@{temp_file_path}"]
    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"VPC '{vpc_name}' deletion playbook executed successfully.")
        # Delete the VPC from the database
        c.execute("DELETE FROM vpcs WHERE vpc_id=? AND tenant_uuid=?", (vpc_id, tenant_uuid))
        conn.commit()
        print(f"VPC '{vpc_name}' deleted successfully.")
    else:
        print("Failed to execute VPC deletion playbook.")

    os.remove(temp_file_path)
    conn.close()

if __name__ == "__main__":
    delete_vpc()
