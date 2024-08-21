#!/usr/bin/env python3

# Logs into the TKGs Cluster with the os.environ["login_user"]/os.environ["login_password"] user.
# This is called by
# - k8s_supervisor_login_admin.py
# - k8s_supervisor_login.py

# Depends on: set_kubeconfig.py
# Depends on: get_kube_api_vip.py

import os
import helper
import re
import subprocess
import pmsg
import time
# import pdb

# Note, I'm changing the IP address that is used to login to the supervisor.
#       now, I'm using the first IP of the supervisor cluster IP range.
#       it appears that this is what is used as the "floating IP".

# Did the VIP get set?
if "supervisor_cluster_vip" not in os.environ.keys():
    pmsg.fail("The VIP for the supervisor cluster VIP was not provided/found.")
    exit(1)
supervisor_cluster_vip = os.environ["supervisor_cluster_vip"]

supervisor_cluster = os.environ["supervisor_cluster"]
supervisor_network_starting_ip = os.environ["supervisor_network_starting_ip"]
vsphere_namespace = os.environ["vsphere_namespace"]
vsphere_username = os.environ["login_user"]
os.environ["KUBECTL_VSPHERE_PASSWORD"] = os.environ["login_password"]
vsphere_namespace = os.environ["vsphere_namespace"]

#server_ip = supervisor_network_starting_ip
server_ip = supervisor_cluster_vip

def try_to_login(command):
    if helper.run_a_command(command) == 0:
        # Connect to the context
        command = "kubectl config use-context " + server_ip

        if helper.run_a_command(command) == 0:
            # Verify that I'm logged in...
            process = subprocess.Popen(["kubectl", "config", "get-contexts"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, err = process.communicate()
            contexts = output.splitlines()
            for context in contexts:
                if re.search("\\*\\s+"+server_ip+"\\s", context.decode('utf-8')) is not None:
                    pmsg.green("k8s supervisor cluster login as " + vsphere_username + " OK.")
                    return True
    return False


# ##################################### Main ###############################
login_command = "kubectl vsphere login --server " + server_ip + " --vsphere-username " + vsphere_username + " --insecure-skip-tls-verify"

logged_in = False
exit_code = 1
for i in range(1, 30):
    # Try to login until either I'm successful or I try too many times.
    logged_in = try_to_login(login_command)
    if logged_in:
        exit_code = 0
        pmsg.green("Log in OK.")
        break
    pmsg.notice("Will try again in a minute...")
    time.sleep(50)

exit(exit_code)
