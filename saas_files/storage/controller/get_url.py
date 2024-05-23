import json
import subprocess
import sys

def run_script(script_name,customer_id):
    """Run a Python script."""
    try:
        subprocess.run(['python3', script_name, customer_id], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running script {script_name}: {e}")

def read_json(file_name):
    """Read JSON data from a file."""
    with open(file_name, 'r') as file:
        return json.load(file)

def write_json(data, file_name):
    """Write JSON data to a file."""
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def generate_webserver_urls(data):
    """Generate web server URLs for each container, excluding 'controller' and 'client'."""
    urls = []
    for container in data.get('192.168.38.13', {}).get('containers', []):
        name = container.get('name', '')
        ip = container.get('ip', '')
        if 'controller' not in name and 'client' not in name:
            url = f'http://{ip}:5000'
            urls.append({'name': name, 'url': url})
    return urls

def main():
    customer_id = sys.argv[1]
    # Path to the Python script and JSON files
    details_script = 'home/details.py'
    input_json_file = f'{customer_id}_containers.json'
    output_json_file = '/home/webserver_urls.json'

    # Run the details.py script
    run_script(details_script, customer_id)

    # Load container data from JSON file
    container_data = read_json(input_json_file)

    # Generate web server URLs
    urls = generate_webserver_urls(container_data)

    # Save the URLs to a new JSON file
    write_json(urls, output_json_file)
    print(f"Web server URLs have been saved to {output_json_file}")

if __name__ == '__main__':
    main()
