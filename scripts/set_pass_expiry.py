#!/usr/bin/env python3

# This script will create a namespace for pass-expiry and place a daemonset there that will
# set the vmware-system-user password to not expire.

import helper
import time
import pmsg
import sys

# Check the first argument. If it is 'cleanup', then the namespace pass-expiry-ns will be deleted upon completion.
delete_pass_expiry_ns = "leave namespace in place"
if len(sys.argv) > 1:
    delete_pass_expiry_ns=sys.argv[1]

ns = "pass-expiry-ns"
daemonsetfile = "templates/pass-expiry.yaml"
pspfile = "templates/pass-expiry-psp.yaml"

# Create a namespace pass-expiry-ns
helper.run_a_command('kubectl create ns ' + ns)

# Add a psp, a role and a role binding that is as restrictive as possible
helper.run_a_command('kubectl apply -f ' + pspfile + ' -n ' + ns)

# apply the daemonset yaml file
helper.run_a_command('kubectl apply -f ' + daemonsetfile + ' -n ' + ns)

# Wait a minute and then delete the namespace so it does not take up resources...
max_tries = 10
try_num = 0
while try_num < max_tries:
    try_num += 1
    # Check the daemonset to see if it is all running
    results = helper.run_a_command_get_stdout(['kubectl', 'get', 'ds', '-n', ns])
    desired = results[1].split()[1]
    current = results[1].split()[2]
    if desired == current:
        break
    time.sleep(5)

# Give the pods another 5 seconds to actually update the password expiration...
time.sleep(5)

if delete_pass_expiry_ns == 'cleanup':
    helper.run_a_command('kubectl delete ns ' + ns)

exit_code = 0
if desired == current:
    pmsg.green("Password expiration changed; OK.")
else:
    pmsg.fail("Password expiration not changed; not OK.")
    exit_code = 1

exit(exit_code)