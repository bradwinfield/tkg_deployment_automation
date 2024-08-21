#!/usr/bin/env python3

# Checks to see if cert-manager is installed and running.
# If not, installs it.
# Assumes the package is in the cluster already.
# Assumes that the commands 'tanzu' and 'kubectl' are available.
# Assumes we are logged-in to the cluster and the context is already set.

# Assumes there is a default storage class.

import helper
import pmsg
import os
import re
import subprocess

package_namespace = os.environ["installed_packages_namespace"]
subprocess.run(['kubectl', 'create', 'ns', package_namespace])
tanzu_lines = subprocess.getoutput("tanzu package available list cert-manager.tanzu.vmware.com -A | grep  -v VERSION").splitlines()

# Determine the most recent version
certManagerVersion = helper.return_newest_version(tanzu_lines)

if certManagerVersion is not None:
    # install cert manager at version retrieved
    pmsg.green("Cert Manager Version: " + certManagerVersion)
    subprocess.run(['tanzu', 'package', 'install', 'cert-manager', helper.get_package_name_option(), 'cert-manager.tanzu.vmware.com', '--namespace', package_namespace, '--version', certManagerVersion])
else:
    pmsg.fail("Cert Manager Package Version NOT FOUND or invalid.")
    exit(1)

print("Checking for reconcile...")
if helper.check_for_result_for_a_time(["tanzu", "package", "installed", "list", "-A"], 'cert-manager.*Reconcile succeeded', 10, 36):
    pmsg.green("The cert-manager package is OK.")
else:
    pmsg.fail("Failed to install the cert-manager package. Check the logs.")
    exit(1)

exit(0)
