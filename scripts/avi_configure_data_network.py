#!/usr/bin/env python3

import requests
import json
import os
import urllib3
import helper
import helper_avi
import pmsg
import re
import time

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_version = os.environ["avi_version"]
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
data_network_ip = os.environ["data_network_ip"]
data_network_vsphere_portgroup_name = os.environ["data_network_vsphere_portgroup_name"]
data_network_static_starting_address_ipv4 = os.environ["data_network_static_starting_address_ipv4"]
data_network_static_address_count = os.environ["data_network_static_address_count"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token):
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    network_details = json.loads(response.text)

    if response.status_code == 200:
        return response, network_details
    else:
        pmsg.fail("Error retrieving network config: " + str(response.status_code) + response.text)
    return response, None

def put_avi_object(api_endpoint, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # send it back
    uuid = obj_details["uuid"]
    path = "/api/network/" + uuid

    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.put(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
    return response

def find_network(avi_network, api_endpoint, path, login_response, avi_username, avi_password, token):
    response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
    if obj_details is None:
        return False, None, None
    else:
        # walk through all the network objects
        for i in range(0, obj_details["count"]):
            network = obj_details["results"][i]
            if network["name"] == avi_network:
                update_network = network
                pmsg.green("AVI network found OK.")
                return True, response, update_network
    return False, None, None

# ################### LOGIN ###############################################
# Login and get session ID...
logged_in = False
exit_code = 1
login_response = helper_avi.login(api_endpoint, False, avi_username, avi_password)
if login_response.status_code >= 300:
    pmsg.fail("Can't login to AVI.")
    exit(exit_code)
logged_in = True
token = helper_avi.get_token(login_response, "")

time.sleep(60)
# ##################### GET AVI Object #############################################
path = "/api/network"
found_network = False
# Try for a while because the sync from vCenter to AVI may take a while...
for i in range(1, 20):
    found_network, response, update_network = find_network(data_network_vsphere_portgroup_name, api_endpoint, path, login_response, avi_username, avi_password, token)
    if found_network:
        break
    else:
        time.sleep(10)

if found_network:
    token = helper_avi.get_token(response, token)
    # Now update the update_network and PUT it back
    avi_network_ip_parts = re.split('/', data_network_ip)
    network_number = avi_network_ip_parts[0]
    mask = int(avi_network_ip_parts[1])
    # calculate the ending IP
    end_ip = helper.get_address_with_offset(data_network_static_starting_address_ipv4, int(data_network_static_address_count))

    prefix = {
        "ip_addr": {"addr": network_number, "type": "V4"}, "mask": mask
    }

    static_ip_range = {
        "range": {
            "begin":
                {"addr": data_network_static_starting_address_ipv4, "type": "V4"},
            "end":
                {"addr": end_ip, "type": "V4"}
        },
        "type": "STATIC_IPS_FOR_VIP_AND_SE"
    }

    configured_subnet = [{"prefix": prefix, "static_ip_ranges": [static_ip_range]}]
    update_network["configured_subnets"] = configured_subnet

    response = put_avi_object(api_endpoint, response, update_network, avi_vm_ip, avi_username, avi_password, token)
    if response.status_code < 300:
        pmsg.green("AVI network updated OK.")
        exit_code = 0
    else:
        pmsg.fail("Can't update the network in AVI: " + str(response.status_code) + " " + response.text)
else:
    pmsg.fail("Can't find network: " + data_network_vsphere_portgroup_name + " in AVI.")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)
