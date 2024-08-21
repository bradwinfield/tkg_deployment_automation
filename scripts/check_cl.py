#!/usr/bin/env python3
# NOTE: This script is not quite complete. It does everything from checking/creating Content Libaries
#       to adding files to the content library. I believe it fails if the transfer takes longer
#       than the 5 minute default timeout. You would have to add calls to keep the session alive
#       or change the default timeout to be long enough to upload the file.
# Create content libraries and add content
# Depends on: env_for_library_id.py
# Depends on: env_for_cluster_rp.py

import base64
import os
import pmsg
import helper
import requests
import json
import ssl
import urllib3
import pdb

urllib3.disable_warnings()

def add_file_to_library(url, headers, cl_id, local_file_path, file_name):
    # First, is the file in there already?
    # Get a list of the items in this library. Is our file in the list? If not, then upload it.
    path = "/api/content/library/item?action=find"
    data = {"name": file_name, "library_id": cl_id}
    response = requests.post(url + path, headers=headers, json=data, verify=False)
    if response.status_code < 300:
        items = json.loads(response.text)
        if len(items) > 0:
            pmsg.green("Content Library file " + file_name + " OK.")
            return True
    else:
        pmsg.fail("Can't get items out of library.")
        return False

    # ##### This call creates a stub file only. No content is sent yet.
    # See: https://developer.vmware.com/apis/vsphere-automation/v7.0U3/content/api/content/library/item/post/
    path = "/api/content/library/item"
    # Types supported: ["ovf", "iso", "vm-template" ]. Both AVI and TKRs are "ovf" types.
    data = {
        "cached": False,
        "description": file_name,
        "library_id": cl_id,
        "name": file_name,
        "type": "ovf"
    }
    response = requests.post(url + path, headers=headers, json=data, verify=False)
    if response.status_code > 299:
        pmsg.fail("Can't create new item in library: " + file_name + ". Recommend adding manually. " + str(response.status_code) + ":" + response.text)
        return False

    obj = json.loads(response.text)
    library_item_id = obj

    # ##### This step creates a "Session" in which I can send file contents.
    path = "/api/content/library/item/update-session"
    data = {
        "client_progress": 0,
        "library_item_id": library_item_id,
    }
    response = requests.post(url + path, headers=headers, json=data, verify=False)
    if response.status_code > 299:
        pmsg.fail("Can't create update session to push file.")
        return False

    # ##### This call tells vSphere that we want to send content over the session. No file contents sent yet.
    # See: https://developer.vmware.com/apis/vsphere-automation/latest/content/api/content/library/item/update-session/update_session_id/file/post/
    update_session_id = json.loads(response.text)
    path = "/api/content/library/item/update-session/" + update_session_id + "/file"
    pdb.set_trace()
    headers["Content-Type"] = "application/json"
    data = {"name": file_name, "source_type": "PUSH"}
    response = requests.post(url + path, headers=headers, json=data, verify=False)
    if response.status_code > 299:
        pmsg.fail("Can't prepare session to push file contents. " + str(response.status_code) + ":" + response.text)
        return False

    # Parse out the response to get the upload endpoint so I can finally send file contents.
    obj = json.loads(response.text)
    upload_endpoint = obj["upload_endpoint"]["uri"]

    # ##### Now I can finally send file contents.
    pmsg.normal("Sending '" + local_file_path + "' to: " + upload_endpoint + "...")
    headers["Content-Type"] = "application/octet-stream"
    myfiles = {'file': open(local_file_path, 'rb')}
    # with open(local_file_path, 'rb') as f:
    response = requests.put(upload_endpoint, files=myfiles, headers=headers, verify=False)
    if response.status_code > 299:
        pmsg.fail("Can't send file contents. " + str(response.status_code) + ":" + response.text)
        return False
    pmsg.green("Content Library file " + file_name + " OK.")
    return True

def create_library(headers, lib_name, datastore_id):
    # Create content library. See: https://developer.vmware.com/apis/vsphere-automation/latest/content/api/content/local-library/post/
    data = {
        "storage_backings": [
            {
                "datastore_id": datastore_id,
                "type": "DATASTORE"
            }
        ],
        "description": "Library created by automation.",
        "type": "LOCAL",
        "version": 2,
        "name": lib_name
    }
    path = "/api/content/local-library"
    response = requests.post(url + path, headers=headers, json=data, verify=False)
    if response.status_code < 300:
        return json.loads(response.text)
    else:
        return ""


############################################ MAIN ###################################
# Disable SSL certificate verification
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
ssl_context.verify_mode = ssl.CERT_NONE

vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
content_library = os.environ["content_library"]
tkr_name = "tbd"
avi_content_library = os.environ["avi_content_library"]
avi_ova_name = os.environ["avi_ova_name"]

content_library_id = ""
avi_content_library_id = ""

if "datastore_id" not in os.environ.keys():
    pmsg.fail("Datastore ID not found in environment. This step depends upon 'env_for_cluster_rp.py' and 'env_for_library_id.py")
    exit(1)

datastore_id = os.environ["datastore_id"]

if "content_library_id" in os.environ.keys():
    content_library_id = os.environ["content_library_id"]
if "avi_content_library_id" in os.environ.keys():
    avi_content_library_id = os.environ["avi_content_library_id"]

local_file_path = os.environ["local_file_path"]

url = "https://" + vsphere_server

# Connect
path = "/api/session"
creds = vsphere_username + ":" + vsphere_password
base64_creds = base64.b64encode(bytes(creds, 'utf-8'))
headers = {"authorization": "Basic "+base64_creds.decode('ascii')}
response = requests.post(url + path, headers=headers, verify=False)

if response.status_code != 201:
    pmsg.fail("Can't connect to: " + url)
    exit(1)

headers["vmware-api-session-id"] = response.headers["vmware-api-session-id"]

# Get a local library to see what the json data looks like...
path = "/api/content/local-library/" + avi_content_library_id
response = requests.get(url+path, headers=headers, verify=False)

#if content_library_id == "":
#    # Create the tanzu library
#    content_library_id = create_library(headers, content_library, datastore_id):
#    if content_library_id != "":
#        pmsg.green("Created Content Library: " + content_library + " OK.")
#    else:
#        pmsg.fail("Can't create library " + content_library + ". " + response.status_code + ": " + response.text)
#else:
#    pmsg.green("Content library " + content_library + ":" + content_library_id + " OK.")
#
#
#if content_library_id != "":
#    result = add_file_to_library(url, headers, content_library_id, local_file_path, tkr_name)

if avi_content_library_id == "":
    # Create the avi library
    avi_content_library_id = create_library(headers, avi_content_library, datastore_id)
    if avi_content_library_id != "":
        pmsg.green("Created Content Library: " + avi_content_library + " OK.")
    else:
        pmsg.fail("Can't create library " + avi_content_library + ".")
        exit(1)
else:
    pmsg.green("Content library " + avi_content_library + ":" + avi_content_library_id + " OK.")

if avi_content_library_id != "":
    file_ok = add_file_to_library(url, headers, avi_content_library_id, local_file_path, avi_ova_name)
    if not file_ok:
        pmsg.fail("Can't add file to content library.")
        exit(1)
exit(0)        
