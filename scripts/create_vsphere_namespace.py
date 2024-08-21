#!/usr/bin/env python3

# This script will create a config file from the template "create-vsphere-namespace.yaml"
#  and then it will call the wcpctl.py apply <interpolated config file>

# Depends on: env_for_library_id.py

import interpolate
import pmsg
import helper
import os
import time
import re

config_file = os.environ["config_file"]
template = "templates/create-vsphere-namespace.yaml"
site_name = os.environ["site_name"]
user = os.environ["USER"]
wcpctl_config = "/tmp/" + user + "_" + site_name + "-wcpctl_config.yaml"
vsphere_namespace = os.environ["vsphere_namespace"]

# The TKG user should be the one that performs this action...
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
rc = 1

def check_namespace_services_ready():
    lines = helper.run_a_command_get_stdout(["kubectl", "get", "all", "-n", vsphere_namespace])
    for line in lines:
        if not re.match('^NAME|^service\\S+\\s+LoadBalancer\\s+(\\d+\\.){3}\\d+\\s+(\\d+\\.){3}\\d+', line):
            return False
    return True


# Interpolate...
# add vsphere_owner_domain and vsphere_username_nodomain to environment...
os.environ["vsphere_username_nodomain"] = vsphere_username
interpolate.interpolate_from_environment_to_template(template, wcpctl_config)

# Run wcpctl.py
os.environ["WCP_PASSWORD"] = vsphere_password
result = helper.run_a_command("./scripts/wcpctl.py apply " + wcpctl_config)
if result == 0:
    # Check the namespace to see if it is ready...
    time.sleep(10)
    for i in range(1, 10):
        if check_namespace_services_ready():
            rc = 0
            break
        time.sleep(10)
else:
    pmsg.fail("Failed to create the vSphere namespace.")

# Clean up first...
os.remove(wcpctl_config)
exit(rc)
