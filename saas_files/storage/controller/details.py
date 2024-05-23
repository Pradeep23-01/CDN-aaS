import paramiko
import sys
import socket
import json
import re

def get_hostname():
    return socket.gethostname()

def get_dir_name(hostname):
    match = re.search(r'\d+', hostname)
    if match:
        number = match.group(0)
        dir_name = f"customer_{number}"
        return dir_name
    else:
        return "No numeric part found in hostname"
'''
def ssh_into_vm_and_run(customer_id, ssh_host, ssh_port, ssh_user, ssh_pass):
    try:
        container_data = {ssh_host: {'containers': [], 'error': None}}
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_pass)
        print(f"Connected to {ssh_host}.")

        # Assuming you have a script or command to run here:
        command = f"sudo docker ps --all --format '{{{{.Names}}}}' | grep ^{customer_id}"
        stdin, stdout, stderr = ssh.exec_command(command)
        container_names = stdout.read().decode().strip()


        print(f"Containers for customer {customer_id}: {container_names}")
        ssh.close()
    except Exception as e:
        print(f"Failed to connect or execute on {ssh_host}: {str(e)}")

def ssh_into_vm_and_run(customer_id, ssh_host, ssh_port, ssh_user, ssh_pass):
    container_data = {ssh_host: {'containers': [], 'error': None}}  # Initialize with defaults

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_pass)
        print(f"Connected to {ssh_host}.")

        command = f"sudo docker ps --all --format '{{{{.Names}}}}' | grep {customer_id}"
        stdin, stdout, stderr = ssh.exec_command(command)
        container_names = stdout.read().decode().strip().splitlines()

        container_data[ssh_host]['containers'] = container_names
        ssh.close()
    except Exception as e:
        print(f"Failed to connect or execute on {ssh_host}: {str(e)}")
        container_data[ssh_host]['error'] = str(e)  # Store error information

    return container_data
'''
import paramiko

def ssh_into_vm_and_run(customer_id, ssh_host, ssh_port, ssh_user, ssh_pass):
    container_data = {ssh_host: {'containers': [], 'error': None}}  # Initialize with defaults

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_pass)
        print(f"Connected to {ssh_host}.")

        # Fetching container names
        list_containers_cmd = f"sudo docker ps --all --format '{{{{.Names}}}}' | grep {customer_id}"
        stdin, stdout, stderr = ssh.exec_command(list_containers_cmd)
        container_names = stdout.read().decode().strip().splitlines()

        container_details = []
        for name in container_names:
            # Fetching IP address for each container
            get_ip_cmd = f"sudo docker exec {name} ip -4 addr show eth0 | grep -oP 'inet \K[\d.]+'"
            stdin, stdout, stderr = ssh.exec_command(get_ip_cmd)
            ip_address = stdout.read().decode().strip()

            # Storing container name and IP address
            container_details.append({'name': name, 'ip': ip_address or 'No IP Found'})

        container_data[ssh_host]['containers'] = container_details
        ssh.close()
    except Exception as e:
        print(f"Failed to connect or execute on {ssh_host}: {str(e)}")
        container_data[ssh_host]['error'] = str(e)  # Store error information

    return container_data

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <customer_id>")
        sys.exit(1)

    customer_id = sys.argv[1]
    ssh_port = 22  # Default SSH port
    ssh_user = 'vmadm'
    ssh_pass = 'vmadm'
    #hostname = get_hostname()
    #dir_name = get_dir_name(hostname)
    exclude_suffixes = ['_client', '_controller']
    exclude_vms = [customer_id + suffix for suffix in exclude_suffixes]

    # Simulated VM details, replace with actual data source as needed

    #for vm_name, details in vm_details.items():
    #if vm_name not in exclude_vms and details['vm_status'] == 'Running':
    ssh_host = "192.168.38.13"
    container_data =ssh_into_vm_and_run(customer_id, ssh_host, ssh_port, ssh_user, ssh_pass)
    all_container_data={}
    all_container_data.update(container_data)
    # Save the data to a JSON file
    with open(f"{customer_id}_containers.json", "w") as json_file:
        json.dump(all_container_data, json_file, indent=4)


    print("Data has been saved to JSON file.")

if __name__ == "__main__":
    main()
