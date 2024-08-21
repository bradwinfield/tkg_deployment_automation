#!/usr/bin/env python3

import base64
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from pyVmomi import vim
import pmsg
import pdb


def api_get(server, path, token):
    """ Gets content in json format from a URL
    :param server: vCenter server IP or FQDN
    :param path: URL path to GET
    :param token: The session token as returned by vcenter_api.vcenter_login()
    :returns: json object
    :rtype: dictionary
    """

    header = {"vmware-api-session-id": token}
    url = "https://"+server+path
    response = requests.get(url, headers=header, verify=False)
    if response.status_code > 299:
        #pmsg.fail ("Call to " + server + path + " Failed. Error occured in prepare-vsphere.pl: function: api_get ("+path+")")
        return None
    json_obj = json.loads(response.content.decode())
    return json_obj

def api_delete(server, path, token):
    """ Calls the DELETE action to server/path
    :param server: vCenter server IP or FQDN
    :param path: URL path to DELETE
    :param token: The session token as returned by vcenter_api.vcenter_login()
    :returns: Boolean
    :rtype: bool
    """
    header = {"vmware-api-session-id": token}
    url = "https://"+server+path
    response = requests.delete(url, headers=header, verify=False)
    if response.status_code > 299:
        pmsg.fail ("Call to " + server + path + " Failed. Error occured in prepare-vsphere.pl: function api_delete.")
        exit (2)
    return True

def api_patch(server, path, token, data, success_code):
    """ Calls the PATCH action to server/path with given data 
    :param server: vCenter server IP or FQDN
    :param path: URL path to PATCH
    :param token: The session token as returned by vcenter_api.vcenter_login()
    :param data: json formatted data to PATCH
    :param success_code: HTTP return_code to expect. Anything else is treated as an error.
    :returns: Boolean
    :rtype: bool
    """
    # Returns True or False
    header = {"vmware-api-session-id": token, "Content-Type": "application/json"}
    url = "https://"+server+path
    response = requests.patch(url, headers=header, verify=False, json=data)

    # Some posts don't return content
    try:
        json.loads(response.content.decode())
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    if response.status_code == success_code:
        return True
    pmsg.warning ("Response: " + "api_post with data: " + str(data) + " returned status code: " + str(response.status_code))
    return False

def api_post(server, path, token, data, success_code):
    """ Calls the POST action to server/path with given data 
    :param server: vCenter server IP or FQDN
    :param path: URL path to POST
    :param token: The session token as returned by vcenter_api.vcenter_login()
    :param data: json formatted data to POST
    :param success_code: HTTP return_code to expect. Anything else is treated as an error.
    :returns: Boolean
    :rtype: bool
    """
    # Returns True or False
    header = {"vmware-api-session-id": token, "Content-Type": "application/json"}
    url = "https://"+server+path
    response = requests.post(url, headers=header, verify=False, json=data)

    # Some posts don't return content
    try:
        json.loads(response.content.decode())
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    if response.status_code == success_code:
        return True
    pmsg.warning ("Response: " + "api_post with data: " + str(data) + " returned status code: " + str(response.status_code))
    return False

def api_post_returns_content(server, path, token, data, success_code):
    """ Calls the POST action to server/path with given data and returns content
    :param server: vCenter server IP or FQDN
    :param path: URL path to POST
    :param token: The session token as returned by vcenter_api.vcenter_login()
    :param data: json formatted data to POST
    :param success_code: HTTP return_code to expect. Anything else is treated as an error.
    :returns: string
    :rtype: string
    """
    # Returns response.content
    header = {"vmware-api-session-id": token, "Content-Type": "application/json"}
    url = "https://"+server+path
    response = requests.post(url, headers=header, verify=False, json=data)

    # Some posts don't return content
    try:
        json.loads(response.content.decode())
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    if response.status_code == success_code:
        return response.content
    pmsg.warning ("Response: " + "api_post with data: " + str(data) + " returned status code: " + str(response.status_code))
    return None


def vcenter_login(server, username, pw):
    """ Logs into the vCenter server
    :param server: vCenter server IP or FQDN
    :param username: User name
    :param pw: Password
    :returns: Session token
    :rtype: string
    """
    args = {'host': server, 'port': 443, 'user': username, 'password': pw, 'disable_ssl_verification': True}
    url = "https://" + server + "/rest/com/vmware/cis/session"
    creds = username + ":" + pw
    base64_creds = base64.b64encode(bytes(creds,'utf-8'))
    header = {"authorization": "Basic "+base64_creds.decode('ascii')}
    response = requests.post(url, headers=header, verify=False)
    if response.status_code == 200:
        jcontent = json.loads(response.content.decode())
        return jcontent["value"]
    return ''
