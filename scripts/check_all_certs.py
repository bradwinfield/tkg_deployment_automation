#!/usr/bin/env python3

# Dumps details about all certs and the private keys.
# Arguments: <directory>

# The directory is expected to have subdirectories where each one has subdirectories:
# .../avi
# .../vcenter
# .../<others>
#   And eash subdirectory has files
#   *.crt
#   *.key

import sys
import os
import helper
import pmsg
import pdb

def has_cert(subdir):
    for file in os.listdir(subdir):
        if 'crt' in file:
            return True
    return False


if len(sys.argv) < 2:
    pmsg.normal(f'Usage: {sys.argv[0]} <cert parent directory>')
    pmsg.normal("Note: To be run from the tkg-deplyment-automation root directory.")
    exit(1)
directory = sys.argv[1]
user = os.environ["USER"]
os.environ["deployment_log"] = "/tmp/" + user + "_deployment.log"

for obj in os.listdir(directory):
    if os.path.isdir(directory + "/" + obj):
        path = directory + "/" + obj
        if os.path.isdir(path) and has_cert(path):
            pmsg.normal(f"\n=========== Examining Certs in {path}")
            helper.run_a_command("./scripts/check_cert.py " + path)
