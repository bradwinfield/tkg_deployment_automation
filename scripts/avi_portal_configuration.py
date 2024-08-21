#!/usr/bin/env python3

# This script will  set the UI to use the avi-controller certificate created
# in the previous step.
# Uses the API. Manuall, you can use the UI at: system->ssl.

import requests
import json
import os
import urllib3
import helper_avi
import pmsg

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_version = os.environ["avi_version"]
avi_floating_ip = os.environ["avi_floating_ip"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]

if "avi_controller_cert_name" in os.environ.keys():
    cert_name = os.environ["avi_controller_cert_name"]
else:
    cert_name = "avi-controller"

avi_vm_ip = avi_floating_ip

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

# ##################### GET Certificate URL (ref) ##################################
# Get the ref for the avi-controller cert first...
path = "/api/sslkeyandcertificate"
cert_url = None
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)
    for result in obj_details["results"]:
        if result["name"] == cert_name:
            cert_url = result["url"]

if cert_url is None:
    pmsg.fail("Can't find the controller certificate. Note that you must run avi_certificates.py first in your steps file.")
    exit(1)

path = "/api/systemconfiguration"
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)
    obj_details = response.json()
    if obj_details["portal_configuration"]["allow_basic_authentication"] and obj_details["portal_configuration"]["sslkeyandcertificate_refs"] == [cert_url]:
        pmsg.green("System Configuration with Certificate OK.")
        exit(0)
    obj_details["portal_configuration"]["allow_basic_authentication"] = True
    obj_details["portal_configuration"]["sslkeyandcertificate_refs"] = [cert_url]

    # Send it back with updated cert ref...
    response = put_avi_object(api_endpoint, path, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token)
    if response.status_code < 300:
        pmsg.green("System Configuration with Cert OK.")
        controller_status_code = 0
        exit_code = 0
    else:
        pmsg.fail("Can't PUT the system configuration to AVI." + str(response.status_code) + " " + response.text)

else:
    pmsg.fail("Can't retrieve the current system configuration from AVI. Recommend: Set SSL/TLS Certificate to " + cert_name + " manually.")
exit(exit_code)
