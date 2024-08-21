variable "vsphere_server" {
  type        = string
  description = "vCenter FQDN."
}
variable "vsphere_username" {
  type        = string
  description = "Admin user in vCenter."
}
variable "vsphere_password" {
  type        = string
  description = "Admin password."
}

// Avi Provider variables
variable "avi_username" {
  type = string
  default = ""
}

# The NEW password to specify after installation
variable "avi_password" {
  type = string
  default = ""
  sensitive = true
}

variable "vsphere_datacenter" {
  type    = string
  default = "vc01"
}

variable "avi_resource_pool_id" {
  type    = string
  default = ""
}

variable "avi_content_library" {
  type    = string
  default = ""
}

variable "datastore" {
  type    = string
  default = ""
}

variable "avi_network" {
  type    = string
  default = ""
}

#variable "vm_folder" {
#  type    = string
#  default = ""
#}

variable "avi_ova_name" {
  type    = string
  default = ""
}
variable "avi_version" {
  type    = string
  default = ""
}
variable "avi_vm_name1" {
  type    = string
  default = ""
}
variable "avi_vm_ip1" {
  type    = string
  default = ""
}
variable "avi_vm_name2" {
  type    = string
  default = ""
}
variable "avi_vm_ip2" {
  type    = string
  default = ""
}
variable "avi_vm_name3" {
  type    = string
  default = ""
}
variable "avi_vm_ip3" {
  type    = string
  default = ""
}

variable "avi_subnet_mask" {
  type    = string
  default = ""
}

variable "avi_default_gateway" {
  type    = string
  default = ""
}

// New variables for full OVA settings:-
// TODO support multiple avi controllers
#variable "avi_management_hostname" {
  #type = string
  #default = "avi-controller-1"
#}
#variable "avi_management_ip_address" {
  #type = string
  #default = "10.2.0.50"
#}

# The following is an integer but written as a string (Avi provider requirement)
#variable "avi_management_subnet_mask_int" {
  #type = string
  #default = "24"
#}
#variable "avi_management_default_gateway" {
  #type = string
  #default = "10.2.0.1"
#}