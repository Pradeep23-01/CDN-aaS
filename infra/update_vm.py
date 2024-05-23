import sqlite3
import json
import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None

def update_vm_name():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        print("Please log in to update a VM.")
        return
    
    vm_id = input("Enter the VM ID to update: ")
    new_vm_name = input("Enter the new name for the VM: ")
    
    # Connect to the database
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    
    # Check if the VM exists
    cursor.execute("SELECT * FROM VMs WHERE tenant_uuid=? AND vm_id=?", (tenant_uuid, vm_id))
    if cursor.fetchone() is None:
        print("VM not found.")
        return
    
    # Prepare details for the playbook
    vm_details = {
        'vm_id': vm_id,
        'tenant_uuid': tenant_uuid,
        'new_vm_name': new_vm_name,
    }

    temp_file_path = "vm_update_details.json"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(vm_details, temp_file)
    
    # Path to your playbook - adjust as necessary
    playbook_path = "/path/to/your/playbook/update_vm_name.yml"
    
    # Execute the playbook
    playbook_command = ["ansible-playbook", playbook_path, "-e", f"@{temp_file_path}"]
    result = subprocess.run(playbook_command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("VM name updated successfully in the system.")
        # Update the VM name in the database
        cursor.execute("UPDATE VMs SET vm_name=? WHERE vm_id=? AND tenant_uuid=?", (new_vm_name, vm_id, tenant_uuid))
        conn.commit()
    else:
        print("Failed to update VM name. Error:", result.stderr.decode())
    
    # Cleanup
    os.remove(temp_file_path)
    conn.close()

if __name__ == "__main__":
    update_vm_name()
