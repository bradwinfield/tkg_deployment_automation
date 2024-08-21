#!/usr/bin/env python3

# Retrieves cluster passwords and private keys by loggining into
# vCenter, pulling the Supervisor Cluster master passwords and
# then logs into the Supervisor Cluster to get the secrets holding
# the workload cluster password and private keys.

# Need to 'pip3 install paramiko' so python can use paramiko libs.
# Will prompt for vCenter FQDN or IP and the PW first if not found
# in the environment (vsphere_server and vsphere_password env vars).

import paramiko
import re
import time
import getpass
import helper
import os

if 'vsphere_server' in os.environ:
    vchost = os.environ['vsphere_server']
    vcpw = os.environ['vsphere_password']
else:
    vchost = input("Enter vCenter FQDN or IP: ")
    vcpw = getpass.getpass(prompt='Password: ', stream=None)
schost = "Found when /usr/lib/vmware-wcp/decryptK8Pwd.py is run."
username = 'root'

# #################### Supporting Functions ##################
def display_secret(ssh_obj, expression, lines):
    clusters  = []
    for line in lines:
        if re.search(expression, line):
            parts = re.split("\\s+", line)
            ns = parts[0]
            secret_name = parts[1]
            cluster_name = re.sub("-ssh.*", "", secret_name)

            if re.search('password', line):
                cmd = f"kubectl get secret -n {ns} {secret_name} -o jsonpath=" + "{'.data.ssh-passwordkey'} | base64 -d"
            else:
                cmd = f"kubectl get secret -n {ns} {secret_name} -o jsonpath=" + "{'.data.ssh-privatekey'} | base64 -d"
            ssh_stdin, ssh_stdout, ssh_stderr = ssh_obj.exec_command(cmd)
            time.sleep(3)
            response = ssh_stdout.channel.in_buffer.read(4000, 4.0).decode().splitlines()

            # Output the password to stdout but put the private key into a file...
            if re.search('password', line):
                print(f'Password found for cluster: {cluster_name} --')
                print("ssh vmware-system-user@<IPADDR> # pw: " + response[0] + "\n")
                clusters.append(cluster_name)
            else:
                filename = "/tmp/" + secret_name
                if os.path.exists(filename):
                    os.chmod(filename, 0o774)
                f = open(filename, "w")
                for sline in response:
                    f.write(sline + "\n")
                f.close()
                os.chmod(filename, 0o400)
                print(f'Private key found for cluster: {cluster_name} --')
                print("ssh vmware-system-user@<IPADDR> -i " + filename + "\n")
    return clusters

# answers
sc_pw = ""
wc_pws = []

ssh_vc = paramiko.SSHClient()
ssh_vc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh_vc.connect(vchost, username=username, password=vcpw)
except:
    print("Can't connect to vCenter at: " + vchost + ". Check server name, username and password. Make sure ssh is turned on in vCenter:5480.")
    exit(1)

cmd = 'python3 /usr/lib/vmware-wcp/decryptK8Pwd.py'
print("Getting Supervisor Cluster Password...")
ssh_stdin, ssh_stdout, ssh_stderr = ssh_vc.exec_command(cmd)
response = ssh_stdout.channel.in_buffer.read(512, 4.0).decode().splitlines()

for line in response:
    if line.startswith("PWD: "):
        sc_pw = line[5:]
        print("Supervisor Cluster Password --")
        print(sc_pw)
    if line.startswith("IP: "):
        schost = line[4:]

print("\nTo login to the Supervisor Cluster at " + schost + ", use --")
print(f'ssh {username}@{schost} # pw: {sc_pw}' + "\n\n")

# Now I can ssh to the supervisor cluster and get the secrets that hold the workload cluster
# password and private key...
ssh_sc = paramiko.SSHClient()
ssh_sc.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh_sc.connect(schost, username=username, password=sc_pw)
except:
    print ("Can't connect to Supervisor Cluster at: " + schost + ".")
    print(f'{username}@{schost} ({sc_pw})')
    exit(1)
cmd = 'kubectl get secrets -A | grep -- -ssh'
ssh_stdin, ssh_stdout, ssh_stderr = ssh_sc.exec_command(cmd)
time.sleep(3)
response = ssh_stdout.channel.in_buffer.read(20000, 4.0).decode().splitlines()

# Look for the ssh private key and the ssh password secrets and get the values...
clusters = display_secret(ssh_sc, '-ssh\\s|-ssh-password\\s', response)

# Get the IP addresses for the worker nodes
for cluster in clusters:
    cmd = "kubectl get nodes -o wide --context " + cluster
    print ("\nList of workload cluster nodes with IP addresses --")
    print("If you don't see nodes and ip addresses, login to the cluster and run '" + cmd + "'.")
    helper.run_a_command(cmd)

time.sleep(1)
ssh_vc.close()
ssh_sc.close()
