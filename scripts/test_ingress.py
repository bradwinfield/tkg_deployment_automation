#!/usr/bin/env python3

# Smoke-Test ingress

import helper
import pmsg
import re
import requests
import time

rc = 1

helper.run_a_command("kubectl create ns test-ingress")
helper.run_a_command("kubectl create rolebinding auth-users-priv --clusterrole=psp:vmware-system-privileged --group=system:authenticated -n test-ingress")
helper.run_a_command("kubectl apply -f https://projectcontour.io/examples/httpbin.yaml -n test-ingress")
time.sleep(30)

cmd = ["kubectl", "get", "ingress", "-n", "test-ingress"]
expression = "httpbin.*\\s(\\d{1,3}.){4}"

# Get the ingress IP address; may take a minute or two to get an IP allocated.
if helper.check_for_result_for_a_time(cmd, expression, 5, 20):
    lines = helper.run_a_command_get_stdout(cmd)
    for line in lines:
        if re.match(expression, line) is not None:
            ip_address = re.split('\\s+', line)[3]
            url = "http://" + ip_address + "/"
            # Put ip_address in the environment so subsequent steps can reference it...
            helper.add_env_override(True, "ingress_ip_address", ip_address)

            if helper.check_for_result_for_a_time(["kubectl", "get", "replicaset", "-n", "test-ingress"], "httpbin.*3.*3.*3", 4, 10):
                time.sleep(50)
                pmsg.blue("Trying to access test app using ingress at URL: " + url)
                max_tries = 10
                ntries = 0
                while ntries < max_tries:
                    response = requests.get(url, headers={"Host": "httpbin"})
                    ntries += 1
                    if response.status_code >= 200 and response.status_code < 300:
                        pmsg.green("Smoke test of the ingress controller OK.")
                        rc = 0
                        break
                    time.sleep(20)
                if rc > 0:
                    pmsg.fail("Smoke test of the ingress controller failed (http error: " + str(response.status_code) + "). Recommend checking ingress by hand.")
                    pmsg.normal("Test manually with: curl -H \"Host: httpbin\" http://$(k get ingress -n test-ingress|grep -v ADDRESS|awk '{print $4}')/")
                break
            else:
                pmsg.fail("Smoke test of the ingress controller failed because pods did not become ready. Recommend checking ingress by hand.")
else:
    pmsg.fail("Failed to get an IP address allocated for the ingress. Recommend manually checking ingress.")

# Clean up the test namespace/app...
if rc == 0:
    helper.run_a_command("kubectl delete ns test-ingress")
else:
    pmsg.notice("Since the smoke test failed, I'm leaving the test app in place so you can diagnose the problem. See the app in namespace: test-ingress.")

exit(rc)
