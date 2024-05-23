# Use the official Ubuntu 22.04 image as the base
FROM ubuntu:22.04

# Start getting needed packages
RUN apt update && \
    apt install -y net-tools inetutils-ping iproute2 openssh-server sudo iptables dnsmasq python3 python3-paramiko && \
    apt install --reinstall -y libvirt-daemon-system libvirt-clients

# Copy configuration files
COPY files/Tenant-dhcp.conf /etc/Tenant-dhcp.conf

# Keep the container running
CMD tail -f /dev/null
