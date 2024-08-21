#!/usr/bin/env python3

import requests
import json
import os
import urllib3
import helper_avi
import pmsg

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_version = os.environ["avi_version"]
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]
data_network_vsphere_portgroup_name = os.environ["data_network_vsphere_portgroup_name"]
avi_ipam_provider_name = os.environ["avi_ipam_provider_name"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token):
    # Send a GET request to the API endpoint to retrieve the Default-Cloud details...
    # return json object of config
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    ipam_details = json.loads(response.text)

    if response.status_code == 200:
        return response, ipam_details
    else:
        pmsg.fail("Error retrieving IPAM configs: " + str(response.status_code) + response.text)
    return response, None

def post_avi_object(api_endpoint, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # send it back
    path = "/api/ipamdnsproviderprofile"

    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.post(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
    return response

def do_exit(exit_code, msg):
    if logged_in:
        helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)
    if exit_code != 0 and len(msg) > 0:
        pmsg.fail(msg)
    exit(exit_code)


# ################### LOGIN ###############################################
# Login and get session ID...
logged_in = False
exit_code = 1
login_response = helper_avi.login(api_endpoint, False, avi_username, avi_password)
if login_response.status_code >= 300:
    do_exit(exit_code, "Can't login to AVI.")

logged_in = True
token = helper_avi.get_token(login_response, "")

# ##################### GET AVI Data Network Ref first #############################################
path = "/api/network"
avi_data_network_ref = None
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    # walk through all the network objects
    for i in range(0, obj_details["count"]):
        network = obj_details["results"][i]
        if network["name"] == data_network_vsphere_portgroup_name:
            avi_data_network_ref = network["url"]
            pmsg.green("AVI data network reference found OK.")
            break
if avi_data_network_ref is None:
    do_exit(1, "Can't find the avi_data_network_ref in: " + path)

# ##################### GET AVI Object #############################################
path = "/api/ipamdnsproviderprofile"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)

    #  Sample of what came back
    # {"count": 0, "results": []}
    if obj_details["count"] == 0:
        # Here is what I need to send back (POST)
        ipam_profile = {
            "allocate_ip_in_vrf": False,
            "internal_profile": {
                "ttl": 30,
                "usable_networks": [
                    {
                        "nw_ref": avi_data_network_ref
                    }
                ]
            },
            "name": avi_ipam_provider_name,
            "tenant_ref": "https://" + avi_vm_ip + "/api/tenant/admin",
            "type": "IPAMDNS_TYPE_INTERNAL",
        }

# ##################### PUT AVI Object #############################################
        response = post_avi_object(api_endpoint, login_response, ipam_profile, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("AVI IPAM profile for the data/vip network OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't create IPAM profile for the data/vip network in AVI: " + str(response.status_code) + " " + response.text)
    else:
        # if the IPAM profile "vip-data-network" already exists, exit without error... only notice.
        for network in obj_details["results"]:
            if network["name"] == "vip-data-network":
                pmsg.notice("IPAM profile found and may be ok. Please check manually. Quitting IPAM Profile creation.")
                do_exit(0, "")
                break
            do_exit(1, "Expected no IPAM profiles. IPAM profile not found. Quitting IPAM Profile creation.")
else:
    pmsg.fail("Can't retrieve AVI data from path: " + path + ".")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)
    logged_in = False

do_exit(exit_code, "")

