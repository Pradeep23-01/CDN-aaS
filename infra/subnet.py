import sqlite3
import subprocess
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found. Ensure you're logged in.")
        return None

def vpc_exists_for_tenant(tenant_uuid, vpc_name):
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def select_vpc(tenant_uuid):
    vpc_name = input("\nEnter the name of the VPC you want to manage subnets for: ")
    if vpc_exists_for_tenant(tenant_uuid, vpc_name):
        return vpc_name
    else:
        print("VPC doesn't exist for this tenant.")
        return None

def subnet_menu():
    global_tenant_uuid = read_tenant_uuid_from_file()
    if not global_tenant_uuid:
        print("Error: Tenant UUID not found. Please log in again.")
        return
    
    vpc_name = select_vpc(global_tenant_uuid)
    if not vpc_name:
        return  # Exiting if VPC doesn't exist or no VPC name was entered

    while True:
        print(f"\nSubnet Management for VPC: {vpc_name}")
        print("1. Create Subnet")
        print("2. Retrieve all Subnets")
        print("3. Update Subnet")
        print("4. Delete Subnet")
        print("5. Return to the previous menu")
        choice = input("Select an option: ")
        if choice == '1':
            subprocess.run(["python3", "create_subnet.py", global_tenant_uuid, vpc_name])
        elif choice == '2':
            subprocess.run(["python3", "retrieve_subnet.py", global_tenant_uuid, vpc_name])
        elif choice == '3':
            subprocess.run(["python3", "update_subnet.py", global_tenant_uuid, vpc_name])
        elif choice == '4':
            subprocess.run(["python3", "delete_subnet.py", global_tenant_uuid, vpc_name])
        elif choice == '5':
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    subnet_menu()
