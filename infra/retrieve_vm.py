import sqlite3
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found. Please log in again.")
        return None

def retrieve_vms():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    # Optional: Ask for a specific VPC or subnet if needed
    vpc_name = input("Enter VPC name to retrieve VMs for (or leave blank to retrieve all for tenant): ")
    subnet_prefix = input("Enter subnet prefix to retrieve VMs for (or leave blank for all within VPC): ")

    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()

    if vpc_name and subnet_prefix:
        query = "SELECT vm_name, ram_size, num_cpus, subnet_name FROM VMs WHERE tenant_uuid=? AND vpc_name=? AND subnet_prefix=?"
        params = (tenant_uuid, vpc_name, subnet_prefix)
    elif vpc_name:
        query = "SELECT vm_name, ram_size, num_cpus, subnet_name FROM VMs WHERE tenant_uuid=? AND vpc_name=?"
        params = (tenant_uuid, vpc_name)
    else:
        query = "SELECT vm_name, ram_size, num_cpus, subnet_name FROM VMs WHERE tenant_uuid=?"
        params = (tenant_uuid,)

    c.execute(query, params)
    vms = c.fetchall()

    if vms:
        print("\nYour VMs:")
        for vm in vms:
            print(f"- VM Name: {vm[0]}, RAM Size: {vm[1]} GB, CPUs: {vm[2]}, Subnet: {vm[3]}")
    else:
        print("No VMs found.")

    conn.close()

if __name__ == "__main__":
    retrieve_vms()
