#!/usr/bin/env python3

# Get workload cluster details and replace TLS cert

# Depends on: env_for_cluster_rp.py

import vcenter_api
import pmsg
import os
import helper

################################ Main #############################
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_cluster_id = os.environ["vsphere_cluster_id"]
new_cert = os.environ["supervisor_cluster_tls_endpoint_certificate"]

# Is this certificate a real certificate or just a stub in the config file?
if not helper.valid_certificate(new_cert):
    pmsg.notice("The Supervisor Cluster TLS Endpoint cert is no good in your config.yaml file. skipping.")
    exit(1)

token = vcenter_api.vcenter_login(vsphere_server, vsphere_username, vsphere_password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)

exit_code = 1

# Get the cluster details
path = f'/api/vcenter/namespace-management/clusters/{vsphere_cluster_id}'
response = vcenter_api.api_get(vsphere_server, path, token)
if response is None:
    pmsg.fail("Can't get the cluster details. Recommend adding supervisor cluster certificate manually.")
    exit(exit_code)

# Check / update response["tls_endpoint_certificate"]
cert = response["tls_endpoint_certificate"]

if cert == new_cert:
    pmsg.green("Certificate OK.")
    exit_code = 0
else:
    pmsg.normal("Putting Supervisor Cluster endpoint certificate in place...")
    data = {"tls_endpoint_certificate": new_cert}
    success = vcenter_api.api_patch(vsphere_server, path, token, data, 204)
    if success:
        pmsg.green("Certificate OK.")
        exit_code = 0
    else:
        pmsg.fail("Can't replace Supervisor Cluster tls_endpoint_certificate.")

exit(exit_code)
