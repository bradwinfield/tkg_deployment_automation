#!/usr/bin/env python3

# This script will print out final messages for the Platform Admin.

import os
import pmsg

vsphere_server = os.environ["vsphere_server"]
vsphere_namespace = os.environ["vsphere_namespace"]
supervisor_cluster = os.environ["supervisor_cluster"]
supervisor_network_starting_ip = os.environ["supervisor_network_starting_ip"]
workload_cluster = os.environ["workload_cluster"]
dns_search_domain = os.environ["dns_search_domain"]
ingress_ip_address = os.environ["ingress_ip_address"]

pmsg.notice("If there were no errors during the deployment...")
pmsg.blue("The deployment of Supervisor Cluster: " + supervisor_cluster + " (" + supervisor_network_starting_ip + ") is complete.")
pmsg.notice("Please make sure that DNS is updated to show " + supervisor_cluster + " resolves to " + supervisor_network_starting_ip + ".")
pmsg.notice("Please make sure that DNS is updated with a wildcard entry for ingress: *.<subdomain name you want for your ingress>." + dns_search_domain + " resolves to " + ingress_ip_address)
pmsg.normal("vSphere cluster: " + vsphere_server + " is now running the workload cluster: " + workload_cluster + ".")
pmsg.normal("You can log in to the clusters as shown here:")
pmsg.normal("  Supervisor Cluster Login:")
pmsg.blue("kubectl vsphere login --server " + supervisor_cluster + " --vsphere-username <yourloginID> --insecure-skip-tls-verify")
pmsg.normal("  Workload Cluster Login:")
pmsg.blue("kubectl vsphere login --server " + supervisor_cluster + " --vsphere-username <yourloginID> --insecure-skip-tls-verify --tanzu-kubernetes-cluster-namespace " + vsphere_namespace + " --tanzu-kubernetes-cluster-name " + workload_cluster)
