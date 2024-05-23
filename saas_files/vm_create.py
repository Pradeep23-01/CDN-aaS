import subprocess
import shutil
import sys

def update_meta_data(vm_name):
    meta_data_path = "meta-data"
    with open(meta_data_path, "w") as meta_data_file:
        meta_data_file.write(f"# cloud-config\ninstance-id: {vm_name}\nlocal-hostname: {vm_name}")

# Input VM name
# vm_name = input("Enter VM name: ").strip()
vm_name= sys.argv[1]
network_name= sys.argv[2]

base_image = "/var/lib/libvirt/images/jammy-server-cloudimg-amd64.img"
destination_dir = "/var/lib/libvirt/images"
#libvirt_pool_dir = "/var/lib/libvirt/images"  # Modify this to the appropriate pool directory

# Commands to create and resize the qcow2 file
create_command = [
    "sudo", "qemu-img", "create", "-f", "qcow2", "-F", "qcow2",
    "-o", f"backing_file={base_image}", f"{destination_dir}/{vm_name}.qcow2"
]

resize_command = [
    "sudo", "qemu-img", "resize", f"{destination_dir}/{vm_name}.qcow2", "10G"
]

# Command to create the cidata.iso file
geniso_command = [
    "sudo", "genisoimage", "-output", f"{destination_dir}/{vm_name}-cidata.iso",
    "-volid", "cidata", "-joliet", "-rock", "user-data", "meta-data"
]

try:
    # Execute the create and resize commands
    subprocess.run(create_command, check=True)
    subprocess.run(resize_command, check=True)

    # Update the meta-data file
    update_meta_data(vm_name)

    # Execute the genisoimage command
    subprocess.run(geniso_command, check=True)

    # Move the .iso file to the /var/lib/libvirt/images directory
    iso_src_path = f"{destination_dir}/{vm_name}-cidata.iso"
    iso_dst_path = f"{destination_dir}/{vm_name}-cidata.iso"
    shutil.move(iso_src_path, iso_dst_path)

    print(f"Successfully processed and moved {vm_name}-cidata.iso")

    # virt-install command
    virt_install_command = [
        "sudo", "virt-install", "--virt-type", "kvm", "--name", vm_name,
        "--ram", "7168", "--vcpus", "3", "--os-variant", "ubuntu22.04",
        "--disk", f"path={destination_dir}/{vm_name}.qcow2,format=qcow2",
        "--disk", f"path={destination_dir}/{vm_name}-cidata.iso,device=cdrom",
        "--noautoconsole", "--import", "--network", f"network={network_name}" ]
    subprocess.run(virt_install_command, check=True)

    print(f"VM {vm_name} created successfully.")

except subprocess.CalledProcessError as e:
    print(f"An error occurred while processing {vm_name}: {e}")
except Exception as e:
    print(f"An error occurred while moving {vm_name}-cidata.iso: {e}")
