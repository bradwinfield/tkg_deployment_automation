#!/usr/bin/env bash

cat << EOF
Perform the following steps manually in AVI before completing the automation.
1. Using your browser, goto https://$avi_vm_ip1/
2. Enter the AVI controller 'admin' password as the passphrases.
3. For DNS: enter $dns_servers
4. For Search Domain: $dns_search_domain
5. Click NEXT
6. Select 'None' for email config.
7. Click NEXT
8. Check the box at the bottom of the screen to 'Skip Cloud Config'.
9. Clict NEXT

10. Add the signed certificate (Templates -> Security -> SSL/TLS Certificates)
11. You will have to re-login as this point

12. Configure the Default-Cloud (Infrastructure -> Clouds)
    a. Select "VMware vCenter/vSphere ESX"
    b. Enter vCenter/vSphere credentials
    c. Save & Relaunch
    d. Select in Data Center: $vsphere_datacenter
    e. Select in Management Network: $supervisor_network_name
    f. Management Network: $avi_network_ip
    g. Defaut Gateway: $avi_default_gateway
    h. Create an IPAM profile: VIP
       i. Add by selecting the data/VIP Network.
    i. Click SAVE

13. Configure the user workload network (Infrastructure -> Cloud Resources -> Networks)
    a. IP range for the user workload network.

14. Configure the VRF static route 0.0.0.0/0 $data_network_gateway_ip (Infrastructure -> Cloud Resources -> VRF Context)

15. Change the license type to ENTERPRISE

16. Certificate:
  a. Put the certificate into $config_file
  b. Put the certificate (root+intermediate) and cert into AVI and make it the one for the console.

17. Complete a steps2.conf to prepare for the remainder of automation.

18. Run the automation: ./run_pipeline.py -c $config_file -s <steps file>

EOF