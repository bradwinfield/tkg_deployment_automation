#!/usr/bin/env python3

# Validates OPA policies (image repo, ingress host name)
# Assumes the OPA and policies applied
# Assumes that the command 'kubectl' is available.
# Assumes we are logged-in to the cluster and the context is already set.
# validation yamls to test / apply located in template/opa

#import helper
import pmsg
#import re
import os
import interpolate
import subprocess

site_name = os.environ["site_name"]
validate_opa_ingress_policies_template = "templates/opa/validate-ingress-policies.yaml"
user = os.environ["USER"]

completed_validate_opa_ingress_policies = "/tmp/" + user + "_" + site_name + "-completed_validate_opa_policies.yaml"
interpolate.interpolate_from_environment_to_template(validate_opa_ingress_policies_template, completed_validate_opa_ingress_policies)

# create namespace test-opa-policies
subprocess.run(['kubectl', 'create', 'namespace', 'test-opa-policies'])
# kubectl apply templated ingress yaml
pmsg.normal("Error output in this step for failed to create invalid ingress are normal.")
pmsg.normal("Only valid ingresses should be created successfully.\n")
subprocess.run(['kubectl', '-n', 'test-opa-policies', 'apply', '-f', completed_validate_opa_ingress_policies])
# check that only valid ingresses are created
result_valid_ingress = subprocess.getoutput("kubectl -n test-opa-policies get ingress")

if 'invalid' not in result_valid_ingress:
    pmsg.green("Only valid ingresses created.")
else:
    pmsg.fail("Invalid ingresses applied, check policies and ingresses below:")
    pmsg.normal(result_valid_ingress)
    pmsg.fail("Invalid ingresses and namespace not deleted, manual cleanup required before running pipeline again.")
    pmsg.fail("To manually clean up: kubectl -n delete ns test-opa-policies")
    exit(1)

# kubectl run pods from different repos
pmsg.normal("Validate image repositorys.\n")
#pass tests - 'valid' in name - pull from allowed repositories and projects
subprocess.getoutput("kubectl -n test-opa-policies run valid-httpbin --image=docker.io/kennethreitz/httpbin")
subprocess.getoutput("kubectl -n test-opa-policies run valid-vmware-nginx-photon --image=vmware/nginx-photon")

#fail tests - 'invalid in name' - pull from root dockerhub (not allowed)
subprocess.getoutput("kubectl run invalid-nginx --image=nginx")

# check that only valid pods run
result_valid_image_repo = subprocess.getoutput("kubectl -n test-opa-policies get pods")

if 'invalid' not in result_valid_image_repo:
    pmsg.green("Only pods created for valid image repositories.\n")
else:
    pmsg.fail("Invalid pods created. Check policies and pods below:")
    pmsg.normal(result_valid_image_repo)
    pmsg.fail("Invaild pods not deleted, manual cleanup required before running pipeline again.")
    pmsg.fail("To manually clean up: kubectl -n delete ns test-opa-policies")
    exit(1)

# cleanup on success
pmsg.normal("Clean up test-opa-policies namespace.\n")
subprocess.run(['kubectl', 'delete', 'namespace', 'test-opa-policies'])


