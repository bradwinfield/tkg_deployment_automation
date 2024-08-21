terraform {
  required_providers {
    // Force local binary use, rather than public binary
    namespace-management = {
      version = "0.1"
      source  = "vmware.com/vcenter/namespace-management"
    }
    vsphere = {
      version = ">= 2.1.1"
      source = "hashicorp/vsphere"
    }
  }
}
provider "namespace-management" {
  vsphere_hostname = var.vsphere_server
  vsphere_username = var.vsphere_username
  vsphere_password = var.vsphere_password
  #vsphere_username = var.tkg_user
  #vsphere_password = var.tkg_user_password
  vsphere_insecure = true
}
provider "vsphere" {
  vsphere_server = var.vsphere_server
  user           = var.vsphere_username
  password       = var.vsphere_password
  #user           = var.tkg_user
  #password       = var.tkg_user_password
  allow_unverified_ssl = true
}

variable "vsphere_server" {
  type        = string
  description = "vsphere server IP or FQDN."
}
variable "vsphere_username" {
  type        = string
  description = "Admin user in vCenter."
}
variable "vsphere_password" {
  type        = string
  description = "Admin password."
}
#variable "tkg_user" {
#  type        = string
#  description = "Admin user in vCenter."
#}
#variable "tkg_user_password" {
#  type        = string
#  description = "Admin password."
#}
variable "vsphere_datacenter" {
  type        = string
  description = "Datacenter name..."
}
variable "cluster_name" {
  type        = string
  description = "Cluster name."
}
variable "storage_class" {
  type = string
  description = "Name of default storage class/policy"
}
variable "avi_controller_ip" {
  type = string
  description = "IP Address of the AVI controller."
}
#variable "avi_floating_ip" {
#  type = string
#  description = "IP Address of the AVI controller."
#}
variable "avi_certificate" {
  type = string
  description = "AVI Certificate."
}
variable "supervisor_network_static_address_count" {
  type = string
  description = "Number of IP addresses in supervisor IP Pool."
}
variable "supervisor_network_starting_ip" {
  type = string
  description = "Starting IP address of Supervisor VMs."
}
variable "supervisor_network_subnet_mask" {
  type = string
  description = "Supervisor network subnet mask."
}
variable "supervisor_network_gateway_ip" {
  type = string
  description = "Supervisor network gateway IP address."
}
variable "dns_server" {
  type = string
  description = "DNS server IPs or FQDNs comma separated."
}
variable "dns_search_domain" {
  type = string
  description = "DNS search domain."
}
variable "ntp_server" {
  type = string
  description = "NTP Server IPs or FQDNs comma separated."
}
variable "distributed_switch" {
  type = string
  description = "Name of Distributed Switch."
}
#variable "supervisor_network_id" {
#  type = string
#  description = "ID of the port-group for the supervisor cluster."
#}
variable "supervisor_network_name" {
  type = string
  description = "Name of the port-group for the supervisor cluster."
}
variable "primary_workload_network_vsphere_portgroup_name" {
  type = string
  description = "Name of the port-group for the primary workload cluster."
}
#variable "workload_network_id" {
#  type = string
#  description = "ID of the port-group for the workload cluster."
#}
variable "content_library" {
  type = string
  description = "vSphere Content Library name."
}
variable "avi_username" {
  type = string
  description = "AVI admin user name."
}
variable "avi_password" {
  type = string
  description = "AVI admin password."
}
#variable "content_library_id" {
#  type = string
#  description = "vSphere Content Library ID."
#}
variable "data_network_static_starting_address_ipv4" {
  type = string
  description = "Data network starting IP address."
}
variable "data_network_static_address_count" {
  type = string
  description = "Data network address count."
}
#variable "primary_workload_network_name" {
#  type = string
#  description = "Workload network name."
#}
variable "primary_workload_network_static_gateway_ipv4" {
  type = string
  description = "Workload cluster network gateway IP address."
}
variable "primary_workload_network_static_starting_address_ipv4" {
  type = string
  description = "Workload cluster network starting IP address."
}
variable "primary_workload_network_static_address_count" {
  type = string
  description = "Workload static address count."
}
variable "primary_workload_network_static_subnet_mask" {
  type = string
  description = "Workload cluster network subnet mask."
}
data "vsphere_datacenter" "dc" {
  name = var.vsphere_datacenter
}

# Converts the vSphere cluster name to its id
data "vsphere_compute_cluster" "fetch" {
  name = var.cluster_name
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_distributed_virtual_switch" "vds" {
  name          = var.distributed_switch
  datacenter_id = data.vsphere_datacenter.dc.id
}
data "vsphere_network" "workload_pg" {
  datacenter_id = data.vsphere_datacenter.dc.id
  name = var.primary_workload_network_vsphere_portgroup_name
}
data "vsphere_network" "mgmt_net" {
  name = var.supervisor_network_name
  datacenter_id = data.vsphere_datacenter.dc.id
}

data "vsphere_storage_policy" "sc" {
  name = var.storage_class
}

data "vsphere_content_library" "content_library" {
  name            = var.content_library
}

# Enables the Tanzu Supervisor Cluster
resource "namespace-management_cluster" "supervisor" {
  cluster_id = data.vsphere_compute_cluster.fetch.id
  master_storage_policy_id = data.vsphere_storage_policy.sc.id
  image_storage_policy_id = data.vsphere_storage_policy.sc.id
  ephemeral_storage_policy_id = data.vsphere_storage_policy.sc.id
  load_balancer_provider = "AVI"
  load_balancer_id = var.cluster_name
  # load_balancer_avi_host = var.avi_floating_ip
  load_balancer_avi_host = var.avi_controller_ip
  load_balancer_avi_ca_chain = var.avi_certificate
  load_balancer_avi_username = var.avi_username
  load_balancer_avi_password = var.avi_password
  master_network_ip_assignment_mode = "STATICRANGE"
  master_network_id = data.vsphere_network.mgmt_net.id
  master_network_static_starting_address_ipv4 = var.supervisor_network_starting_ip
  master_network_static_address_count = var.supervisor_network_static_address_count
  master_network_static_subnet_mask = var.supervisor_network_subnet_mask
  master_network_static_gateway_ipv4 = var.supervisor_network_gateway_ip
  master_dns_servers = var.dns_server
  worker_dns_servers = var.dns_server
  master_dns_search_domain = var.dns_search_domain
  master_dns_names = var.dns_search_domain
  master_ntp_servers = var.ntp_server
  workload_ntp_servers = var.ntp_server

  data_network_static_starting_address_ipv4 = var.data_network_static_starting_address_ipv4
  data_network_static_address_count = var.data_network_static_address_count

  primary_workload_network_vsphere_portgroup_id = data.vsphere_network.workload_pg.id
  primary_workload_network_name = var.primary_workload_network_vsphere_portgroup_name
  primary_workload_network_static_gateway_ipv4 = var.primary_workload_network_static_gateway_ipv4
  primary_workload_network_static_starting_address_ipv4 = var.primary_workload_network_static_starting_address_ipv4
  primary_workload_network_static_address_count = var.primary_workload_network_static_address_count
  primary_workload_network_static_subnet_mask = var.primary_workload_network_static_subnet_mask
  default_kubernetes_service_content_library_id = data.vsphere_content_library.content_library.id

}



# Only the newly enabled cluster (including the cluster ID)
output "cluster" {
  value = namespace-management_cluster.supervisor
  sensitive = true
}

output "content_library" {
  value = data.vsphere_content_library.content_library
}