import json
import os
import shutil
import pandas as pd
import re  # For parsing directory names
import sys

# Function to load JSON data from the provided file path
def load_json_input(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Custom function to copy an entire directory tree to a new location with a numerically increasing name
def copytree_to_numerically_named_dir(src, parent_dst_dir, base_name="customer_"):
    # Determine the next directory name with numeric suffix
    existing_dirs = [d for d in os.listdir(parent_dst_dir) if os.path.isdir(os.path.join(parent_dst_dir, d))]
    existing_nums = [int(re.search(f"{base_name}(\\d+)", d).group(1)) for d in existing_dirs if re.match(f"{base_name}\\d+", d)]
    next_num = max(existing_nums) + 1 if existing_nums else 1
    new_dir_name = f"{base_name}{next_num}"
    dst = os.path.join(parent_dst_dir, new_dir_name)
    
    # Copy the directory
    shutil.copytree(src, dst)
    return dst  # Return the path of the newly created directory

# Step 1: Collect user input for the JSON file path
json_file_path = sys.argv[1] # input("Enter the path to the JSON file: ")
data = load_json_input(json_file_path)

# Parse the JSON data
source_data_dir = data['srcdata']
locations = data['locations']
subnet = data['Subnet']

# Step 2: Copy source data to a numerically named new directory under the storage location
storage_location = '/home/vmadm/saas_d/storage/'
# Ensure the storage location exists
if not os.path.exists(storage_location):
    os.makedirs(storage_location)

# Copy the source directory to the new numerically named directory
new_storage_path = copytree_to_numerically_named_dir(source_data_dir, storage_location)

# Step 3: Prepare the pandas DataFrame for storage
csv_file_path = 'updated_dataframe.csv'
if os.path.exists(csv_file_path):
    df = pd.read_csv(csv_file_path)
else:
    df = pd.DataFrame(columns=['Customer_ID','srcdata', 'locations', 'Subnet', 'vm_details'])

# Update the original data with the new storage location
data['srcdata'] = new_storage_path

data['Customer_ID'] = os.path.basename(new_storage_path)
data['vm_details'] = None
# Append the new data to the DataFrame
df = df.append(data, ignore_index=True)

# Save the DataFrame to a CSV file
df.to_csv(csv_file_path, index=False)

print(f"Source data and locations mapping completed successfully and saved to CSV. New data stored in {new_storage_path}")
