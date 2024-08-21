#!/usr/bin/env python3

# This script is not complete. It will pull the kubectl command from
# the workload management part of vCenter AFTER Workload Management is enabled in vCenter
# The current method of getting kubectl is to pull it from CustomerConnect.
# But it will be better pulled from vCenter after Workload Management is up which
# will guarantee version compatibility.

# This script will retrieve the kubectl command from vcenter post
# namespace creation

# Sample URL: https://10.214.152.66

# The button for download is: https://10.214.152.66/wcp/plugin/linux-amd64/vsphere-plugin.zip

kubectl_url = "https://"