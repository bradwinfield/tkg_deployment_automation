#!/usr/bin/env python3

# Logs into the supervisor cluster with the vSphere administrator ID.

# Depends on: set_kubeconfig.py
# Depends on: get_kube_api_vip.py

import helper
import os

os.environ["login_user"] = os.environ["vsphere_username"]
os.environ["login_password"] = os.environ["vsphere_password"]

exit(helper.run_a_command("./scripts/k8s_login.py"))
