import sqlite3
import uuid
import json
import subprocess
from datetime import datetime, timedelta
import os
import ipaddress

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def read_tenant_uuid():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None

def vpc_exists(tenant_uuid, vpc_name, prefix):
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT * FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    if c.fetchone():
        conn.close()
        return True
    c.execute("SELECT * FROM vpcs WHERE tenant_uuid=? AND subnet_mask=?", (tenant_uuid, prefix))
    if c.fetchone():
        conn.close()
        return True
    conn.close()
    return False

def create_vpc():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        return

    vpc_name = input("Enter VPC name: ")
    prefix = input("Enter prefix (e.g., 192.168.1.0/24): ")
    zone = input("Enter Zone: ")

    if vpc_exists(tenant_uuid, vpc_name, prefix):
        print("A VPC with the given name or prefix already exists for this tenant.")
        return

    network = ipaddress.ip_network(prefix, strict=False)
    hosts = list(network.hosts())
    gateway_ip = str(hosts[0])
    namespace_ip = str(hosts[1])

    vpc_details = {
        'vpc_id': str(uuid.uuid4()),
        'tenant_uuid': tenant_uuid,
        'vpc_name': vpc_name,
        'prefix': prefix,
        'gateway_ip': gateway_ip,
        'namespace_ip': namespace_ip,
        'zone': zone,
    }

    temp_file_path = "vpc_details.json"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(vpc_details, temp_file)

    playbook_path = os.path.join(os.getcwd(), "create_vpc.yml")
    playbook_command = ["ansible-playbook", playbook_path, "-i", "localhost,", "-e", f"@{temp_file_path}"]
    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"VPC '{vpc_name}' creation playbook executed successfully.")
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("INSERT INTO vpcs (vpc_id, tenant_uuid, vpc_name, subnet_mask, zone) VALUES (?, ?, ?, ?, ?)",
                  (vpc_details['vpc_id'], tenant_uuid, vpc_name, prefix, zone))
        conn.commit()
        conn.close()
        print(f"VPC '{vpc_name}' created successfully with ID {vpc_details['vpc_id']}.")
    else:
        print("Failed to execute VPC creation playbook. Error:", result.stderr)

    os.remove(temp_file_path)

if __name__ == "__main__":
    create_vpc()
