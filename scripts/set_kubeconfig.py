#!/usr/bin/env python3

# Sets an environment variable so that we don't clash with this users $HOME/.kube config file(s).

import helper
import os

workload_cluster = os.environ["workload_cluster"]
user = os.environ["USER"]
kubeconfig_dir = "/tmp/" + user + "_" + workload_cluster+"_kubeconfig"
kubeconfig = kubeconfig_dir + "/config"

helper.add_env_override(True, "KUBECONFIG", kubeconfig)

# Make sure the directory exists...
if not os.path.exists(kubeconfig_dir):
    os.makedirs(kubeconfig_dir)
