#!/usr/bin/env python3

# Add a license to vSphere

import vsphere_mob
import os
import pmsg

vsphere_license = os.environ["vsphere_license"]
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]

if len(vsphere_license) < 2:
    pmsg.fail("vSphere license not valid... too short.")
    exit(1)

mob = vsphere_mob.vsphere_mob(False)
c = mob.login(vsphere_server, vsphere_username, vsphere_password, True)
content = c.content
if content is None:
    pmsg.fail("Could not login to the MOB SOAP API. Check your user credentials in the config.yaml and try again. Exiting.")
    exit (2)

lm = content.licenseManager
result = lm.AddLicense(vsphere_license)
if result.licenseKey == vsphere_license:
    pmsg.green("License OK.")
else:
    pmsg.fail("License can't be added to vSphere.")
