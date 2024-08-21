#!/usr/bin/env python3

# Class and Methods for interacting with the MOB3 SOAP interface.
# Note: Only adding the avi-admin user to Global Permissions.

# Depends on: env_for_create_global_permissions.py

import requests
import re
import os
import pmsg
# import urllib.parse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

vsphere_server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
tkg_user = os.environ["tkg_user"]
# tkg_role = os.environ["tkg_role"]
# tkg_role_id = os.environ["tkg_role_id"]
avi_vsphere_username = os.environ["avi_vsphere_username"]
avi_role = os.environ["avi_role"]
avi_role_id = os.environ["avi_role_id"]

full_url = "https://" + vsphere_server + "/invsvc/mob3/?moid=authorizationService&method=AuthorizationService.AddGlobalAccessControlList"

def login_and_get_nonce(full_url):
    nonce = ""

    # Create a session and set the authentication headers
    session = requests.session()
    session.auth = (username, password)

    # Make a GET request to retrieve information from the vSphere MOB
    response = session.get(full_url, verify=False)

    if response.status_code == 200:
        parts = re.search('vmware-session-nonce. type=.hidden. value=.([\\d\\-a-z]+)', response.text)
        if parts is None:
            return ""
        nonce = parts[1]
        return session, nonce

def add_user_to_global_permissions(session, full_url, user, role_id, nonce):
    permissions_body = "<permissions><principal><name>" + user + "</name><group>false</group></principal><roles>" + role_id + "</roles><propagate>true</propagate></permissions>"
    post_data = "vmware-session-nonce=" + nonce + "&permissions=" + permissions_body

    # Add a global permission...
    full_url_post = full_url + "&" + post_data 
    response2 = session.post(full_url_post, verify=False)

    if response2.status_code != 200:
        pmsg.fail("Can't add user/role: " + user + "/" + role_id + ".")
        return False
    return True


# ##################################### Main ###################################
session, nonce = login_and_get_nonce(full_url)
if nonce == "":
    pmsg.fail("Can't find the vmware-session-nonce in mob call.")
    exit(1)

#if add_user_to_global_permissions(session, full_url, tkg_user, tkg_role_id, nonce):
#    pmsg.green("User/role " + tkg_user + "/" + tkg_role + " global permission OK.")
#else:
#    pmsg.fail("Failed to add User/role " + tkg_user + "/" + tkg_role + " as a global permission.")
#    exit(1)

if add_user_to_global_permissions(session, full_url, avi_vsphere_username, avi_role_id, nonce):
    pmsg.green("User/role " + avi_vsphere_username + "/" + avi_role + " global permission OK.")
else:
    pmsg.fail("Failed to add User/role " + avi_vsphere_username + "/" + avi_role + " as a global permission.")
    exit(1)

exit(0)
