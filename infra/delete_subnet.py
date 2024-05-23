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

def delete_subnet():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    vpc_name = input("Enter the VPC name containing the subnet you wish to delete: ")
    subnet_mask = input("Enter the subnet mask of the subnet you wish to delete: ")

    # Fetch subnet details based on the tenant_uuid, vpc_name, and subnet_mask
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT vpc_id FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    vpc = c.fetchone()

    if vpc:
        vpc_id = vpc[0]
        c.execute("SELECT subnet_id FROM subnets WHERE tenant_uuid=? AND vpc_id=? AND subnet_mask=?", (tenant_uuid, vpc_id, subnet_mask))
        subnet = c.fetchone()

        if subnet:
            subnet_id = subnet[0]
            subnet_details = {
                'tenant_uuid': tenant_uuid,
                'vpc_id': vpc_id,
                'subnet_id': subnet_id,
                'subnet_mask': subnet_mask,
            }

            temp_file_path = "subnet_delete_details.json"
            with open(temp_file_path, 'w') as temp_file:
                json.dump(subnet_details, temp_file)

            playbook_command = ["ansible-playbook", "delete_subnet.yml", "-i", "localhost", "-e", f"@{temp_file_path}"]
            result = subprocess.run(playbook_command, capture_output=True, text=True)

            if result.returncode == 0:
                print("Subnet deletion playbook executed successfully.")
                c.execute("DELETE FROM subnets WHERE subnet_id=?", (subnet_id,))
                conn.commit()
                print(f"Subnet with mask {subnet_mask} deleted successfully from VPC {vpc_name}.")
            else:
                print("Failed to delete subnet. Error:", result.stderr)
            os.remove(temp_file_path)
        else:
            print("No matching subnet found for deletion.")
    else:
        print("Specified VPC does not exist.")

    conn.close()

if __name__ == "__main__":
    delete_subnet()
