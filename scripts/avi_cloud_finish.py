#!/usr/bin/env python3

import requests
import json
import os
import urllib3
import helper_avi
import pmsg
import re

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
avi_network = os.environ["avi_network"]
avi_network_ip = os.environ["avi_network_ip"]

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

    cloud_details = json.loads(response.text)

    if response.status_code == 200:
        return response, cloud_details
    else:
        pmsg.fail("Error retrieving cloud config: " + str(response.status_code) + response.text)
    return response, None

def put_avi_object(api_endpoint, path, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # send it back

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

# ##################### GET IPAM Provider Ref #######################
path = "/api/ipamdnsproviderprofile"
avi_ipam_provider_ref = None
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)
    if obj_details["count"] > 0:
        for ipam in obj_details["results"]:
            if ipam["name"] == avi_ipam_provider_name:
                avi_ipam_provider_ref = ipam["url"]
                break

if avi_ipam_provider_ref is None:
    pmsg.fail("Can't find the IPAM profile reference that was created for Default-Cloud.")
    exit(1)

# ##################### GET the AVI management network ref ########################
path = "/api/vimgrnwruntime"    
avi_management_network_ref = None
response, vim_objects = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if vim_objects is not None:
    token = helper_avi.get_token(response, token)
    if vim_objects["count"] != 1:
        for obj in vim_objects["results"]:
            if obj["name"] == avi_network:
                avi_management_network_ref = obj["url"]
                break

if avi_management_network_ref is None:
    pmsg.fail("Can't find the management network reference.")
    exit(1)

# ##################### GET AVI Object #############################################
# If modifying an AVI object, get the current configuration of whatever you are going to modify...
path = "/api/cloud"
response, cloud_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if cloud_details is not None:
    token = helper_avi.get_token(response, token)
    if cloud_details["count"] != 1:
        pmsg.warning("AVI seems to have already been configured with multiple 'Clouds'. There should only be 'Default-Cloud'. Proceeding anyway.")

    if cloud_details["results"][0]["name"] == "Default-Cloud":
        pmsg.green("Cloud data retrieved OK.")
        token = helper_avi.get_token(response, token)
        default_cloud_details = cloud_details["results"][0]
        default_cloud_details["ipam_provider_ref"] = avi_ipam_provider_ref
        default_cloud_details["vcenter_configuration"]["management_network"] = avi_management_network_ref
        netparts = re.split('\/', avi_network_ip)
        msubnet = {
            "ip_addr": {
                "addr": netparts[0],
                "type": "V4"
            },
            "mask": int(netparts[1])
        }
        default_cloud_details["vcenter_configuration"]["management_ip_subnet"] = msubnet

        # Setup json object in preparation for PUTting to AVI...
        uuid = default_cloud_details["uuid"]
        path = "/api/cloud/" + uuid
        response = put_avi_object(api_endpoint, path, login_response, default_cloud_details, avi_vm_ip, avi_username, avi_password, token)
        if response.status_code < 300:
            pmsg.green("AVI Default-Cloud finished OK.")
            exit_code = 0
        else:
            pmsg.fail("Can't update Defaut-Cloud. " + str(response.status_code) + " " + response.text)
    else:
        pmsg.fail("I am expecting Default-Cloud to be the first cloud defined but it isn't. Recommend deleting all Clouds except Default-Cloud.")
else:
    pmsg.fail("Can't retrieve AVI data from path: " + path + ".")

if logged_in:
    helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)

exit(exit_code)
