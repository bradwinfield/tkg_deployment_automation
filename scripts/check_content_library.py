#!/usr/bin/env python3

# Create content libraries and add content using the 'govc' command.
# Arguments:
# 1. lib_name
# 2. pathname -or- sub_url (e.g. https://wp-content.vmware.com/v2/latest/lib.json)

import helper
import os
import pmsg
import re
import sys
import time

def add_file_to_library(cl_id, pathname):
    # First, is the file in there already?
    m = re.search('[^/]+$', pathname)
    filename = "Can't figure out filename from pathname."
    if m is not None:
        filename = m.group().strip('.ova')

    # Get a list of the items in this library. Is our file in the list? If not, then upload it.
    items = helper.run_a_command_get_stdout(["govc", "library.ls", f'/{lib_name}/*'])
    for item in items:
        if filename in item:
            pmsg.green(f'Content Library item {filename} OK.')
            return True

    if helper.run_a_command(f'govc library.import {cl_id} {pathname}') > 0:
        pmsg.fail(f'Can\'t upload file: {pathname}.')
        exit(1)
    return True

def get_lib_id(lib_name):
    results = helper.run_a_command_get_stdout(["govc", "library.info", lib_name])
    for line in results:
        if re.match('ID:', line) is not None:
            m = re.search('\S+\-.*', line)
            if m is not None:
                return m.group()
    return None

def create_library(lib_name):
    return helper.run_a_command_get_stdout(["govc", "library.create", lib_name])


############################################ MAIN ###################################
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
cmd = sys.argv[0]
usage = f'USAGE: {cmd} [ContentLibraryName] [PathToUploadFile | SubscriptionURL]'

if len(sys.argv) < 3:
    pmsg.fail(usage)
    exit(1)

lib_name = sys.argv[1]
pathname = sys.argv[2]

os.environ["GOVC_URL"] = vsphere_server
os.environ["GOVC_USERNAME"] = vsphere_username
os.environ["GOVC_PASSWORD"] = vsphere_password
os.environ["GOVC_INSECURE"] = "true"

# Get the library ID
lib_id = get_lib_id(lib_name)

if lib_id is None:
    if "https://" in pathname:
        helper.run_a_command(f'govc library.create -sub {pathname} -sub-ondemand=true {lib_name}')
    else:
        helper.run_a_command(f'govc library.create {lib_name}')

# Wait a bit for the library to be created and then look for the ID again...
max_tries = 10
try_num = 0
while try_num < max_tries:
    try_num += 1
    # Get the library ID
    lib_id = get_lib_id(lib_name)
    if len(lib_id) > 10:
        break
    time.sleep(5)

if len(lib_id) < 10:
    pmsg.fail(f'Can\'t create library {lib_name}')
    exit(1)

# Upload the file...
if "https://" not in pathname:
    if not add_file_to_library(lib_id, pathname):
        exit(1)

exit(0)
