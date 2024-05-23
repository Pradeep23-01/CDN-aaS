import sqlite3
import json
import subprocess
import os
import uuid

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found. Please log in again.")
        return None

def get_ovs_bridge_name(subnet_name):
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT ovs_bridge_name FROM subnets WHERE subnet_name=?", (subnet_name,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def create_vm():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    # Inputs required for VM creation
    vpc_name = input("Enter VPC name: ")
    subnet_name = input("Enter subnet name: ")
    vm_name = input("Enter VM name: ")
    ram_size = input("Enter RAM size: ")
    num_cpus = input("Enter number of CPUs: ")

    # Prompt the user for the OVS bridge name
    ovs_bridge_name = input("Enter the name of the OVS bridge for the subnet: ")

    if not ovs_bridge_name:
        print("Error: OVS bridge name cannot be empty. VM creation aborted.")
        return

    # VM details to be passed to the playbook
    vm_details = {
        'vm_name': vm_name,
        'ram_size': ram_size,
        'num_cpus': num_cpus,
        'vpc_name': vpc_name,
        'tenant_uuid': tenant_uuid,
        'subnet_name': subnet_name,
        'ovs_bridge_name': ovs_bridge_name
    }

    # Execute playbook with passed variables
    playbook_path = "create_vm.yml"
    playbook_command = [
        "ansible-playbook", playbook_path, "-i", "localhost,", "-e", 
        f"@vm_creation_details.json"
    ] 

    # Save VM details to a JSON file for ansible-playbook
    with open('vm_creation_details.json', 'w') as temp_file:
        json.dump(vm_details, temp_file)

    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"VM '{vm_name}' creation playbook executed successfully.")

        # Insert VM details into the database
        vm_id = str(uuid.uuid4())
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("INSERT INTO VMs (vm_id, tenant_uuid, vpc_name, subnet_name, vm_name, ram_size, num_cpus) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (vm_id, tenant_uuid, vpc_name, subnet_name, vm_name, ram_size, num_cpus))
        conn.commit()
        conn.close()
        print(f"VM '{vm_name}' created successfully with ID {vm_id}.")
    else:
        print("Failed to execute VM creation playbook. Error:", result.stderr)

    os.remove('vm_creation_details.json')  # Clean up the temporary file

if __name__ == "__main__":
    create_vm()
