import subprocess
import datetime
import pandas as pd
import json
import requests

def log_request(user_name,cid, server_ip):
    """Log user request to a file."""
    with open("user_requests_host.log", "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp}, {user_name}, {cid}, {server_ip}\n")

def fetch_server_content(server_ip):
    """Fetch and return content from the server application."""
    try:
        response = requests.get(f"http://{server_ip}:5000")
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.RequestException as e:
        return f"Failed to fetch content from the server at {server_ip}. Error: {e}"

def main():
    user_name = input("Please enter your name: ")
    print(f"Hello {user_name}!")
    print("These are the Server locations available: ")
    print("1. host")
    print("2. loc1")
    print("3. loc2")
    loc = input("Please enter your Location: ")

    df = pd.read_csv("updated_dataframe.csv")
    print("Available Customer IDs:")
    print(df['Customer_ID'])
    customer_id = input("Please enter the Customer ID: ")

    if customer_id in df['Customer_ID'].values:
        container_name = f"{customer_id}_controller"
        command = f"sudo docker exec {container_name} python3 /home/get_server1.py {customer_id} {customer_id}_{loc}"
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            server_ip = result.stdout.strip()
            #print(server_ip)
            print(f"Hello {user_name}, you are being routed to the server at {server_ip}.")

            # Fetch content from the server application and print it
            server_content = fetch_server_content(server_ip)
            print("Content from the server:")
            print(server_content)

            # Log the request
            log_request(user_name, customer_id ,server_ip)

        except subprocess.CalledProcessError as e:
            print(f"Failed to execute script inside container. Error: {e}")
    else:
        print("Invalid Customer ID.")

if __name__ == "__main__":
    main()
