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
variable "vsphere_datacenter" {
  type        = string
  description = "Datacenter name."
}
variable "cluster_name" {
  type        = string
  description = "Cluster name."
}
#variable "tkg_user" {
#  type        = string
#  description = "TKG Admin User name."
#}
variable "tkg_role" {
  type        = string
  description = "TKG role name."
}
variable "avi_role" {
  type        = string
  description = "AVI role name."
}
#variable "avi_vsphere_username" {
#  type        = string
#  description = "AVI vSphere User name."
#}
provider "vsphere" {
  user           = var.vsphere_username
  password       = var.vsphere_password
  vsphere_server = var.vsphere_server
  allow_unverified_ssl = true
}
data "vsphere_datacenter" "datacenter" {
  name = var.vsphere_datacenter
}
data "vsphere_compute_cluster" "cluster" {
  name = var.cluster_name
  datacenter_id = data.vsphere_datacenter.datacenter.id
}
resource "vsphere_role" "tkg_admin_role" {
  name = var.tkg_role
  role_privileges = ["Cns.Searchable", "Datastore.AllocateSpace", "ContentLibrary.ManageRegistry", "ContentLibrary.ManageClusterRegistryResource", "ContentLibrary.EvictLibraryItem", "ContentLibrary.TypeIntrospection", "ContentLibrary.GetConfiguration", "ContentLibrary.DeleteCertFromTrustStore", "ContentLibrary.UpdateSession", "ContentLibrary.AddSubscription", "ContentLibrary.DeleteSubscription", "ContentLibrary.UpdateLibrary", "ContentLibrary.SyncLibraryItem", "ContentLibrary.UpdateSubscribedLibrary", "ContentLibrary.UpdateLibraryItem", "ContentLibrary.DeleteLibraryItem", "ContentLibrary.AddCertToTrustStore", "ContentLibrary.ManageRegistryProject", "ContentLibrary.SyncLibrary", "ContentLibrary.UpdateConfiguration", "ContentLibrary.CheckOutTemplate", "ContentLibrary.PublishLibraryItem", "ContentLibrary.UpdateSubscription", "ContentLibrary.DownloadSession", "ContentLibrary.CheckInTemplate", "ContentLibrary.DeleteLocalLibrary", "ContentLibrary.EvictSubscribedLibrary", "ContentLibrary.DeleteSubscribedLibrary", "ContentLibrary.ImportStorage", "ContentLibrary.CreateSubscribedLibrary", "ContentLibrary.UpdateLocalLibrary", "ContentLibrary.PublishLibrary", "ContentLibrary.ProbeSubscription", "ContentLibrary.ReadStorage", "ContentLibrary.AddLibraryItem", "ContentLibrary.CreateLocalLibrary", "Datastore.Browse", "Datastore.FileManagement", "Global.DisableMethods", "Global.EnableMethods", "Global.Licenses", "Host.Config.Storage", "Namespaces.Manage", "Network.Assign", "Resource.AssignVMToPool", "Sessions.GlobalMessage", "Sessions.ValidateSession", "StorageProfile.View", "SupervisorServices.Manage", "VirtualMachine.Config.AddExistingDisk", "VirtualMachine.Config.AddNewDisk", "VirtualMachine.Config.AddRemoveDevice", "VirtualMachine.Config.AdvancedConfig", "VirtualMachine.Config.CPUCount", "VirtualMachine.Config.ChangeTracking", "VirtualMachine.Config.DiskExtend", "VirtualMachine.Config.EditDevice", "VirtualMachine.Config.Memory", "VirtualMachine.Config.RawDevice", "VirtualMachine.Config.RemoveDisk", "VirtualMachine.Config.Settings", "VirtualMachine.Interact.PowerOff", "VirtualMachine.Interact.PowerOn", "VirtualMachine.Inventory.CreateFromExisting", "VirtualMachine.Inventory.Delete", "VirtualMachine.Provisioning.DeployTemplate", "VirtualMachine.Provisioning.DiskRandomRead", "VirtualMachine.Provisioning.GetVmFiles", "VirtualMachine.State.CreateSnapshot", "VirtualMachine.State.RemoveSnapshot", "VApp.Import"]
}
resource "vsphere_role" "AviRole-Global" {
  name = var.avi_role
  role_privileges = ["ContentLibrary.AddLibraryItem", "ContentLibrary.DeleteLibraryItem", "ContentLibrary.UpdateLibraryItem", "ContentLibrary.UpdateSession", "Datastore.AllocateSpace", "Datastore.DeleteFile", "Network.Assign", "Network.Delete", "VApp.Import", "VirtualMachine.Config.AddNewDisk", "Folder.Create", "Resource.AssignVMToPool", "Task.Create", "Task.Update", "VApp.ApplicationConfig", "VApp.AssignResourcePool", "VApp.AssignVApp", "VApp.AssignVM", "VApp.Create", "VApp.Delete", "VApp.Export", "VApp.Import", "VApp.InstanceConfig", "VApp.PowerOff", "VApp.PowerOn", "VirtualMachine.Config.AddExistingDisk", "VirtualMachine.Config.AddNewDisk", "VirtualMachine.Config.AddRemoveDevice", "VirtualMachine.Config.AdvancedConfig", "VirtualMachine.Config.CPUCount", "VirtualMachine.Config.DiskExtend", "VirtualMachine.Config.DiskLease", "VirtualMachine.Config.EditDevice", "VirtualMachine.Config.Memory", "VirtualMachine.Config.MksControl", "VirtualMachine.Config.RemoveDisk", "VirtualMachine.Config.Resource", "VirtualMachine.Config.Settings", "VirtualMachine.Interact.DeviceConnection", "VirtualMachine.Interact.PowerOff", "VirtualMachine.Interact.PowerOn", "VirtualMachine.Interact.Reset", "VirtualMachine.Interact.ToolsInstall", "VirtualMachine.Inventory.Create", "VirtualMachine.Inventory.Delete", "VirtualMachine.Inventory.Register", "VirtualMachine.Inventory.Unregister", "VirtualMachine.Provisioning.DeployTemplate", "VirtualMachine.Provisioning.DiskRandomAccess", "VirtualMachine.Provisioning.DiskRandomRead", "VirtualMachine.Provisioning.FileRandomAccess", "VirtualMachine.Provisioning.MarkAsVM"]
}
