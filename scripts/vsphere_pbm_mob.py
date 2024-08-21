#!/usr/bin/env python3

# Class that contains common routines for accessing vSphere Managed Objects.
# vCenter API imports
import ssl
try:
    from pyvim.connect import SmartConnect, Disconnect
except ImportError:
    from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

# CONSTANTS

class vsphere_pbm_mob():
    """
    Class containing vSphere MOB functions/methods
    """
    def __init__(self, set_verbose):
        self.verbose = set_verbose
        pass

    def login(self, server, username, password, certValidation):

        s = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        c = SmartConnect(host=server, user=username, pwd=password, sslContext=s, disableSslCertValidation=certValidation)

        return c

    def disconnect(self, c):
        Disconnect(c)

    def print_indented(self, msg, depth):
        if self.verbose:
            for i in range(depth):
                print (".", end="")
            print (str(msg))

    def find_object(self, obj, object_name, obj_type, depth):
        depth += 2
        self.print_indented ("Looking at: " + obj.name + " (" + str(type(obj)) + ")", depth)
        if type(obj) == obj_type:
            self.print_indented ("Found matching type: "+str(obj_type), depth)
            if obj.name == object_name:
                return obj
#        else:
#            self.print_indented ("Found non-matching type: "+str(obj_type), depth)
        if type(obj) == vim.Folder:
            for child in obj.childEntity:
                self.print_indented ("Recursing on " + child.name + "...", depth)
                result = self.find_object(child, object_name, obj_type, depth)
                if result is not None:
                    return result
        return None

    def find_cluster_element(self, content, cluster):
        # The cluster can be found by examining/walking from
        # content.rootFolder.childEntity(0-n).hostFolder.childEntity(0-m).name == cluster
        # returns the cluster entity which you can then call FetchUserPrivilegeOnEntities to confirm permissions
        for child in content.rootFolder.childEntity:
            for subchild in child.hostFolder.childEntity:
                if subchild.name == cluster and type(subchild) == vim.ClusterComputeResource:
                    return subchild
        return None

