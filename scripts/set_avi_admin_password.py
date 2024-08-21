#!/usr/bin/env python3

# Hits the admin-user-setup page in an AVI vm to initialize the admin user.
# This script sets the admin password and is under test to
# set the passphrase.
import requests
import urllib3
import os
import json
import pmsg
import helper_avi
import re

urllib3.disable_warnings()

def do_exit(exit_code):
    if logged_in:
        helper_avi.logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token)
    exit(exit_code)


avi_version = os.environ["avi_version"]
avi_username = os.environ["avi_username"]
avi_password = os.environ["avi_password"]
avi_vm_ip1 = os.environ["avi_vm_ip1"]
avi_vm_ip2 = os.environ["avi_vm_ip2"]
avi_vm_ip3 = os.environ["avi_vm_ip3"]
avi_floating_ip = os.environ["avi_floating_ip"]
dns_servers = os.environ["dns_servers"]
dns_search_domain = os.environ["dns_search_domain"]
ntp_servers = os.environ["ntp_servers"]

avi_vm_ip = avi_vm_ip1
if "avi_vm_ip_override" in os.environ.keys():
    avi_vm_ip = os.environ["avi_vm_ip_override"]

default_avi_password = '58NFaGDJm(PJH0G'
api_endpoint = "https://" + avi_vm_ip

###################################################
# pmsg.normal("STEP 1 - GET token from " + api_endpoint + "#############################")
path = "/"
logged_in = False
login_response = requests.get(api_endpoint + path, verify=False)
if login_response.status_code > 299:
    pmsg.fail("Can't get the csrftoken on inital call to the AVI api. HTTP: " + str(login_response.status_code) + login_response.text)
    do_exit(1)
logged_in = True
token = helper_avi.get_token(login_response, "")
next_cookie_jar = helper_avi.get_next_cookie_jar(login_response, None, avi_vm_ip, token)
###################################################
# pmsg.normal("STEP 2 GET initial-data?include_name&treat_expired_session_as_unauthenticated=true ###############")
path = "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true"
response = requests.get(api_endpoint + path, verify=False, cookies=next_cookie_jar)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI api. HTTP: " + str(response.status_code) + response.text)
    do_exit(1)
token = helper_avi.get_token(response, token)
next_cookie_jar = helper_avi.get_next_cookie_jar(response, next_cookie_jar, avi_vm_ip, token)

###################################################
# pmsg.normal("STEP 3 POST login with default pw. #############################")
path = "/login?include_name=true"
data = {"username": avi_username, "password": default_avi_password}
response = requests.post(api_endpoint + path, json=data, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't login to AVI. HTTP: " + str(response.status_code) + response.text)
    pmsg.fail("Recommend manual set of AVI password.")
    pmsg.underline(api_endpoint + "/")
    logged_in = False
    do_exit(1)
token = helper_avi.get_token(response, token)
next_cookie_jar = helper_avi.get_next_cookie_jar(response, next_cookie_jar, avi_vm_ip, token)

###################################################
# 4. do a GET to get inital data and invalidate the session...
# pmsg.normal("STEP 4 get initial data and unauthenticate the session. #############################")
path = "/api/initial-data?include_name&treat_expired_session_as_unauthenticated=true"
# update the token in the header...
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code) + response.text)
    do_exit(1)
token = helper_avi.get_token(response, token)
next_cookie_jar = helper_avi.get_next_cookie_jar(response, next_cookie_jar, avi_vm_ip, token)
cookie = response.headers.get('Set-Cookie')

###################################################
# 5.
# pmsg.normal("STEP 5 Switch tenant. #############################")
path = "/api/switch-to-tenant?tenant_name=admin"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code) + response.text)
    do_exit(1)
token = helper_avi.get_token(response, token)
next_cookie_jar = helper_avi.get_next_cookie_jar(response, next_cookie_jar, avi_vm_ip, token)

###################################################
# 6. get default-values and parse out the backupconfiguration
# pmsg.normal("STEP 6 getting the backup configuration uuid")
path = "/api/default-values?include_name"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get config data from AVI. HTTP: " + str(response.status_code) + response.text)
    do_exit(1)
token = helper_avi.get_token(response, token)
next_cookie_jar = helper_avi.get_next_cookie_jar(response, next_cookie_jar, avi_vm_ip, token)
json_obj = json.loads(response.text)
backupid = json_obj["default"]["backupconfiguration"][0]
# pmsg.normal("Backup Configuration: " + backupid)

###################################################
# 7. GET controller-inventory
# pmsg.normal("STEP 7 GET controller-inventory.")
path = "/api/controller-inventory/?include=config,faults&include_name=true"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get controller inventory data from AVI. HTTP: " + str(response.status_code) + response.text)
    do_exit(1)

###################################################
# 8. do a PUT to change the default admin password...
# pmsg.normal("STEP 8 Change default admin password. ################################")
path = "/api/useraccount"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
data = {"username": "admin", "password": avi_password, "old_password": default_avi_password}
response = requests.put(api_endpoint + path, headers=headers, json=data, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the default admin password in AVI. Recommend manual operation. HTTP: " + str(response.status_code) + response.text)
    do_exit(1)
token = helper_avi.get_token(response, token)
next_cookie_jar = helper_avi.get_next_cookie_jar(response, next_cookie_jar, avi_vm_ip, token)

###################################################
# 9a. Get the system configuration:
# pmsg.normal("STEP 9a - Get the system configuration...")
path = "/api/systemconfiguration/?include_name=true&join=admin_auth_configuration.remote_auth_configurations.auth_profile_ref"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get system config data from AVI. HTTP: " + str(response.status_code) + " " + response.text)
    do_exit(1)
system_config_payload = json.loads(response.text)
array_of_dns_servers = []
for server in re.split(' |,|;', dns_servers.replace(" ", "")):
    one_dns_server = {"addr": server, "type": "DNS"}
    array_of_dns_servers.append(one_dns_server)
system_config_payload["dns_configuration"] = {"server_list": array_of_dns_servers, "search_domain": dns_search_domain}
system_config_payload["email_configuration"] = {"smtp_type": "SMTP_NONE"}
system_config_payload["ntp_configuration"]["ntp_server_list"] = []
array_of_ntp_servers = []
for server in re.split(' |,|;', ntp_servers.replace(" ", "")):
    one_ntp_server = {"server": {"addr": server, "type": "DNS"}}
    array_of_ntp_servers.append(one_ntp_server)
system_config_payload["ntp_configuration"]["ntp_servers"] = array_of_ntp_servers
system_config_payload["ntp_configuration"]["ntp_authentication_keys"] = []
system_config_payload["mgmt_ip_access_control"] = {}
system_config_payload["linux_configuration"] = {}

##################################################
# 9b. Get the backup configuration payload
# pmsg.normal("STEP 9b - Get the backup configuration payload...")
path = "/api/backupconfiguration/" + backupid + "?include_name=true"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
response = requests.get(api_endpoint + path, headers=headers, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't get system config data from AVI. HTTP: " + str(response.status_code) + " " + response.text)
    do_exit(1)
backup_payload = json.loads(response.text)
backup_payload["backup_passphrase"] = os.environ["vsphere_password"]

###################################################
# 9c. Create/Enter a passphrase...
# pmsg.normal("STEP 9c Create a passphrase")
path = "/api/macrostack"
headers = helper_avi.make_header(api_endpoint, token, avi_username, avi_password, avi_version)
payload = {
    "data": [
        {
            "data": backup_payload,
            "method": "PUT",
            "model_name": "backupconfiguration"
        },
        {
            "data": system_config_payload,
            "method": "PUT",
            "model_name": "systemconfiguration"
        }
    ]
}
data = json.dumps(payload)
headers["content-length"] = str(len(data))
response = requests.post(api_endpoint + path, headers=headers, data=data, cookies=next_cookie_jar, verify=False)
if response.status_code > 299:
    pmsg.fail("Can't change the Passphrase/DNS/Domain in AVI. Recommend manual operation. HTTP: " + str(response.status_code) + response.text)
    pmsg.fail("Recommend manual set of AVI passphrase.")
    pmsg.underline(api_endpoint + "/")
    do_exit(1)
pmsg.green("AVI admin password/passphrase OK.")

do_exit(0)
