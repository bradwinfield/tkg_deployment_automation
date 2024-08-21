#!/usr/bin/env python3

import helper
import interpolate
import pmsg
import os
import stat
import time

site_name = os.environ["site_name"]
yaml_source = os.environ["config_file"]
template_file = "templates/workload-cluster-template.yaml"
user = os.environ["USER"]
output_file = "/tmp/" + user + "_" + site_name + "-tkc_result"
workload_cluster = os.environ["workload_cluster"]
vsphere_namespace = os.environ["vsphere_namespace"]

def create_cluster(cmd):
    # Tries to create a workload cluster.
    # returns 0 on success
    # returns 1 on failure
    # returns 2 when you can try again.

    if helper.check_for_result(cmd, "tanzukubernetescluster.* created"):
        if helper.check_for_result_for_a_time(["kubectl", "get", "tkc", workload_cluster, "-n", vsphere_namespace, "-o", "jsonpath='{.status.phase}'"], "running", 60, 50):
            pmsg.green("Workload cluster is RUNNING")
            return 0
        else:
            pmsg.fail("Failed to create cluster in time, check logs for more details")
            return 1
    return 2


# does this workload cluster already exist?
if helper.run_a_command("kubectl get tkc " + workload_cluster + " -n " + vsphere_namespace) == 0:
    pmsg.green("Workload cluster is RUNNING")
    exit(0)

# Try to create the workload cluster. I'm going to try several times if the yaml is not accepted.
interpolate.interpolate_from_yaml_to_template(yaml_source, template_file, output_file)
os.chmod(output_file, stat.S_IRWXG | stat.S_IRWXU | stat.S_IRWXO)

cmd = ['kubectl', 'apply', '-f', output_file]
pmsg.normal("Creating workload cluster...")
for i in range(1, 10):
    rc = create_cluster(cmd)
    if rc == 0:
        exit(0)
    if rc == 1:
        exit(1)
    else:
        time.sleep(30)
        pmsg.normal("Supervisor Cluster not quite ready. Wait a minute and try creating the workload cluster again...")
