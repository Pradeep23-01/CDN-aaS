import sqlite3
import os

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found. Ensure you're logged in.")
        return None

def retrieve_subnets():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return

    vpc_name = input("Enter the VPC name to list its subnets: ")

    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()

    # First, get the VPC ID to ensure it belongs to the tenant and exists
    c.execute("SELECT vpc_id FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    vpc = c.fetchone()

    if not vpc:
        print("No VPC found with the name", vpc_name)
        conn.close()
        return

    vpc_id = vpc[0]

    # Retrieve all subnets associated with the VPC
    c.execute("SELECT subnet_name, subnet_prefix FROM subnets WHERE vpc_id=?", (vpc_id,))
    subnets = c.fetchall()

    if not subnets:
        print("No subnets found for the VPC", vpc_name)
    else:
        print(f"Subnets in VPC {vpc_name}:")
        for subnet in subnets:
            print(f"- {subnet[0]} with prefix {subnet[1]}")

    conn.close()

if __name__ == "__main__":
    retrieve_subnets()
