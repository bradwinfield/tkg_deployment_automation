#!/usr/bin/env bash

cat << EOF

AVI needs a valid certificate to function over HTTP. 
vSphere needs to know about the certificate if it is not a public certificate.
In any case, the AVI cert should have in the SANS field, the VIP FQDN and the FQDNs of the AVI controllers if they are installed in HA mode.

There are 2 options for getting AVI certificates right so this pipeline can finish.

OPTION 1:
You may have previously obtained a public cert for AVI and put the root and leaf 
cert into the config.yaml file so the pipeline can install the certs.
If that is the case, you can simply proceed forward with this pipeline automation.

OPTION 2:
You can use a private AVI certificate signed by the AVI CA. 
You can now use the AVI UI to create a new leaf cert and then 
put that certificate (and root) in files that this pipeline 
can access without having to be restarted.
Then you can proceed to run the rest of the pipeline.
To create a new private certificate in AVI, do the following:
1. Access AVI at https://${avi_floating_ip}.
2. Enter a passphrase (twice) for backup server (I use the password for the passphrase) and login.
3. Go to Templates -> Security -> SSL/TLS Certificates
4. Select 'Create' and choose 'Controller Certificate'
5. Create a self-signed certificate
... name = "${avi_controller_cert_name}"
... Enter the SANS for each of the AVI controllers AND the AVI FQDN which points to the AVI floating IP.
... Save the new certificate
6. Copy the contents AVI root certificate and the leaf certificate and put them in:
- Root Cert goes into: /tmp/${USER}_${site_name}/avi_root_certificate
- UI Cert goes into: /tmp/${USER}_${site_name}/avi_certificate
7. Then you may proceed with the pipeline by type 'y' <enter>.

EOF
