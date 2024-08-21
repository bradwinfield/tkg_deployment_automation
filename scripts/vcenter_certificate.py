#!/usr/bin/env python3

# Get workload cluster details and replace TLS cert


import vcenter_api
import pmsg
import os

################################ Main #############################
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
new_cert = os.environ["vcenter_tls_certificate"]

token = vcenter_api.vcenter_login(vsphere_server, vsphere_username, vsphere_password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (9)

exit_code = 1

# Get the cluster details
path = "/api/vcenter/certificate-management/vcenter/tls"
response = vcenter_api.api_get(vsphere_server, path, token)
if response is None:
    pmsg.fail("Can't get the vCenter TLS certificate. Recommend adding vCenter TLS certificate manually.")
    exit(exit_code)

cert = response["tls_endpoint_certificate"]

if cert == new_cert:
    pmsg.green("Certificate OK.")
    exit_code = 0
else:
    pmsg.normal("Putting vCenter TLS certificate in place...")
    data = {"??certificate": new_cert}
    success = vcenter_api.api_post(vsphere_server, path, token, data, 204)
    if success:
        pmsg.green("Certificate OK.")
        exit_code = 0
    else:
        pmsg.fail("Can't replace Supervisor Cluster tls_endpoint_certificate.")

exit(exit_code)
