import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def vm_menu():
    global_tenant_uuid = read_tenant_uuid_from_file()
    if not global_tenant_uuid:
        print("Error: Tenant UUID not found. Please log in again.")
        return
    while True:
        print(f"\nVM Management for Tenant UUID: {global_tenant_uuid}")
        print("1. Create VM")
        print("2. Retrieve all VMs")
        print("3. Update VM")
        print("4. Delete VM")
        print("5. Return to the main menu")
        choice = input("Select an option: ")
        if choice == '1':
            subprocess.run(["python3", "create_vm.py"])
        elif choice == '2':
            subprocess.run(["python3", "retrieve_vm.py"])
        elif choice == '3':
            subprocess.run(["python3", "update_vm.py"])
        elif choice == '4':
            subprocess.run(["python3", "delete_vm.py"])
        elif choice == '5':
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    vm_menu()
