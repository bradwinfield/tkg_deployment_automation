#!/usr/bin/env python3

# Installs and configures OPA from helm chart
# Assumes the package is in the cluster already.
# Assumes that the commands 'tanzu', 'kubectl', and helm are available.
# Assumes we are logged-in to the cluster and the context is already set.

#import helper
import pmsg
import os
import interpolate
import subprocess

site_name = os.environ["site_name"]
ingress_valid_domain_constraint_template = "templates/opa/constraint-templates/ingressvaliddomain.yaml"
user = os.environ["USER"]
completed_ingress_valid_domain_constraint_template = "/tmp/" + user + "_" + site_name + "-ingressvaliddomain.yaml"
interpolate.interpolate_from_environment_to_template(ingress_valid_domain_constraint_template, completed_ingress_valid_domain_constraint_template)

# add gatekeeper helm repo
subprocess.run(['helm', 'repo', 'add', 'gatekeeper', 'https://open-policy-agent.github.io/gatekeeper/charts'])

# helm repo update
subprocess.run(['helm', 'repo', 'update'])

# helm install gatekeeper
# check on the wait timer for sites like ANC1
pmsg.normal("Installing gatekeeper helm chart...")
pmsg.normal("Note: Wait timeout of 20 min to allow for slower sites (Anchorage) to pull images and start pods")
pmsg.normal("This step may take longer on sites with slower network links")
helm_install_gatekeeper = subprocess.getoutput("helm upgrade -i -n gatekeeper-system gatekeeper gatekeeper/gatekeeper --create-namespace --wait --timeout 20m")
pmsg.normal(helm_install_gatekeeper)

#check status of helm chart install
result_helm_install_gatekeeper = subprocess.getoutput("helm -n gatekeeper-system ls -o json | jq -r '.[].status'")

if result_helm_install_gatekeeper == "deployed":
  pmsg.green("Gatekeper helm chart status: " + result_helm_install_gatekeeper)
else:
  pmsg.fail("Gatekeeper helm chart failed to install. Check Logs.")
  pmsg.fail("Helm Chart Status: " + result_helm_install_gatekeeper)
  pmsg.fail("Check pod status: kubectl -n gatekeeper-system get pods")
  exit(1)

# apply opa constraint templates first
result_templates = subprocess.run(['kubectl', 'apply', '-f', 'templates/opa/constraint-templates/'], capture_output=True)

if result_templates.returncode == 0:
  pmsg.normal(result_templates.stdout.decode())
if result_templates.returncode !=0:
  pmsg.fail(result_templates.stderr.decode())
  exit(1)

# apply interpolated templates
result_interpolated = subprocess.run(['kubectl', 'apply', '-f', completed_ingress_valid_domain_constraint_template], capture_output=True)

if result_interpolated.returncode == 0:
  pmsg.normal(result_interpolated.stdout.decode())
if result_interpolated.returncode !=0:
  pmsg.fail(result_interpolated.stderr.decode())
  exit(1)

# apply opa constraints
result_constraints = subprocess.run(['kubectl', 'apply', '-f', 'templates/opa/constraints/'], capture_output=True)

if result_constraints.returncode == 0:
  pmsg.normal(result_constraints.stdout.decode())
if result_constraints.returncode !=0:
  pmsg.fail(result_constraints.stderr.decode())
  exit(1)

exit(0)
