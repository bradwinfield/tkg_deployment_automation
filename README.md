![bcom_header](/docs/img/bcom_header.png)
# vSphere with Tanzu
This repo contains version 1.0 of automation to deploy vSphere with Tanzu in an already deployed and configure vSphere environment.

## Release Information
```
Authors: Brad Winfield, Ben Stein, Nick Koehn, CJ Oster
Version: v1.0
Date: May 2024
```

## Description
This repo contains a general purpose script for running "steps" of automation. Specifically, the automation included here can be used to automate the deployment of TKG (vSphere with Tanzu) including the deployment of AVI (HA enabled), enablement of Workload Management which creates the Supervisor Cluster, Workload Clusters, Tanzu Standard Packages and other stuff. It ends with a 'Smoke test' to make sure all the stuff works.

## Project Status
This code is under current development / enhancement. It has been tested with vSphere 7 and 8. 
---

## TKG Deployment Automation Overview
This repository contains code to deploy TKG clusters to a vSphere 7 or 8 environment. At a high level, it will
1. Install and configure AVI including making it highly available (HA)
2. Enable Workload Management in vSphere
3. Create a vSphere Namespace
4. Create a workload cluster
5. Install kapp
6. Pull down the tanzu packages
7. Install cert-manager
8. Install Contour
9. Install Fluentbit
10. Create rolebindings
11. Create Storage Classes
12. Run a smoke test to validate that ingress is working

There are additional scripts that have been used in specific environments for specific reasons. The things that the pipeline does, depends on what "steps" are in the steps file passed to the ./run_pipeline.py command which will be described below.

The concept is to have a general-purpose pipeline running (written in Python) that will execute scripts or run terraform based upon the steps provided in a "steps file". Input is provided in a configuration file (YAML) and passwords can be prompted for or provided in a password file (YAML).

## Usage
Here is a brief outline of how the pipeline works
1. Execute ./run_pipeline.py -c "config file" -s "steps file" -p "password file"
2. Which puts all the "config file" values into the environment.
3. Then reads in the passwords and put those into the environment.
4. Then executes each script (and "# Depends on: 'script'") or terraform in the order found in the "steps file".
5. Run until the steps file says to "Abort" if an error is encountered, or "Exit", or the last step is finished.

Note that some utility scripts (steps) have been provided which print instructions and wait for manual intervention if needed before proceeding.

The code directory structure looks like this:
<pre>
root directory - Contains run_pipeline.py, config.yaml and steps.conf
  | - scripts subdirectory - Contains all scripts that actually check/deploy things (except terraform stuff)
  | - terraform subdirectory - Contains terraform .tf file(s).
  
</pre>
You can add as many terraform directories as you need. The run_pipeline.py will find them if they are referenced in the steps file.

You can add as many scripts as you need (in .../scripts). Again, the run_pipeline.py will find them if referenced in the steps file.

## Installation
### Prepare the environment
To prepare to run the automation:
1. Prepare a jumpbox (recommend Ubuntu Desktop). You will have to manually install 'git' to get started. I also like to manually install openssh-server so I can just ssh to the jumpbox.
2. Use 'git clone ...' to download the automation software. The clone URL will be provided upon request. Run "cd tkg-deployment-automation" to get into the automation directory. You can 'git clone ...' to any location but you need to be in that directory to run the pipeline.
3. Install all the required tools. You may run the script: ./scripts/prep_jumpbox.sh which will do this for you. Note that there are several places where the prep_jumpbox.sh script will prompt you to download files from vmware and other places. You may do this using the Web Console of the Jumpbox and it's web browser or other suitable tools. The downloaded files are expected to be in your user directory '~/Downloads' subdirectory. Every user that will run the automation will need to prepare their environment which can be safely done by running ./scripts/prep_jumpbox.sh.
4. Copy the config.yaml file to a site-specific config file (e.g. atl1-config.yaml) and fill in all the values for the specific site - This contains all the variables needed to build up a TKGs cluster starting from vSphere 7 or 8 at the given site.
5. Copy the steps.conf file to a site-specific steps file (e.g. atl1-steps.conf) if you anticipate changing the steps in any way. This file contains the list of steps (script names as found in the scripts subdirectory -OR- terrform subdirectory names) that will be run.
6. Copy the passwords.yaml file to create a site-specific file for the passwords used and created for the given site (e.g. atl1-access.yaml) - This file contains the passwords for vCenter, AVI and the service accounts that will be created (tkg-admin and avi-admin).

After these things are complete you are ready to run the automation.

### How to run the automatic deployment
The command that runs the deployment is:
./run_pipeline.py -c "config file" -s "step file" -p "password file"

## What if I want to run only some of the steps?

In the course of automatically deploying AVI, TKGs, etc., if you encounter an error, you can fix the error and then pickup the running of the automation by providing an abbreviated steps file. 

For example:
1. If you get through the AVI install but the enabling of workload management fails, you can provide a steps file that starts with "wm_terraform" which does the enabling of Workload Management.
2. If you have workload cluster and just want to install tanzu packages, you can provide a steps file that does just those steps.

You can run just the steps you want by modifying the steps file (or copy to another file that you can use), and including only the steps you want to run. NOTE that some steps require some environment variable be provided so that it runs correctly. For example, to run "check-fluentbit.py" it requires the Virtual IP Address of the Supervisor Cluster and it needs to be logged into the workload cluster. You will NOT need to include the pre-requisite scripts because the run_pipeline.py will automatically add those to the steps list at run time.  However, it doesn't hurt to explicitly include any pre-requisite scripts in the steps file. The steps file would look something like this:
<pre>
set_kubeconfig.py
get_kube_api_vip.py
k8s_cluster_login.py
check_fluentbit.py
</pre>

## How to add steps

Note that all config lines in the config.yaml are added to the environment (environment variables) so that your scripts don't need to read the config.yaml file or take in arguments. All scripts have access to all the config data in the environment. The same is true for terraform scripts noting that terraform can read environment variables that have "TF_VAR_" prepended to them. For example: if you want to use the "cluster_name" variable in terraform, you can use 'var.cluster_name'. You will notice that the environment will have "TF_VAR_cluster_name" in it when terraform is invoked by the 'run_pipeline.py' script.

In order to add steps to this TKGs deployment system

### add a new script
1. Create a new script in the 'scripts' subdirectory. Access the config.yaml data by using the environment variables by the same name. There is no need to read the config.yaml file as all the configuration values will already be in environment.
2. Scripts should exit(0) if they ran correctly and exit(>0) if not.
3. Scripts must be executable. You can make a file executable by running $ chmod 775 scripts/"scriptname".
4. Add the script name in the appropriate place in the steps file. Note that you can have a steps config file with just what you want to test as long as all the dependencies/prerequisites are already met in the target system.
5. If a script depends upon another script (some scripts add environment variables), you can either:
a. Put the prerequisite script in the steps file before the given script; or
b. Add a line(s) to the given script noting the dependency: e.g. # Depends on: <prerequisite script>

### add terraform
You can add terraform if that is best for adding capabilities to this deployment system by either:
1. Add lines to an existing terraform .tf file
2. OR create a new terraform subdirectory and create .tf files in that subdirectory. Then add this new terraform subdirectory name to a steps file to test/run it.

### Helpful things if you are writing in python

1. There is a module for printing messages with color. If you use this, it will make the output look consistent and pretty. Use 'import pmsg'.
2. There is a module of interpolating yaml into templates. Use 'import interpolate'.
3. There is a function for running a shell command (e.g. tazu package installed list -A) and looping to check for a final state that you are waiting for. Use 'import helper' and use helper.check_for_result_for_a_time().
4. If you want to add other helpful functions into a module, add them to 'helper.py' (in the scripts subdirectory).

## Technical Details and Features

### run_pipeline.py arguments
The arguments for ./run_pipeline.py are:
<pre>
usage: run_pipeline.py [-h] -c CONFIG_FILE -s STEPS_FILE [-p PASSWORD_FILE] [-d] [-v] [-n]

Pipeline main script to deploy a TKGs workload cluster.

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --config_file CONFIG_FILE
                        Name of yaml file which contains config params
  -s STEPS_FILE, --steps_file STEPS_FILE
                        Name of steps file; what scripts will run this time.
  -p PASSWORD_FILE, --password_file PASSWORD_FILE
                        Name of additional configs file (secrets).
</pre>

### How do I pass arguments to scripts?
You never have to pass arguments to scripts. However, you can add arguments to scripts in the steps file though that is not recommended. Each script is written (or should be if you are adding new scripts/steps) to read the variables it needs from the environment. For example, when a script wants to login to the vCenter server, it will use the credentials defined in the config file and are retrieved from the environment (if a Python script) vsphere_username = os.environ["vsphere_username"] or (if a bash script) ${vsphere_name}

Note that all of the variables defined in the config file are put into the environment when run_pipeline.py starts. Additionally, all the variables are put into the environment prepended with "TF_VAR_" so that terraform scripts can make use of config file values.

### Clean up before and after running automation
Clean-up of temporary files is done automatically when the run_pipeline.py script is about to exit. You can also include a clean-up or initialization script as the first step of the steps file if you wish. You will find the script clean_up_tfstate_files.sh in the sample steps.conf file that cleans up terraform files so there is no prior terraform state found.

### Temporary files
The automation sometimes creates temporary files. For example, if it is needed to interpolate the config values into a template file when the create a workload cluster script runs, it will place the temporary file into /tmp. The name of the temporary file will be /tmp/"username"_"site name"-"filename"
where:
- username is the name of the user running the pipeline.
- site name is the first part of the vsphere_server URL form the config file
- filename is defined by the script. 

Note that the step "cleanup_temp_files.sh" will remove all temporary files and is implicitly run when all the steps are complete.

### Extra Environment Variables
There are several variables that are placed into the environment to help scripts understand context or other things. They are:
<pre>
Name of the config file specified on the command line. ${config_file}
Name of the user if not already in the parent environment. ${USER}
Name of the site (first part of the vsphere_server URL). ${site_name}
Name of the first DNS server. ${dns_server}
Name of the first NTP server. ${ntp_server}
</pre>

### Step file constructs
A step file line can have only one of the following syntaxes:
1. Blank line - ignored
2. Comment line, lines beginning with a "#" - ignored but echoed to stdout when encountered.
3. Script name - if found in ./scripts, will be run. You can add arguments but all scripts, at this time, read variables out of the environment.
4. Terraform directory - if found in the current directory, will run the main.tf found in that directory.
5. Abort - if the previous line is a script or terraform and returns non-zero, will cause the pipeline to stop.
6. Exit - when encountered, will cause the pipeline to stop.

### Special Scripts
Note that there are some special scripts which can cause the pipeline to print instructions, pause or add values to the environment. By including:
1. print_final_messages.py will print some selective details about the new clusters like how to login, etc.
2. pause_steps.sh will print a message and then wait for user input of "y" before proceeding.
3. print_manual_steps.sh will print a list of manual steps that should/must be done. Follow this step up with a call to pause_steps.sh if you want the pipeline to pause.

#### print_certificate_manual_steps.sh (for example)
Note that you can create scripts that print messages to the screen. For example, the script "print_certificate_manual_steps.sh" will print instructions to stdout. In this case, this script is followed by "pause_steps.sh" so the user can perform manual steps as instructed.

#### pause_steps.sh
This script will print a message that the pipeline is pausing and will wait for someone to hit "y" followed by Enter/Return. At that time, the pipeline will continue processing.

#### env_for_library_id.py (for example)
Some scripts will add information to the environment. In some scripts, for example, the Content Library ID is needed to perform an action. There are several scripts that need the Content Library ID. So this script can add the ID to the environment so steps further down will have in the environment without having to do the work to look it up. Note that you can mark this script as "# Depends on: env_for_library_id.py" (as you will see in some other scripts/steps) so that it is automatically included when the pipeline runs.

### Dependencies / Prerequisites
There are some scripts which gather information like vCenter Content Library ID and adds that to the environment so subsequent scripts have access to that data without having to go get it before it does its work. For example, the script 'check_avi_resource_pool.py' requires a Content Libray ID and a Resource Pool ID. The config.yaml calls for the Content Library NAME only. So the ID must be retrieved from vCenter. 

You can satisfy the dependencies / prerequisites by doing either of the following:
1. Add the prerequisite script to the steps file before the given script; or
2. Add a special comment line to the given script which looks like this:

<pre># Depends on: scriptname</pre>

When the 'run_pipeline.py' script runs, it will read through the steps file once to find all dependencies and insert them just before the scripts that reference them.

## Support
The code is not supported beyond simply asking for help from it's authors. Contact Brad Winfield (brad.winfield@broadcom.com).

## Roadmap
No roadmap has been developed.

## Contributing
You may contribute to this repo by following the Project Alexander guidelines for maintaining and enhancing features.