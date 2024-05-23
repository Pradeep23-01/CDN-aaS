import sqlite3
import os
from prettytable import PrettyTable

def read_tenant_uuid_from_file():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None

def retrieve_vpcs():
    """Retrieves and displays the list of VPCs for the logged-in tenant in a tabular format."""
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        print("Error: Tenant UUID not provided or could not be retrieved.")
        return

    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()

    # Assuming you have a 'prefix' column for the subnet mask/prefix and a 'zone' column for location in your 'vpcs' table
    cursor.execute("SELECT vpc_name, subnet_mask, zone FROM vpcs WHERE tenant_uuid=?", (tenant_uuid,))
    vpcs = cursor.fetchall()

    if vpcs:
        table = PrettyTable(["VPC Name", "Prefix", "Location"])
        for vpc in vpcs:
            table.add_row([vpc[0], vpc[1], vpc[2]])
        print("\nYour VPCs:")
        print(table)
    else:
        print("You do not have any VPCs.")

    conn.close()

if __name__ == "__main__":
    retrieve_vpcs()
