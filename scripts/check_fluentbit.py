#!/usr/bin/env python3

# Checks to see if fluent-bit is installed and running.
# If not, installs it.
# Assumes the package is in the cluster already.
# Assumes that the commands 'tanzu' and 'kubectl' are available.
# Assumes we are logged-in to the cluster and the context is already set.

import helper
import pmsg
import os
import interpolate
import subprocess

package_namespace = os.environ["installed_packages_namespace"]
site_name = os.environ["site_name"]
values_file = "templates/fluent-bit-default-values.yaml"
user = os.environ["USER"]
completed_values_file = "/tmp/" + user + "_" + site_name + "-fluent-bit-default-values.yaml"
interpolate.interpolate_from_environment_to_template(values_file, completed_values_file)

# Get fluent-bit version
tanzu_lines = subprocess.getoutput("tanzu package available list fluent-bit.tanzu.vmware.com -A | grep  -v VERSION").splitlines()

fluentbitVersion = helper.return_newest_version(tanzu_lines)

if fluentbitVersion is not None:
    # install fluent-bit at version retrieved
    pmsg.green("fluent-bit Version: " + fluentbitVersion)
    # expected command to execute: tanzu package install fluent-bit --package-name fluent-bit.tanzu.vmware.com --values-file fluent-bit-default-values.yaml -n tanzu-packages --version 1.9.5+vmware.1-tkg.2
    subprocess.run(['tanzu', 'package', 'install', 'fluent-bit', helper.get_package_name_option(), 'fluent-bit.tanzu.vmware.com', "--values-file", completed_values_file, '--namespace', package_namespace, '--version', fluentbitVersion])
else:
    pmsg.fail("Fluent-bit Package Version NOT FOUND or valid.")
    exit(1)

print("Checking for reconcile...")
if helper.check_for_result_for_a_time(["tanzu", "package", "installed", "list", "-A"], 'fluent-bit.*Reconcile succeeded', 10, 36):
    pmsg.green("The fluent-bit package is OK.")
else:
    pmsg.fail("Failed to install the fluent-bit package. Check the logs.")
    exit(1)

exit(0)
