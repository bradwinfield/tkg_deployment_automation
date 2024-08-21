#!/usr/bin/env python3

# Get additional variables needed by the create_vsphere_namespace.py script.
#
# Additional variables needed but not found in config.yaml are:
# - vsphere_cluster_id
# - parent_resource_pool_id
# - avi_resource_pool_id

import os
import pmsg
import helper
import vsphere_mob
from pyVmomi import vim

# Already in the environment?
if os.environ.keys() >= {"vsphere_cluster_id", "parent_resource_pool_id", "avi_resource_pool_id"}:
    exit(0)

# Get server and credentials from the environment...
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]
datastore = os.environ["datastore"]
cluster_name = os.environ["cluster_name"]
avi_resource_pool = os.environ["avi_resource_pool"]

mob = vsphere_mob.vsphere_mob(False)
c = mob.login(vsphere_server, vsphere_username, vsphere_password, True)
content = c.content
if content is None:
    pmsg.fail("Could not login to the MOB SOAP API. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (2)

dcobj = mob.find_object(content.rootFolder, vsphere_datacenter, vim.Datacenter, False)
if dcobj is None:
    pmsg.fail("Can't find the datacenter in the vSphere MOB.")
    exit(1)

for ds in dcobj.datastore:
    if ds.name == datastore:
        helper.add_env_override(True, "datastore_id", ds._moId)
        break

cluster_obj = mob.find_object(dcobj.hostFolder, cluster_name, vim.ClusterComputeResource, False)
if cluster_obj is None:
    pmsg.fail("Can't find the cluster in the vSphere MOB.")
    exit(1)

helper.add_env_override(False, "vsphere_cluster_id", cluster_obj._moId)

# Also add the parent resourcePool ID
helper.add_env_override(False, "parent_resource_pool_id ", cluster_obj.resourcePool._moId)

# While I'm in the MOB, check for AVI Resource Pool... does it exist already?
# For now, just look directly in the Resource Pool directly under the cluster
for rp in cluster_obj.resourcePool.resourcePool:
    if rp.name == avi_resource_pool:
        helper.add_env_override(False, "avi_resource_pool_id", rp._moId)

exit(0)
