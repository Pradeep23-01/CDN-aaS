import sqlite3
import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found. Please log in again.")
        return None

def delete_vm():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    vm_name = input("Enter the VM name to delete: ")

    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()

    # Check if the VM exists
    c.execute("SELECT * FROM VMs WHERE tenant_uuid=? AND vm_name=?", (tenant_uuid, vm_name))
    if not c.fetchone():
        print("Error: VM does not exist.")
        conn.close()
        return

    # Execute playbook with the VM name as a parameter
    playbook_path = "delete_vm.yml"
    playbook_command = [
        "sudo", "ansible-playbook", playbook_path, "-e", f"vm_name={vm_name}"
    ]
    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"VM '{vm_name}' deletion process executed successfully.")

        # Delete VM details from the database
        c.execute("DELETE FROM VMs WHERE tenant_uuid=? AND vm_name=?", (tenant_uuid, vm_name))
        conn.commit()
        print(f"VM '{vm_name}' deleted successfully from the database.")
    else:
        print("Failed to execute VM deletion playbook. Error:", result.stderr.decode())

    conn.close()

if __name__ == "__main__":
    delete_vm()
