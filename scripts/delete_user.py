#!/usr/bin/env python3

# This script is intended to run independently/interactively
#  instead of via automation (run_pipeline.py).
# It will process arguments instead of reading from the environment.
# It only finds/deletes local.os users


import vcenter_api
import pmsg
import argparse
import getpass

################################ Main #############################
# setup args...
help_text = "Create/Check vCenter users for TKGs install."

parser = argparse.ArgumentParser(description=help_text)
parser.add_argument('-s', '--vsphere_server', required=True, help='vSphere admin user.')
parser.add_argument('-u', '--vsphere_username', required=True, help='vSphere admin user.')
# parser.add_argument('-p', '--vsphere_password', required=True, help='vSphere admin password.')
parser.add_argument('-d', '--delete_username', required=True, help='User to delete.')
args = parser.parse_args()

server = args.vsphere_server
username = args.vsphere_username
# password = args.vsphere_password
delete_username = args.delete_username
prompt_text = "Enter " + username + " password: "
password = getpass.getpass(prompt=prompt_text, stream=None)
    
token = vcenter_api.vcenter_login(server, username, password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)

result = vcenter_api.api_delete(server, "/api/appliance/local-accounts/" + delete_username, token)
if result:
    pmsg.green("User deleted.")
    exit(0)
else:
    pmsg.fail("User: " + delete_username + " not deleted.")
    exit(1)
