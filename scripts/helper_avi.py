#!/usr/bin/env python3

# General purpose AVI API functions

import re
import base64
import requests
from datetime import datetime
import http.cookiejar
import pmsg

# import pdb

class helper_avi():
    """
    Class used to provide general purpose AVI functions.
    """

# ########################################################
def __init__(self):
    pass

def make_header(api_endpoint, token, username, pw, avi_version):
    creds = username + ":" + pw
    base64_creds = base64.b64encode(bytes(creds, 'utf-8'))
    header = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept-Encoding": "application/json",
        "accept": "application/json,text/plain,*/*",
        "x-csrftoken": token,
        "x-avi-version": avi_version,
        "x-avi-useragent": "UI",
        "Referer": api_endpoint + "/",
        "Authorization": "Basic " + base64_creds.decode('ascii')
    }
    return header

# ########################################################
def get_token(response, token):
    cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
    if "csrftoken" in cookies_dict.keys():
        tok = cookies_dict["csrftoken"]
        if len(tok) > 1:
            token = tok
    return token

def make_cookie(name, value, domain, expires, secure):
    cookie = http.cookiejar.Cookie(
        version=0,
        name=name,
        value=value,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=False,
        secure=secure,
        expires=expires,
        path="/",
        path_specified=True,
        port=None,
        port_specified=False,
        discard=False,
        comment=None,
        comment_url=None,
        rest={'HttpOnly': None, 'SameSite': 'None'}
    )
    return cookie

def get_next_cookie_jar(response, last_cookie_jar, avi_vm_ip, token):
    if last_cookie_jar is None:
        cookie_jar = http.cookiejar.CookieJar()
        a_set_cookie = make_cookie(name="csrftoken", value=token, domain=avi_vm_ip, expires=None, secure=True)
        cookie_jar.set_cookie(a_set_cookie)
    else:
        cookie_jar = last_cookie_jar

    # And update the cookie jar with any 'Set-Cookie' values
    sch = response.headers.get('Set-Cookie')
    if sch is not None and len(sch) > 20:

        # First, substitute the commas with '#' that follow the day-of-week name (Sun, -> Sun#). Then, split on comma.
        set_cookie_header = re.sub('expires=(\w{3}),', 'expires=\\1#', sch)
        parts = re.split(',', set_cookie_header)
        for cookie in parts:
            cname = ""
            cvalue = ""
            cexpires = ""
            csecure = False

            cookie_parts = re.split(';', cookie)
            for cookie_part_value in cookie_parts:
                if "=" in cookie_part_value:
                    nm, value = re.split('=', cookie_part_value)
                else:
                    nm = cookie_part_value
                    value = None
                name = nm.strip().lower()
                if name == "max-age":
                    continue
                if re.search('csrftoken|sessionid', name):
                    cname = name
                    cvalue = value
                    continue
                if name == "secure":
                    csecure = True
                    continue
                if name == "expires":
                    cexpires = re.sub('#', ',', value)
                    if re.match('\w+, \d+', cexpires):
                        cexpires = str(datetime.strptime(cexpires, '%a, %d-%b-%Y %H:%M:%S %Z').timestamp()).split('.')[0]

            a_set_cookie = make_cookie(name=cname, value=cvalue, domain=avi_vm_ip, expires=cexpires, secure=csecure)
            cookie_jar.set_cookie(a_set_cookie)
    return cookie_jar

def login(api_endpoint, verify, avi_username, avi_password):
    path = "/login"
    data={'username': avi_username, 'password': avi_password}
    return requests.post(api_endpoint + path, verify=False, data=data)

def logout(api_endpoint, login_response, avi_vm_ip, avi_username, avi_password, token):
    path = "/logout"
    data={'username': avi_username, 'password': avi_password}
    logout_response = requests.post(api_endpoint + path, verify=False, headers={'X-CSRFToken': token, 'Referer': api_endpoint}, data=data, cookies=login_response.cookies)
#    if logout_response.status_code >= 300:
#        pmsg.warning("Can't logout of AVI. " + str(logout_response.status_code) + logout_response.text)
