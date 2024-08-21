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
data_network_gateway_ip = os.environ["data_network_gateway_ip"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]
api_endpoint = "https://" + avi_vm_ip

def get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token):
    # Send a GET request to the API endpoint to retrieve the Default-Cloud details...
    # return json object of config
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    response = requests.get(api_endpoint + path, verify=False, headers=headers, cookies=dict(sessionid=login_response.cookies['sessionid']))

    cloud_details = json.loads(response.text)

    if response.status_code == 200:
        return response, cloud_details
    else:
        pmsg.fail("Error retrieving cloud config: " + str(response.status_code) + response.text)
    return response, None

def put_avi_object(api_endpoint, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # Update or construct AVI object json... ## SAMPLE ##
    uuid = obj_details["uuid"]

    # send it back
    path = "/api/vrfcontext/" + uuid

    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.put(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
    return response


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

# ##################### GET AVI Object #############################################
# If modifying an AVI object, get the current configuration of whatever you are going to modify...
vrf_object = None
path = "/api/vrfcontext"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)

    # Find the global one...
    for vrf in obj_details["results"]:
        if vrf["name"] == "global":
            vrf_object = vrf
            break

    if vrf_object is not None:
        static_route = {
            "prefix": {"ip_addr": {"addr": "0.0.0.0", "type": "V4" }, "mask": 0},
            "next_hop": {"addr": data_network_gateway_ip, "type": "V4"},
            "route_id": "1"
        }
        vrf_object["static_routes"] = [static_route]

# ##################### PUT AVI Object #############################################
        response = put_avi_object(api_endpoint, login_response, vrf_object, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("AVI VRF Static Route OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't set the AVI VRF Statid Route. " + str(response.status_code) + " " + response.text)
    else:
        pmsg.fail("Can't find the AVI global VRF context at: " + path + ".")
else:
    pmsg.fail("Can't retrieve AVI VRF Contexts from path: " + path + ".")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)
