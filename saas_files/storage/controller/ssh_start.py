import paramiko
import json
import sys

def ssh_run_command(ssh, command):
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        errors = stderr.read().decode()
        if errors:
            return None, errors
        return stdout.read().decode(), None
    except Exception as e:
        return None, str(e)

def manage_containers(ssh, customer_id, container_names):
    """Function to manage commands on specific containers."""
    for name in container_names:
        if name == f"{customer_id}_client":
            # Install curl and sshpass
            #install_command = f"sudo docker exec {name} sh -c 'apt-get update && apt-get install -y curl sshpass'"
            install_command = f"sudo docker exec {name} sh -c 'export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y curl sshpass && mkdir home/logs'"
            _, errors = ssh_run_command(ssh, install_command)
            if errors:
                print(f"Errors occurred while installing utilities on {name}: {errors}")
            else:
                print(f"Utilities installed successfully on {name}")

            # Execute Python scripts
            scripts = ['details.py', 'get_url.py', 'log.py']
            for script in scripts:
                run_script_command = f"sudo docker exec -d {name} python3 /home/{script} {customer_id}"
                _, script_errors = ssh_run_command(ssh, run_script_command)
                if script_errors:
                    print(f"Errors occurred while running {script} on {name}: {script_errors}")
                else:
                    print(f"Executed {script} on {name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <customer_id>")
        sys.exit(1)

    customer_id = sys.argv[1]
    ssh_host = "192.168.38.13"
    ssh_user = 'vmadm'
    ssh_password = 'vmadm'  # Replace with the correct password
    ssh_port = 22
    file_name = f"{customer_id}_containers.json"

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_host, port=ssh_port, username=ssh_user, password=ssh_password)

        with open(file_name, 'r') as file:
            data = json.load(file)

        container_names = data[ssh_host]['containers']

        for name in container_names:
            # name= container_name = container['name'] sudo apt-get install -y apt-utils
            flask_install_command = f"sudo docker exec {name['name']} sh -c 'apt-get update && apt-get install -y apt-utils python3-flask'"
            _, errors = ssh_run_command(ssh, flask_install_command)
            if errors:
                print(f"Errors occurred while installing Flask on {name['name']}: {errors}")
            else:
                print(f"Successfully installed Flask on {name['name']}")

            nohup_command = f"sudo docker exec -d {name['name']} sh -c 'nohup python3 home/{customer_id}/app.py > home/{customer_id}/app.log 2>&1 &'"
            _, errors = ssh_run_command(ssh, nohup_command)
            if errors:
                print(f"Errors occurred while starting the script on {name['name']}: {errors}")
            else:
                print(f"Script started in background on {name}")

        container_names = [container['name'] for container in data[ssh_host]['containers']]

        manage_containers(ssh, customer_id, container_names)        



    except Exception as e:
        print(f"An error occurred while connecting to SSH or executing commands: {str(e)}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
