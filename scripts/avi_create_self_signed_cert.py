#!/usr/bin/env python3

# This script will create a self-signed Web UI cert in AVI if the flag (config.yaml)
# avi_create_self_signed_cert: true

import requests
import json
import os
import urllib3
import helper
import interpolate
import helper_avi
import pmsg

urllib3.disable_warnings()

# Get local variables from environment to make it cleaner looking code.
avi_create_self_signed_cert = os.environ["avi_create_self_signed_cert"]
if avi_create_self_signed_cert == 'false':
    pmsg.notice("Not asking AVI to create a self-signed certificate for the UI.")
    exit(0)

avi_version = os.environ["avi_version"]
avi_floating_ip = os.environ["avi_floating_ip"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_certificate = os.environ["avi_certificate"]
avi_create_self_signed_cert = os.environ["avi_create_self_signed_cert"]
user = os.environ["USER"]
site_name = os.environ["site_name"]

template_file = "templates/avi_new_certificate.json"

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

def post_avi_object(api_endpoint, path, login_response, obj_details, avi_vm_ip, avi_username, avi_password, token):
    # Must set the header and the cookie for a PUT call...
    headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
    cookies = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
    response = requests.post(api_endpoint + path, verify=False, json=obj_details, headers=headers, cookies=cookies)
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

# Does the certificate already exist in AVI?
path = "/api/sslkeyandcertificate"
cert_name_found = False
response, obj_details = get_avi_object(api_endpoint, path, login_response, avi_username, avi_password, token)
if obj_details is not None:
    token = helper_avi.get_token(response, token)
    for result in obj_details["results"]:
        if result["name"] == cert_name:
            cert_name_found = True
            # Make sure this discovered cert is in the environment...
            avi_certificate = result['certificate']['certificate']
            helper.add_env_override(True, "avi_certificate", avi_certificate)

    if cert_name_found:
        pmsg.green("Already exists. Controller (client/leaf) Certificate OK.")
        exit(0)


# Read in json create-cert template and Interpolate
json_data = json.loads(interpolate.interpolate_from_environment_to_string(template_file))

# ##################### Create a new controller certificate #############################################
# Send POST to AVI
response = post_avi_object(api_endpoint, path, login_response, json_data, avi_vm_ip, avi_username, avi_password, token)
if response.status_code < 300:
    pmsg.green("AVI Controller Certificate OK.")
    exit_code = 0

    # Get the certificate itself.
    json_response_text = json.loads(response.text)
    avi_certificate = json_response_text['certificate']['certificate']

    # Put new cert into the environment for later steps.
    helper.add_env_override(True, "avi_certificate", avi_certificate)

exit(exit_code)
