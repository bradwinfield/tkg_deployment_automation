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

urllib3.disable_warnings()

avi_user = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_floating_ip = os.environ["avi_floating_ip"]
api_endpoint = "https://" + avi_floating_ip


###################################################
def try_to_connect(api_endpoint, path):
    try:
        response = requests.post(api_endpoint + path, verify=False, data={'username': avi_user, 'password': avi_password})
        if response.status_code == 200:
            return True
    except:
        return False
    return False

exit_code = 1
for i in range(0, 30):
    if try_to_connect(api_endpoint, "/login"):
        pmsg.green("AVI HA OK.")
        exit_code = 0
        break
    else:
        time.sleep(60)

if exit_code != 0:
    pmsg.fail("AVI HA controller is not responding.")

exit(exit_code)
