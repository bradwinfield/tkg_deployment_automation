#!/usr/bin/env python3

# Dumps details about a cert and the private key.
# Arguments: <directory>

# The directory is expected to have files
# *.crt
# *.key

import sys
import os
import subprocess
import pmsg
import re

def file_readable(file):
    if os.path.isfile(file) and os.access(file, os.R_OK):
        return True
    return False

def get_file_modulus(file):
    if file_readable(file):
        return subprocess.getoutput(f'openssl x509 -noout -modulus -in {file}')
    return None


os.environ["deployment_log"] = "/tmp/" + os.environ["USER"] + "_deployment.log"

if len(sys.argv) < 2:
    pmsg.normal(f'Usage: {sys.argv[0]} <cert directory>')
    exit(1)

directory = sys.argv[1]
keypassword_file = directory + "/../../keypassword"

for file in os.listdir(directory):
    if re.search('.key.enc$', file) is not None:
        key_file_name = directory + "/" + file
    if re.search('.crt$', file) is not None:
        cert_file_name = directory + "/" + file

check_cert = True
if not file_readable(cert_file_name):
    pmsg.fail("Can't read cert file " + cert_file_name)
    check_cert = False

if not file_readable(key_file_name):
    pmsg.fail("Can't read key file " + key_file_name)
    check_cert = False

if check_cert:
    result = subprocess.getoutput(f'openssl x509 -in {cert_file_name} -noout -text | grep -E "Issuer:|Subject:|DNS:"')
    pmsg.normal(cert_file_name)
    pmsg.normal(result)

    # Get the md5 checksum and compare them...
    mod_crt = subprocess.getoutput(f'openssl x509 -noout -modulus -in {cert_file_name}')
    if len(mod_crt) < 1:
        pmsg.fail("Bad crt file.")
    mod_key_plus = subprocess.getoutput(f'openssl rsa -in {key_file_name} -passin file:{keypassword_file} | openssl rsa -noout -modulus | tail -1')
    mod_key = mod_key_plus.replace("writing RSA key\n", "")

    if mod_crt == mod_key:
        pmsg.green("Certificate and Private key OK.")
    else:
        pmsg.fail("Certificate and Private key do not match.")

    pmsg.normal(key_file_name)

else:
    pmsg.fail("Can't check certificate: " + cert_file_name)