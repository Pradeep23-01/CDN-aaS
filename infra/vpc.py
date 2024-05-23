import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()  # Ensure we return a clean UUID without newline
    except FileNotFoundError:
        return None

def vpc_menu():
    global_tenant_uuid = read_tenant_uuid_from_file()
    if not global_tenant_uuid:
        print("Error: Tenant UUID not found. Please log in again.")
        return
    
    while True:
        print(f"\nVPC Management for Tenant UUID: {global_tenant_uuid}")
        print("1. Create VPC")
        print("2. Retrieve all VPCs")
        print("3. Update VPC")
        print("4. Delete VPC")
        print("5. Return to the main menu")
        choice = input("Select an option: ")
        if choice == '1':
            subprocess.run(["sudo", "python3", "create_vpc.py"])
        elif choice == '2':
            subprocess.run(["sudo", "python3", "retrieve_vpc.py"])
        elif choice == '3':
            subprocess.run(["sudo", "python3", "update_vpc.py"])
        elif choice == '4':
            subprocess.run(["sudo", "python3", "delete_vpc.py"])
        elif choice == '5':
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    vpc_menu()
