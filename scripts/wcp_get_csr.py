#!/usr/bin/env python3

# This script will get a Certificate Signing Request from vCenter only.

# Request Certificate Signing Request (CSR) from vCenter workload cluster API
# The rest of the procedure is manual...
# Use the CSR to request a certificate from whereever you get certs
# Apply the certificate to vCenter WCP so you don't have to use --insecure-skip-tls-verify
# when you login to clusters.

# NOTE: This script was written for a specific customer. You will want to modify it for 
# your environment.

import vcenter_api
import pmsg
import os
import json
import stat

################################ Main #############################
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
cluster_name = os.environ["cluster_name"]
supervisor_cluster = os.environ["supervisor_cluster"]
site_name = os.environ["site_name"]

csr_file_name = f'/tmp/{site_name}_wcp.csr'
exit_code = 1

token = vcenter_api.vcenter_login(vsphere_server, vsphere_username, vsphere_password)
if len(token) < 1:
    pmsg.fail("No token obtained from login api call to vSphere. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (exit_code)

# Get the cluster ID (I only know the cluster name at this point)
cluster_id = None
path = "/rest/vcenter/cluster"
json_obj = vcenter_api.api_get(vsphere_server, path, token)
if json_obj is None:
    pmsg.fail("Can't get the cluster ID given the cluster name: " + cluster_name)
    exit(exit_code)

for value in json_obj["value"]:
    if value["name"] == cluster_name:
        cluster_id = value["cluster"]

# Check to see if I got a cluster ID...
if cluster_id is None:
    pmsg.fail("Can't find cluster ID. I did find these clusters: " + json.dumps(json_obj))
    exit(exit_code)

# Get the CSR...
path = "/api/" + cluster_id + "/csr/tls-endpoint"
data = {
    "country": "US",
    "state_or_province": "TX",
    "email_address": "dont-reply@company.com",
    "locality": "Dallas",
    "organization_name": "DSS",
    "common_name": supervisor_cluster,
    "organization_unit_name": "Platform",
    "key_size": 2048
}
print(f'{vsphere_server}{path} -d {data}')
response = vcenter_api.api_post_returns_content(vsphere_server, path, token, data, 200)
if response is None:
    pmsg.fail("Can't get the CSR from vCenter. Recommend getting vCenter certificate signing request manually.")
    exit(exit_code)

# Put CSR in file
f = open(csr_file_name, "w")
f.write(response.decode().replace('\\n', "\n").replace('"', ""))
f.close()
os.chmod(csr_file_name, stat.S_IRWXG | stat.S_IRWXU | stat.S_IRWXO)

pmsg.blue(response.decode().replace('\\n', "\n").replace('"', ""))
pmsg.normal("Use this CSR to request a certificate. Once received, put the cert in vCenter. See the following doc.")
pmsg.underline("https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-CF707AE9-7BD7-47BC-AAD7-BCF17DCB640D.html")
pmsg.normal("CSR can be found in: " + csr_file_name)

exit(0)
