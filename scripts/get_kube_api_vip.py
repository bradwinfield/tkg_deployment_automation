#!/usr/bin/env python3
import requests
import json
import os
import urllib3
import helper
import time
import pmsg

urllib3.disable_warnings()


def get_kube_api_vip(api_endpoint, login):
    # Send a GET request to the API endpoint to retrieve the list of virtual services
    response = requests.get(api_endpoint + "/api/vsvip", verify=False, cookies=dict(sessionid= login.cookies['sessionid']))

    # Parse the response and retrieve the VIPs
    if response.status_code == 200:
        vs_list = json.loads(response.text)
        for vs in vs_list["results"]:
            if "--kube-system-kube-apiserver-lb-svc" in vs["name"]:
                for vip in vs["vip"]:
                    print(vip["ip_address"]["addr"])
                    helper.add_env_override(True, "supervisor_cluster_vip", vip["ip_address"]["addr"])
                    return True
    else:
        print("Error retrieving virtual services: ", response.text)
    return False


# ################################## Main ################################
if "supervisor_cluster_vip" in os.environ.keys():
    exit(0)

# Set up the API endpoint and authentication details
# If we have a DNS entry pre-created for AVI at this DC, then use this...
# server = os.environ["avi_controller_ip"]
# If not, use the IP address...
server = os.environ["avi_floating_ip"]
api_endpoint = "https://" + server
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]

# Set up the HTTP headers and authentication token
headers = {
    "Content-Type": "application/json",
}
#    "X-Avi-Version": "18.2.7",

# Login and get session ID...
login = requests.post(api_endpoint + "/login", verify=False, data={'username': avi_username, 'password': avi_password})

# Try to retrieve the kube_api VIP. We may have to wait a while before it is allocated in AVI after
#  terraform starts to create the supervisor cluster.
for i in range(1, 30):
    if get_kube_api_vip(api_endpoint, login):
        pmsg.green("Kube API VIP OK.")
        exit(0)
    time.sleep(60)

pmsg.fail("Can't find the kube API VIP from AVI.")
exit(1)
