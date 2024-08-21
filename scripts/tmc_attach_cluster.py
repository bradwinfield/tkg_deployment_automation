#!/usr/bin/env python3

import requests
import pmsg
import helper
import json
import urllib3
import os

urllib3.disable_warnings()

# This script will attach a cluster to TMC
cluster_name = os.environ["cluster_name"]
tmc_refresh_token = os.environ["tmc_refresh_token"]
tmc_hostname = os.environ["tmc_hostname"]

tmc_yaml_file = "/tmp/tmc.yaml"

# 1. Access Token to get a Access Token from https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize
# access_token=$(curl -k -d "refresh_token=$tmc_refresh_token" https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize | jq -r '.access_token')

# 2. The name of the TMC URL
# Sample call using curl: curl  -k -s 'searchScope.name=*' https://vplpsamer.tmc.cloud.vmware.com/v1alpha1/clusters -H "Authorization: Bearer $access_token" | jq '.clusters[].fullName.name'

# Get Access Token
url = "https://console.cloud.vmware.com"
path = "/csp/gateway/am/api/auth/api-tokens/authorize"
headers = {"key": "Content-Type", "value": "application/x-www-form-urlencoded", "type": "text"}
data = {"key": "refresh_token", "refresh_token": tmc_refresh_token}
response = requests.post(url + path, headers=headers, data=data, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get an access_token from " + url + path + ". " + str(response.status_code) + "; " + response.text)
    exit(1)
stuff = json.loads(response.text)
access_token = stuff["access_token"]

# Prepare to request an "Attach Cluster" request...
# header = {"content-type": "application/json", "key": "Authorization", "value": "Bearer " + access_token, "type": "text"}
header = {"content-type": "application/json", "accept": "application/json", "authorization": "Bearer " + access_token}
data = '{"cluster": {"fullName": {"managementClusterName": "attached", "provisionerName": "attached", "name": "' + cluster_name + '"}, "meta": {}, "spec": {"clusterGroupName": "default"}}}'
# body = {"mode": "raw", "raw": raw_part, "options": {"raw": {"language": "json"}}}
path = "/v1alpha1/clusters"
url = "https://" + tmc_hostname
response = requests.post(url + path, headers=header, data=data, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't request cluster attachment: " + url + path + ". " + str(response.status_code) + "; " + response.text)
    exit(1)
pmsg.blue("Looks good.")

# Get the installer link out of the previous response...
stuff = json.loads(response.text)
installer_link = stuff["cluster"]["status"]["installerLink"]

# Then get TMC agent installer information (yaml)...
response = requests.get(installer_link, headers=[], verify=False)

# Get the yaml to apply to this cluster to create the agent, etc.
yaml = response.text

# Create a temp file with the yaml content
f = open(tmc_yaml_file, "w")
f.write(yaml)
f.close()

helper.run_a_command("kubectl apply -f " + tmc_yaml_file)
os.remove(tmc_yaml_file)
