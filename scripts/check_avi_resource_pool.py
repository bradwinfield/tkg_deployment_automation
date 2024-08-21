#!/usr/bin/env python3

# Checks for and creates the AVI resource group.
# Depends on: env_for_cluster_rp.py
# Depends on: env_for_library_id.py

import vcenter_api
import pmsg
import os
import helper

def create_resource_pool(server, token, resource_pool, vsphere_cluster_id, parent_resource_pool_id):
    found_rg = False
    json_data = {"name": resource_pool, "parent": parent_resource_pool_id}
    id = vcenter_api.api_post_returns_content(server, "/api/vcenter/resource-pool", token, json_data, 201)
    if id is not None:
        pmsg.green ("Resource Pool: " + resource_pool + " created.")
        found_rg = True
        helper.add_env_override(True, "avi_resource_pool_id", id.decode().strip('"'))
    else:
        pmsg.fail ("I can't create the Resource Group: " + resource_pool + ". You may want to create it manually. Please check Resource groups in vCenter and try again.")
    return found_rg


################################ Main #############################

server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
avi_resource_pool = os.environ["avi_resource_pool"]
parent_resource_pool_id = os.environ["parent_resource_pool_id"]
vsphere_cluster_id = os.environ["vsphere_cluster_id"]

if "avi_resource_pool_id"  in os.environ.keys():
    # Found that the AVI resource pool already exists.
    pmsg.green("AVI Resource pool OK.")
    exit(0)

token = vcenter_api.vcenter_login(server, username, password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)

exit_code = 1

if create_resource_pool(server, token, avi_resource_pool, vsphere_cluster_id, parent_resource_pool_id):
    pmsg.green("Resource Pool: " + avi_resource_pool + " OK.")
    exit_code = 0
else:
    pmsg.fail("Resource Pool: " + avi_resource_pool + " not OK.")

exit(exit_code)
