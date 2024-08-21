#!/usr/bin/env python3

# Check for storage policy; create it if it is missing in vCenter.
# NOTE: Values are hard-coded in this script for the storage class.

import os
import pmsg
import argparse
import ssl
import service_instance
from pyVmomi import pbm, VmomiSupport

# Get server and credentials from the environment...
vsphere_server = os.environ["vsphere_server"]
vsphere_username = os.environ["vsphere_username"]
vsphere_password = os.environ["vsphere_password"]
vsphere_datacenter = os.environ["vsphere_datacenter"]
cluster_name = os.environ["cluster_name"]
storage_class = os.environ["storage_class"]

# retrieve SPBM API endpoint
def get_pbm_connection(vpxd_stub):
    from http import cookies
    import pyVmomi
    session_cookie = vpxd_stub.cookie.split('"')[1]
    http_context = VmomiSupport.GetHttpContext()
    cookie = cookies.SimpleCookie()
    cookie["vmware_soap_session"] = session_cookie
    http_context["cookies"] = cookie
    VmomiSupport.GetRequestContext()["vcSessionCookie"] = session_cookie
    hostname = vpxd_stub.host.split(":")[0]

    context = None
    if hasattr(ssl, "_create_unverified_context"):
        context = ssl._create_unverified_context()
    pbm_stub = pyVmomi.SoapStubAdapter(
        host=hostname,
        version="pbm.version.version1",
        path="/pbm/sdk",
        poolSize=0,
        sslContext=context)
    pbm_si = pbm.ServiceInstance("ServiceInstance", pbm_stub)
    pbm_content = pbm_si.RetrieveContent()

    return pbm_si, pbm_content


# Connect to SPBM Endpoint
args = argparse.Namespace()
args.host = vsphere_server
args.port = 443
args.user = vsphere_username
args.password = vsphere_password
args.disable_ssl_verification = True

si = service_instance.connect(args)
pbm_si, pbm_content = get_pbm_connection(si._stub)

pm = pbm_content.profileManager
profile_ids = pm.PbmQueryProfile(
    resourceType=pbm.profile.ResourceType(resourceType="STORAGE"),
    profileCategory="REQUIREMENT"
)

profiles = []
if len(profile_ids) > 0:
    profiles = pm.PbmRetrieveContent(profileIds=profile_ids)

for profile in profiles:
    if profile.name == storage_class:
        pmsg.green ("Storage profile in vSphere OK.")
        exit(0)

# If I get here, the storage profile does not exist.
pmsg.normal("Storage profile in vSphere not found.")

# Step 2 - see Notes
vSanCapable = False
resourceTypes = pm.FetchResourceType()
rt_found = None

# Loop to find the STORAGE resourceType
for rt in resourceTypes:
    if rt.resourceType == 'STORAGE':
        vendorInfo = pm.PbmFetchVendorInfo(rt)

        # Walk through list to find VSAN (or not)
        for vrti in vendorInfo:
            if vrti.resourceType == 'STORAGE':
                for vnsinfo in vrti.vendorNamespaceInfo:
                    if vnsinfo.namespaceInfo.namespace == 'VSAN':
                        vSanCapable = True
                        rt_found = rt

if vSanCapable:
    metadata = pm.PbmFetchCapabilityMetadata(rt_found)

    propertyInstancevar = pbm.capability.PropertyInstance()
    propertyInstancevar.id = 'stripeWidth'
    propertyInstancevar.value = 1

    constraintvar = pbm.capability.ConstraintInstance()
    constraintvar.propertyInstance = [propertyInstancevar]

    idvar = pbm.capability.CapabilityMetadata.UniqueId()
    idvar.id = 'stripeWidth'
    idvar.namespace = 'VSAN'

    capability = pbm.PbmCapabilityInstance()
    capability.id = idvar
    capability.constraint = [constraintvar]

    subprofilevar = pbm.profile.SubProfileCapabilityConstraints.SubProfile()
    subprofilevar.capability = [capability]

    constraintsvar = pbm.profile.SubProfileCapabilityConstraints()
    constraintsvar.subProfiles = [subprofilevar]

    spec = pbm.profile.CapabilityBasedProfileCreateSpec()
    spec.name = storage_class
    spec.description = 'Created via script "check_storage_policy.py".'
    spec.category = 'REQUIREMENT'
    spec.resourceType = rt_found
    spec.constraints = constraintsvar

    # Finally, create the Storage Profile in vSphere...
    profile_id = pm.PbmCreate(spec)
    if profile_id is not None:
        pmsg.green ("Storage profile in vSphere OK.")
        exit(0)
    else:
        pmsg.fail("Could not create the vSphere Storage Class: " + storage_class + ". Recommand creating by hand.")

else:
    pmsg.fail("VSAN storage policies not supported in this vSphere.")
    exit(1)

exit(1)
