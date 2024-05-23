import paramiko
import sys
import subprocess

def ssh_into_vm_and_run(customer_id, ssh_host, ssh_port, ssh_user, ssh_pass, local_log_directory):
    """ SSH into a VM, fetch logs from containers, and save them locally. """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_pass)
        print(f"Connected to {ssh_host}.")

        # Fetching container names excluding controller and client containers
        list_containers_cmd = f"sudo docker ps --filter name={customer_id} --format '{{{{.Names}}}}' | grep -Ev 'controller|client'"
        stdin, stdout, stderr = ssh.exec_command(list_containers_cmd)
        container_names = stdout.read().decode().strip().splitlines()

        # Loop through each container to fetch and copy logs
        for name in container_names:
            # Define the paths for the log files inside the Docker container and on the local machine
            log_path = f"/home/{customer_id}/app.log"  # Adjust path as necessary within the container
            remote_temp_path = f"/tmp/{name}_app.log"  # Temporary path on the Docker host

            # Command to copy the log file from the container to the Docker host's temporary location
            docker_cp_command = f"sudo docker cp {name}:{log_path} {remote_temp_path}"
            ssh.exec_command(docker_cp_command)

            # Command to copy the log file from the Docker host to the local system running this script
            local_log_path = f"{local_log_directory}/{name}_app.log"
            scp_command = f"sudo sshpass -p '{ssh_pass}' scp -o StrictHostKeyChecking=no {ssh_user}@{ssh_host}:{remote_temp_path} {local_log_path}"
            subprocess.run(scp_command, shell=True, check=True)
            print(f"Log file fetched for container {name} and saved to {local_log_path}")

        ssh.close()
    except Exception as e:
        print(f"Failed to connect or execute on {ssh_host}: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <customer_id>")
        sys.exit(1)

    customer_id = sys.argv[1]
    local_log_directory = "/home/logs"

    # Assuming SSH details are known and fixed
    ssh_host = "192.168.38.13"
    ssh_port = 22
    ssh_user = "vmadm"
    ssh_pass = "vmadm"

    ssh_into_vm_and_run(customer_id, ssh_host, ssh_port, ssh_user, ssh_pass, local_log_directory)

if __name__ == '__main__':
    main()
