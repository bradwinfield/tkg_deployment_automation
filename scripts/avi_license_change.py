#!/usr/bin/env python3

# Hits the admin-user-setup page in an AVI vm to initialize the admin user.
# This will only check to see if AVI is ready. 
# It will retry every minute for about 30 minutes until ready or it
# does not respond in this amount of time.

import requests
import pmsg
import urllib3
import os
import time
import json
import sys

urllib3.disable_warnings()

def get_token(response):
    token = ""
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
    if "csrftoken" in cookies_dict.keys():
        token = cookies_dict["csrftoken"]
    return token


avi_version = os.environ["avi_version"]
avi_license = os.environ["avi_license"]
avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
#avi_ip = os.environ["avi_floating_ip"]
avi_ip = os.environ["avi_vm_ip1"]
api_endpoint = "https://" + avi_ip

############################## login ##############################
login = requests.post(api_endpoint + "/login", verify=False, data={'username': avi_user, 'password': avi_password})
if login.status_code != 200:
    pmsg.fail("Can't login to AVI.")
    exit(1)

# Create a 'headers' for the rest of the requests...
headers = {
    "Referer": api_endpoint + "/",
    "Content-Type": "application/json",
    "Accept-Encoding": "application/json",
    "X-CSRFToken": login.cookies["csrftoken"],
    "X-Avi-Version": avi_version
}

############################# Check current license tier #######################
path = "/api/systemconfiguration/?include_name=true&join=admin_auth_configuration.remote_auth_configurations.auth_profile_ref"
response = requests.get(api_endpoint + path, verify=False, cookies=dict(sessionid=login.cookies['sessionid']))
if response.status_code == 200:
    json_obj = json.loads(response.content)
    if json_obj["default_license_tier"] == avi_license:
        pmsg.green("AVI License " + avi_license + " OK.")
        exit(0)
    else:
        pmsg.normal("AVI License tier is: " + json_obj["default_license_tier"] + ". Will attempt to change to " + avi_license + " ...")
else:
    pmsg.fail("Can't run the config audit in prep for " + avi_license + " license. HTTP: " + str(response.status_code) + "; " + response.text)
    exit(1)

############################### Audit ###########################
path = "/api/config-audit/tier/" + avi_license
response = requests.get(api_endpoint + path, verify=False, cookies=dict(sessionid=login.cookies['sessionid']))
if response.status_code == 200:
    pmsg.normal("AVI License check complete.")
    obj = json.loads(response.content)
    #print(json.dumps(obj))
    if obj["config_licensing_status"] != "passed":
        pmsg.fail("The audit failed so I can't change the license to " + avi_license)
        exit(1)
else:
    pmsg.fail("Can't run the config audit in prep for " + avi_license + " license. HTTP: " + str(response.status_code) + "; " + response.text)
    exit(1)

# If I got here, then the license audit finished ok. Convert the license...
######################## STEP 1 ##########################
path = "/api/albservices/status"
response = requests.get(api_endpoint + path, verify=False, cookies = dict(sessionid= login.cookies['sessionid']))
if response.status_code != 200:
    pmsg.fail("Can't GET albservicesconfig." + str(response.status_code) + "; " + response.text)
    exit(1)

# And now change the license...
token = get_token(login)

path = "/api/systemconfiguration/?include_name"
payload = {"replace": {"default_license_tier": avi_license}}
data = str(payload).replace("'", '"')
response = requests.patch(api_endpoint + path, verify=False, headers=headers, data=data, cookies=login.cookies)
if response.status_code != 200:
    pmsg.fail("Can't change license to " + avi_license + ". Recommend manual operation. " + str(response.status_code) + "; " + response.text)
    exit(1)
pmsg.green("AVI License " + avi_license + " OK.")
exit(0)
