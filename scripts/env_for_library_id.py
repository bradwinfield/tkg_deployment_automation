#!/usr/bin/env python3

# Get additional variables needed by the create_vsphere_namespace.py script.
#
# Additional variables needed but not found in config.yaml are:
# - content_library_id
# - avi_content_library_id

import os
import vcenter_api
import pmsg
import helper
import pdb

# Get server and credentials from the environment...
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
cluster_name = os.environ["cluster_name"]
content_library = os.environ["content_library"]
avi_content_library = os.environ["avi_content_library"]

token = vcenter_api.vcenter_login(vsphere_server, vsphere_username, vsphere_password)

if len(token) < 1:
    pmsg.fail("Can't login to the vCenter API.")
    exit(1)

# Get content library id
if "content_library_id" not in os.environ.keys():
    apipath = "/api/content/library?action=find"
    data = {"name": content_library}
    bstring = vcenter_api.api_post_returns_content(vsphere_server, apipath, token, data, 200)
    if bstring is not None:
        content_library_id = bstring.decode('utf-8').strip('[]"')
        helper.add_env_override(True, "content_library_id", content_library_id)
    else:
        pmsg.fail("Can't find the content library.")
        exit(1)

if "avi_content_library_id" not in os.environ.keys():
    data = {"name": avi_content_library}
    bstring = vcenter_api.api_post_returns_content(vsphere_server, apipath, token, data, 200)
    if bstring is not None:
        avi_content_library_id = bstring.decode('utf-8').strip('[]"')
        helper.add_env_override(False, "avi_content_library_id", avi_content_library_id)
    else:
        pmsg.fail("Can't find the AVI content library.")
        exit(1)

exit(0)
