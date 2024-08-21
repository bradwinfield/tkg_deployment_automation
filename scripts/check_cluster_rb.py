#!/usr/bin/env python3

# Checks to see if a psp is installed in the cluster.
# If not, installs it.
# Assumes that the command 'kubectl' is available.
# Assumes we are logged-in to the cluster and the context is already set.

import helper
import pmsg
import re

# First, make sure that the 'auth-users' with restricted PSP is in place...
helper.run_a_command("kubectl create clusterrolebinding auth-users --clusterrole=psp:vmware-system-restricted --group=system:authenticated")

cluster_role_binding_yaml_file = "templates/workload_cluster_rolebinding.yaml"

# What is the name of the clusterrolebinding in the template to look for?
with open(cluster_role_binding_yaml_file) as file:
    cb_yaml = [line.rstrip() for line in file]

crb_name = None
state = "look_for_metadata"
for i in range(0, len(cb_yaml)):
    line = cb_yaml[i]
    pmsg.normal(line)
    if state == "look_for_metadata":
        if "metadata:" in line:
            # The next line starting with "name:" contains the crb name
            state = "look_for_name"
    if state == "look_for_name":
        if "name:" in line:
            parts = re.split(':', line.replace(' ', ''))
            crb_name = parts[1]
            break

if crb_name is None:
    pmsg.fail("Can't determine the Cluster Role Binding name in template: " + crb_name)
    exit(1)

# Check/Create:

# Is the clusterrolebinding there?
if not helper.check_for_result(["kubectl", "get", "clusterrolebindings"], crb_name):
    # Create the cluster role binding...
    # No interpolation needed yet.
    if helper.run_a_command("kubectl apply -f " + cluster_role_binding_yaml_file) == 0:
        # Check it
        if helper.check_for_result(["kubectl", "get", "clusterrolebindings"], crb_name):
            pass
    else:
        pmsg.fail("Failed to create clusterrolebinding... Recommend running by hand.")
        exit(1)
pmsg.green("Cluster Role Binding OK.")
exit(0)
