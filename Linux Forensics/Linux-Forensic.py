#!/usr/bin/env python3
#RUN THIS AS ROOT! AS WITH GREAT POWERS COMES GREAT RESPONSIBILITIES :D

import os
import sys
import subprocess
import datetime

def execute_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return result.stdout
    except Exception as e:
        print(f"Error executing command: {e}")
        return ""
def main():

    if os.geteuid() != 0:
        print("You need to run this script as root!")
        sys.exit(1)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f"forensic_data_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    commands = [
        ("uname -a", "system_info.txt"), #DISTRO
        ("lsb_release -a", "lsb_release.txt"), #OSINFO
        ("ps aux", "process_list.txt"), #PSLIST CHECKS 
        ("ss -tuln", "network_connections.txt"), #OPEN NETWORK CONNECTIONS - NO NETSTAT DEPENDENCY
        ("ip addr show", "ip_addresses.txt"), #ALTERNATIVE TO IFCONFIG
        ("df -h", "disk_space.txt"), #DISK SPACE CHECKS
        ("cat /etc/passwd", "passwd.txt"), #CHECKS FOR PASSWD 
        ("cat /etc/group", "group.txt"), #CHECK FOR GROUP ACCNTS
        ("cat /var/log/auth.log", "auth_log.txt"), #CHECKS FOR AUTH LOG
        ("cat /var/log/syslog", "sys_log.txt"), #CHECKS FOR SYSLOG 
        ("cat ~/.ssh/known_hosts", "known_ssh_hosts.txt"), #CHECKS FOR KNOWN SSH 
        ("cat ~/.bash_history", "bash_history.txt"), #CHECKS FOR BASH HISTORY
    ]

    #CHECK FOR INSTALLED APPLICATIONS 
    with open("/etc/os-release") as f:
        os_release_data = f.read()
    distro_name = ""
    for line in os_release_data.split("\n"):
        if line.startswith("ID_LIKE="):
            distro_name = line.split("=")[1].strip('"').lower()
            break

    if "debian" in distro_name:
        command = ["dpkg", "--get-selections"]
    elif "rhel" in distro_name or "fedora" in distro_name or "centos" in distro_name:
        command = ["rpm", "-qa"]
    else:
        print("Unsupported distribution")
        exit()

    output = subprocess.check_output(command)
    installed_packages_file = os.path.join(output_dir, "installed_packages.txt")
    with open(installed_packages_file, "w") as f:
        f.write(output.decode())
    #CHECK FOR INSTALLED APPS COMPLETED 

    for command, output_file in commands:
        print(f"Executing: {command}")
        print(f"Executing: Installed Software Check")
        output = execute_command(command)
        with open(os.path.join(output_dir, output_file), "w") as f:
            f.write(output)
    print(f"Forensic data collected in {output_dir}")
if __name__ == "__main__":
    main()