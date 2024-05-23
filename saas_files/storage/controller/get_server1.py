import json
import sys

def main():
    # Check that the script has the correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: python script.py <customer_id> <location>")
        sys.exit(1)

    customer_id = sys.argv[1]
    location = sys.argv[2]  # The name of the container whose IP you want to find
    file_name = f"{customer_id}_containers.json"

    # Load the JSON data from the file
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_name}")
        return

    # Assuming the structure includes an IP address, loop through each container
    ssh_host = "192.168.38.13"  # Example SSH host address
    containers = data[ssh_host]['containers']

    # Search for the specified location in the container details
    for container in containers:
        if container['name'] == location:
            #return print(f"IP for {location}: {container['ip']}")
            return print(f"{container['ip']}") # container['ip']

    # If no matching container name is found
    print(f"No container found with the name {location}")

if __name__ == "__main__":
    main()
