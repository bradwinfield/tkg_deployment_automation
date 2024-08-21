#!/usr/bin/env python3

# Checks to see if contour.tanzu.vmware.com is installed and running.
# If not, installs it.
# Assumes the package is in the cluster already.
# Assumes that the commands 'tanzu' and 'kubectl' are available.
# Assumes we are logged-in to the cluster and the context is already set.

# Assumes there is a default storage class.

import helper
import pmsg
import os
import subprocess

package_namespace = os.environ["installed_packages_namespace"]
contour_template_file = "templates/contour-data-values.yaml"
#contour_config_file = /tmp/

# Get contour version
tanzu_lines = subprocess.getoutput("tanzu package available list contour.tanzu.vmware.com -A | grep  -v VERSION").splitlines()

contourVersion = helper.return_newest_version(tanzu_lines)

if contourVersion is not None:
    # install contour at version retrieved
    pmsg.green("Contour Version: " + contourVersion)
    subprocess.run(['tanzu', 'package', 'install', 'contour', helper.get_package_name_option(), 'contour.tanzu.vmware.com', '--namespace', package_namespace, '--version', contourVersion, "--values-file", contour_template_file])
else:
    pmsg.fail("Contour Package Version NOT FOUND or valid.")
    exit(1)

print("Checking for reconcile...")
if helper.check_for_result_for_a_time(["tanzu", "package", "installed", "list", "-A"], 'contour.*Reconcile succeeded', 10, 36):
    pmsg.green("The contour package is OK.")
else:
    pmsg.fail("Failed to install the contour package. Check the logs.")
    exit(1)

exit(0)
