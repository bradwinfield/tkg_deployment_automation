#!/usr/bin/env python3

# Reads the configuration file (Argument 1) and dumps out
# the CN/SANs so you can verify it is what you think.
# Also dumps out the private key details.

import sys
import yaml
import os
import subprocess
import pmsg

os.environ["deployment_log"] = "/tmp/" + os.environ["USER"] + "_deployment.log"
cert_file_name = "/tmp/leaf.crt"
key_file_name = "/tmp/private.key"

if len(sys.argv) < 2:
    pmsg.normal(f'Usage: {sys.argv[0]} <site config file name>')
    exit(1)

config_file = sys.argv[1]

with open(config_file, 'r') as cf:
    configs = yaml.safe_load(cf)

# what is the avi_certificate (leaf cert)?
cert_file = open(cert_file_name, "w")
cert_file.writelines(configs["avi_certificate"])
cert_file.close()

result = subprocess.getoutput(f'cat {cert_file_name} | openssl x509 -noout -text | grep -E "Issuer:|Subject:|DNS:"')
pmsg.normal("Certificate details =-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
pmsg.normal(result)

# what is the private key
key_file = open(key_file_name, "w")
key_file.writelines(configs["avi_private_key"])
key_file.close()

md5_crt = subprocess.getoutput(f'openssl x509 -noout -modulus -in {cert_file_name} | openssl md5')
md5_key = subprocess.getoutput(f'openssl rsa -noout -modulus -in {key_file_name} | openssl md5')

if md5_crt == md5_key:
    pmsg.green("Certificate and Private key OK.")
else:
    pmsg.fail("Certificate and Private key do not match.")

# Clean up
os.remove(cert_file_name)
os.remove(key_file_name)
