terraform {
  required_providers {
    avi = {
      # version = ">= 21.1"
      source  = "vmware/avi"
    }
    vsphere = {
      version = ">= 2.1.1"
      source = "hashicorp/vsphere"
    }
  }
}

provider "vsphere" {
  user           = var.vsphere_username
  password       = var.vsphere_password
  vsphere_server = var.vsphere_server
  allow_unverified_ssl = true
}

data "vsphere_datacenter" "dc" {
  name = var.vsphere_datacenter
}

data "vsphere_datastore" "datastore" {
  name          = var.datastore
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_network" "network" {
  name          = var.avi_network
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_content_library" "library" {
  name = var.avi_content_library
}

data "vsphere_content_library_item" "item" {
  name       = var.avi_ova_name
  library_id = data.vsphere_content_library.library.id
  type = "" // Is actually a Read item, not a set one
}

resource "vsphere_virtual_machine" "vm1" {
  // For settings with vSphere networking:-
  // See: https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-CBA041AB-DC1D-4EEC-8047-184F2CF2FE0F.html

  // Is name the same as hostname? (doubtful - VM name in vCenter)
  name             = var.avi_vm_name1
  resource_pool_id = var.avi_resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  count = 1
  num_cpus = 4
  memory = 24576
  // folder = var.vm_folder
  // Management network (only interface in OVA)
  // TODO determine if OVA setting is automatically linked to this
  network_interface {
    network_id   = data.vsphere_network.network.id
  }
  lifecycle {
    ignore_changes = [guest_id]
  }
  disk {
    label = "disk1"
    size = 130
    // Thin unless you have a very good reason not to
    thin_provisioned = true
  }
  clone {
    template_uuid = data.vsphere_content_library_item.item.id
  }
  vapp {
    properties = {
      // Missing from Avi examples, but in the OVA:-
      // BKW: can do using the AVI api.
      // TODO how to do NTP, DNS, search domain???
      # dns_server_list = [var.avi_management_dns_server]
      # dns_suffix_list = [var.avi_management_dns_suffix]
      # linux_options {
      #   host_name = var.avi_management_hostname
      #   domain    = var.avi_management_domain
      # }

      // Hostname for the controller vm
      // OVA Docs: Hostname of Avi controller (For modification by NSX Manager only. This field should not be filled in or modified by the user directly)
      hostname = var.avi_vm_name1
      // OVA Docs: IP address for the Management Interface. Leave blank if using DHCP. Example: 192.168.10.4
      // Tanzu Docs: Enter the IP address for the [this] Controller VM, such as 10.999.17.51.
      // REQUIRED field if DHCP is not being used (which normally it isn't for a controller)
      mgmt-ip = var.avi_vm_ip1
      // OVA Docs: Subnet mask for the Management Interface. Leave blank if using DHCP. Example : 24 or 255.255.255.0
      // Tanzu Docs: Enter the subnet mask, such as 255.255.255.0.
      // REQUIRED if management ip specified (Static IP)
      mgmt-mask = var.avi_subnet_mask
      // OVA Docs: Optional default gateway for the Management Network. Leave blank if using DHCP.
      // Tanzu Docs: Enter the default gateway for the Management Network, such as 10.199.17.235.
      // REQUIRED if management ip specified (Static IP)
      default-gw = var.avi_default_gateway

      // Optional: Don't specify for now. sysadmin-public-key = var.avi_management_ssh_key
    } // properties
  } // vapp
  wait_for_guest_ip_timeout = 30
}
provider "avi" {
  avi_username   = var.avi_username
  avi_password   = var.avi_password
  # avi_controller = vsphere_virtual_machine.vm[0].default_ip_address
  avi_tenant     = "admin"

  # For after creation by vsphere
  avi_controller = var.avi_vm_ip1

  # Required for Terraform provider not to puke
  # Without this it complains about 'common_criteria' being there (even though false by default) as the terraform provider defaults to v18.8
  avi_version = var.avi_version
}

data "avi_systemconfiguration" "ensure_server1_responding" {
  depends_on = [vsphere_virtual_machine.vm1]
}

resource "vsphere_virtual_machine" "vm2" {
  // For settings with vSphere networking:-
  // See: https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-CBA041AB-DC1D-4EEC-8047-184F2CF2FE0F.html

  // Is name the same as hostname? (doubtful - VM name in vCenter)
  name             = var.avi_vm_name2
  resource_pool_id = var.avi_resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  count = 1
  num_cpus = 4
  memory = 24576
  // folder = var.vm_folder
  // Management network (only interface in OVA)
  // TODO determine if OVA setting is automatically linked to this
  network_interface {
    network_id   = data.vsphere_network.network.id
  }
  lifecycle {
    ignore_changes = [guest_id]
  }
  disk {
    label = "disk1"
    size = 130
    // Thin unless you have a very good reason not to
    thin_provisioned = true
  }
  clone {
    template_uuid = data.vsphere_content_library_item.item.id
  }
  vapp {
    properties = {
      // Missing from Avi examples, but in the OVA:-
      // BKW: can do using the AVI api.
      // TODO how to do NTP, DNS, search domain???
      # dns_server_list = [var.avi_management_dns_server]
      # dns_suffix_list = [var.avi_management_dns_suffix]
      # linux_options {
      #   host_name = var.avi_management_hostname
      #   domain    = var.avi_management_domain
      # }

      // Hostname for the controller vm
      // OVA Docs: Hostname of Avi controller (For modification by NSX Manager only. This field should not be filled in or modified by the user directly)
      hostname = var.avi_vm_name2
      // OVA Docs: IP address for the Management Interface. Leave blank if using DHCP. Example: 192.168.10.4
      // Tanzu Docs: Enter the IP address for the [this] Controller VM, such as 10.999.17.51.
      // REQUIRED field if DHCP is not being used (which normally it isn't for a controller)
      mgmt-ip = var.avi_vm_ip2
      // OVA Docs: Subnet mask for the Management Interface. Leave blank if using DHCP. Example : 24 or 255.255.255.0
      // Tanzu Docs: Enter the subnet mask, such as 255.255.255.0.
      // REQUIRED if management ip specified (Static IP)
      mgmt-mask = var.avi_subnet_mask
      // OVA Docs: Optional default gateway for the Management Network. Leave blank if using DHCP.
      // Tanzu Docs: Enter the default gateway for the Management Network, such as 10.199.17.235.
      // REQUIRED if management ip specified (Static IP)
      default-gw = var.avi_default_gateway

      // Optional: Don't specify for now. sysadmin-public-key = var.avi_management_ssh_key
    } // properties
  } // vapp
  wait_for_guest_ip_timeout = 30
}
data "avi_systemconfiguration" "ensure_server2_responding" {
  depends_on = [vsphere_virtual_machine.vm2]
}
resource "vsphere_virtual_machine" "vm3" {
  // For settings with vSphere networking:-
  // See: https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-CBA041AB-DC1D-4EEC-8047-184F2CF2FE0F.html

  // Is name the same as hostname? (doubtful - VM name in vCenter)
  name             = var.avi_vm_name3
  resource_pool_id = var.avi_resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  count = 1
  num_cpus = 4
  memory = 24576
  // folder = var.vm_folder
  // Management network (only interface in OVA)
  // TODO determine if OVA setting is automatically linked to this
  network_interface {
    network_id   = data.vsphere_network.network.id
  }
  lifecycle {
    ignore_changes = [guest_id]
  }
  disk {
    label = "disk1"
    size = 130
    // Thin unless you have a very good reason not to
    thin_provisioned = true
  }
  clone {
    template_uuid = data.vsphere_content_library_item.item.id
  }
  vapp {
    properties = {
      // Missing from Avi examples, but in the OVA:-
      // BKW: can do using the AVI api.
      // TODO how to do NTP, DNS, search domain???
      # dns_server_list = [var.avi_management_dns_server]
      # dns_suffix_list = [var.avi_management_dns_suffix]
      # linux_options {
      #   host_name = var.avi_management_hostname
      #   domain    = var.avi_management_domain
      # }

      // Hostname for the controller vm
      // OVA Docs: Hostname of Avi controller (For modification by NSX Manager only. This field should not be filled in or modified by the user directly)
      hostname = var.avi_vm_name3
      // OVA Docs: IP address for the Management Interface. Leave blank if using DHCP. Example: 192.168.10.4
      // Tanzu Docs: Enter the IP address for the [this] Controller VM, such as 10.999.17.51.
      // REQUIRED field if DHCP is not being used (which normally it isn't for a controller)
      mgmt-ip = var.avi_vm_ip3
      // OVA Docs: Subnet mask for the Management Interface. Leave blank if using DHCP. Example : 24 or 255.255.255.0
      // Tanzu Docs: Enter the subnet mask, such as 255.255.255.0.
      // REQUIRED if management ip specified (Static IP)
      mgmt-mask = var.avi_subnet_mask
      // OVA Docs: Optional default gateway for the Management Network. Leave blank if using DHCP.
      // Tanzu Docs: Enter the default gateway for the Management Network, such as 10.199.17.235.
      // REQUIRED if management ip specified (Static IP)
      default-gw = var.avi_default_gateway

      // Optional: Don't specify for now. sysadmin-public-key = var.avi_management_ssh_key
    } // properties
  } // vapp
  wait_for_guest_ip_timeout = 30
}
data "avi_systemconfiguration" "ensure_server3_responding" {
  depends_on = [vsphere_virtual_machine.vm3]
}

# This did not work. 
#resource "avi_useraccount" "avi_user" {
#  username     = var.avi_username
#  name     = var.avi_username
#  # id     = var.avi_username
#  # Stupidly, the provider relies on old and new password differing, and not being empty
#  old_password = "58NFaGDJm(PJH0G"
#  # Even more stupidly, since v17.2.2 the default admin password is a hardcoded value available from the customer portal. This is NOT DOCUMENTED in ANY of the terraform examples from Avi
#  password     = var.avi_password
#
#  depends_on = [data.avi_systemconfiguration.ensure_server1_responding]
#}

output "initial_configuration" {
  value = data.avi_systemconfiguration.ensure_server1_responding
}

output "admin_user" {
  value = var.avi_username
}
