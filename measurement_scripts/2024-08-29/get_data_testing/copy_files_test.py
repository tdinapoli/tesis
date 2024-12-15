import paramiko
import os
import time
from scp import SCPClient
import subprocess

# Configuration
REMOTE_HOST = 'rp-f05512.local'
REMOTE_USER = 'root'
REMOTE_PASSWORD = 'root'
#REMOTE_PATH = '/root/.local/refurbishedPTI/measurements/2024-09-02'
REMOTE_PATH = '/mnt/data/2024-09-11/0.1800_0.5000'
#LOCAL_PATH = '/home/tomi/Documents/academicos/facultad/tesis/tesis/measurement_scripts/2024-08-29/data/2024-09-11/'
LOCAL_PATH = '/run/media/tomi/FOTOS 1 HDD 1GB/data/2024-09-11/0.1800_0.5000'
CHECK_INTERVAL = 10  # Time interval (in seconds) between checks

def create_ssh_client(host, user, password):
    """Create an SSH client."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=user, password=password)
    return client

def get_directories(client, path):
    """Get a list of directories in the specified path."""
    stdin, stdout, stderr = client.exec_command(f'ls -d {path}/*/')
    directories = stdout.read().decode().splitlines()
    return directories

def copy_directory(client, directory, local_path):
    """Copy the directory from the remote host to the local machine."""
    with SCPClient(client.get_transport()) as scp:
        remote_dir_name = os.path.basename(directory.rstrip('/'))
        local_dir_path = os.path.join(local_path, remote_dir_name)
        scp.get(directory, local_dir_path, recursive=True)

def remove_directory(client, directory):
    """Remove the directory from the remote host."""
    client.exec_command(f'rm -rf {directory}')

def check_amount_screens(client, directory):
    command = f"ls {directory} | wc -l"
    stdin, stdout, stderr = client.exec_command(command)
    result = stdout.read().decode().splitlines()
    return result[0]


def already_copied(directory):
    ls = subprocess.Popen(["ls", f"{directory}"], stdout=subprocess.PIPE)
    stdout = subprocess.check_output(('wc', '-l'), stdin=ls.stdout)
    try:
        return not int(stdout) < 192
    except Exception as e:
        print("Exception in already copied")


def main():
    # Connect to the remote host
    ssh_client = create_ssh_client(REMOTE_HOST, REMOTE_USER, REMOTE_PASSWORD)
    
    # Set to keep track of existing directories
    #existing_directories = set(get_directories(ssh_client, REMOTE_PATH))

    print("Monitoring for new directories...")

    try:
        for wl in range(370, 700):

            if already_copied(f"{LOCAL_PATH}/{wl}"):
                print(f"{LOCAL_PATH}/{wl} directory exists.")
                continue

            copy_dir = f"/mnt/data/2024-09-11/0.1800_0.5000/{wl}"
            amount_screens = int(check_amount_screens(ssh_client, copy_dir))
            while amount_screens < 192:
                amount_screens = int(check_amount_screens(ssh_client, copy_dir))
                print(f"{amount_screens=}")
                time.sleep(5)
            try:
                print(f"copying dir {wl}")
                copy_directory(ssh_client, copy_dir, LOCAL_PATH)
            except Exception as e:
                print(f"Error handling directory {copy_dir}: {e}")

    except KeyboardInterrupt:
        print("Stopped monitoring.")

    finally:
        ssh_client.close()

if __name__ == '__main__':
    main()
