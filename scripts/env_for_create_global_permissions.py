#!/usr/bin/env python3

# Gets the tkg_role_id and the avi_role_id from the MOB and adds them
# to the environment for subsequent steps to use.

import requests
import re
import os
import helper
import pmsg
import pdb
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Already in the environment?
if os.environ.keys() >= {"tkg_role_id", "avi_role_id"}:
    exit(0)

vsphere_server = os.environ["vsphere_server"]
username = os.environ["vsphere_username"]
password = os.environ["vsphere_password"]
tkg_role = os.environ["tkg_role"]
avi_role = os.environ["avi_role"]

# Create a session and set the authentication headers
session = requests.session()
session.auth = (username, password)

# Make a GET request to retrieve information from the vSphere MOB
full_url = "https://" + vsphere_server + "/invsvc/mob3/?moid=authorizationService&method=AuthorizationService.GetRoles"
response = session.get(full_url, verify=False)

if response.status_code == 200:
    parts = re.search('vmware-session-nonce. type=.hidden. value=.([\\d\\-a-z]+)', response.text)
    if parts is None:
        pmsg.fail("Can't find the vmware-session-nonce in mob call.")
        exit(1)
    nonce = parts[1]
    post_data = "vmware-session-nonce=" + nonce

    # Add a global permission...
    full_url_post = full_url + "&" + post_data
    response2 = session.post(full_url_post, verify=False)
    env_new_file = True

    if response2.status_code == 200:
        sections = re.split('<tr><th>Name</th><th>Type</th><th>Value</th>', response2.text)

        # Parse the HTML body and pull out the TKG and AVI role names and find the ID...
        for section in sections:
            if 'name</td><td class="c1">string</td><td>' + tkg_role + '</td>' in section:
                # Parse out the ID for this role...
                parts = re.search('id</td><td class="c1">long</td><td>([\-\d]+)</td>', section)
                helper.add_env_override(env_new_file, "tkg_role_id", parts[1])
                pmsg.green("Role id for " + tkg_role + " (" + parts[1] + ") OK.")
                env_new_file = False

            if 'name</td><td class="c1">string</td><td>' + avi_role + '</td>' in section:
                # Parse out the ID for this role...
                parts = re.search('id</td><td class="c1">long</td><td>([\-\d]+)</td>', section)
                helper.add_env_override(env_new_file, "avi_role_id", parts[1])
                pmsg.green("Role id for " + avi_role + " (" + parts[1] + ") OK.")
                env_new_file = False

    else:
        pmsg.fail("Can't find role list in vCenter.")
        exit(1)
exit(0)
