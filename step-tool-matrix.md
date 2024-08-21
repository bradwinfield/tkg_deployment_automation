# Tool / Step Matrix

This doc privides a detailed break-down of which steps in the TKG deployment automation are performed by which tools

The tools used in the automation if all the steps are run include the following:
1. python3 - with libraries: pyVmomi, pyVim, pyyaml, jinja2, paramiko and other standard libraries such as "system", etc.
2. bash
3. terraform
4. CLIs
4.1. kubectl
4.2 tanzu
4.3 govc - with prerequisites such as GoLang, govmomi
4.4 kapp
5. Powershell

# Notes about partial deployments
If you want to deplay just subsets of components, such as just enabling workload management or just creating a TKG workload cluster, you will only have to install/maintain a subset of the tools per the table below.

# Notes about TOOLS
If, in the TOOLS: reference lines below, you see "python3", assume that all the libraries required for all steps are included. This matrix does not attempt to show which python libraries are specifically used by each step.

## Deploy just AVI
TOOLS: python3, terraform

## Deploy just workload management
TOOLS: python3, terraform

## Deploy just a TKG workload cluster
TOOLS: python3, kubectl, tanzu, kapp, bash

# All Steps

## Add the user/role in the global permission table...
STEP: check_global_permissions.py  
TOOLS: python3

## Check/create users in vCenter before everything else...
STEP: check_users.py  
TOOLS: python3, govc

## This terraform directory contains code to create roles and privileges.
STEP: user_terraform  
TOOLS: terraform

## Add the user/role in the global permission table...
STEP: check_global_permissions.py  
TOOLS: python3

## Check for Content Library
STEP: check_content_library.py  
TOOLS: python3, govc, kubectl

## Check/create the AVI resource pool...
STEP: check_avi_resource_pool.py  
TOOLS: python3

## Create the 3 AVI controllers...
STEP: avi_controller_terraform  
TOOLS: terraform

## Set the AVI admin credentials
STEP: set_avi_admin_password.py  
STEP: avi_cloud_credentials.py  
TOOLS: python3

## Configure the AVI controllers...
STEP: avi_configure_mgmt_network.py  
STEP: avi_ipam_data_profile.py  
STEP: avi_cloud_finish.py  
STEP: avi_configure_data_network.py  
STEP: avi_configure_workload_network.py  
STEP: avi_configure_vrf.py  
TOOLS: python3

## Convert the AVI license to <LICENSELEVEL(ESSENTIALS|ENTERPRISE)>
Only do this if required base on what license was ordered.  
STEP: avi_license_change.py <LICENSELEVEL>
TOOLS: python3

## Enable AVI High Availability Mode
STEP: avi_ha.py  
TOOLS: python3

## Poll for AVI ready after configuration is complete.
STEP: wait_for_avi_ha.py  
TOOLS: python3

## Add AVI Certificate
STEP: avi_certificates.py  
STEP: avi_portal_configuration.py  
TOOLS: python3

## Create a storage policy in vSphere
STEP: check_storage_policy.py  
TOOLS: python3

## Enable Workload Management
STEP: wm_terraform  
TOOLS: terraform

## Login to the supervisor cluster
STEP: k8s_supervisor_login_admin.py  
TOOLS: python3

## Create the vSphere namespace
STEP: create_vsphere_namespace.py  
TOOLS: python3

## Add the Supervisor Cluster TLS Endpoint Certificate
STEP: wm_certificate.py  
TOOLS: python3

## Create workload cluster
STEP: tkcclustercreate.py  
TOOLS: python3, kubectl

## Complete workload cluster
NOTE: If you want to use the automation with a steps file that ONLY creates a TKG workload cluster,
      then you don't need terraform. The only tools that are needed from this point forward (for
      creating a TKG workload cluster are:  
TOOLS: bash, kubectll, tanzu, python3

### Increase the size of coredns to 256Mi
STEP: set_coredns_memory_limit.sh  
TOOLS: bash, kubectl

### Configure Tanzu Standard Packages
STEP: check_sc.py  
STEP: check_kapp.py  
STEP: tanzu_package.py  
STEP: cert-manager.py  
STEP: check_contour.py  
STEP: check_cluster_rb.py  
STEP: check_fluentbit.py  
TOOLS: python3, kubectl, tanzu, kapp

### Example of Customer tool installation
check_prisma.sh  
TOOLS: bash, kubectl

### Add Certificate for Contour Ingress
check_tls_secret.sh
TOOLS: bash, kubectl

### Create and publish storage policy on workload with desired Reclaimpolicy and bind mode
create-local-sc.py  
TOOLS: python3, kubectl

### Change the workload cluster VMs so the account vmware-system-user password does not expire
STEP: set_pass_expiry.py  
TOOLS: python3, kubectl

### Smoke test
STEP: test_ingress.py, kubectl  
TOOLS: python3

## Attach cluster to TMC
STEP: tmc_attach_cluster.py  
TOOLS: python3, kubectl

## Print final messages
STEP: print_final_messages.py  
TOOLS: python3

