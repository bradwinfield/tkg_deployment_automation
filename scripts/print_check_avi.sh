#!/usr/bin/env bash

# Prints message to check avi Default-Cloud.

cat << EOF

Check AVI Default-Cloud to make sure the vCenter Credentials are working.
Go to https://${avi_vm_ip1}/ 
Check the Default-Cloud vCenter credentials.
Are the Management Network (port groups) in the list?
If not, then reinitialize the Default-Cloud manually.
Then enter the vCenter credentials and try again.
When it works, you can proceed with the deployment.

EOF
