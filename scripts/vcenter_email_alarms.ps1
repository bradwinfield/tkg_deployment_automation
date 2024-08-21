#!/usr/bin/env pwsh

# Powershell script to update email actions in list of vCenter Alarm Definitions
# need the following variables...
# - vsphere_server
# - vsphere_username
# - vsphere_password
# - email_address
# File name that contains all of the Alarm Definitions to be updated with email actions.

$vCenterServer = $Env:vsphere_server
$user = $Env:vsphere_username
$pass = $Env:vsphere_password
$MailTo = $Env:notification_email

if($MailTo -notmatch ".*@.*") {
  Write-Error "The 'notification_email' config line is missing or incorrect (not an email address) in your config.yaml file."
  exit 1
}

# Constants
$vCenterAlarmsFile = "templates/vcenter_alarm_list.txt"

# Bring in the vmware module...
if(-not (Get-Module -Name VMware.PowerCLI -ListAvailable)){
      Install-Module -Name VMware.PowerCLI -AllowClobber -Force -Confirm:$false | Out-Null
  }

# You can participate (or not) in the vmware Customer Experience Improvement Program using this next call...
# You only have to do this once and then exit pwsh. The next time you get in, you won't get all the CEIP
# notices.
# Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP:$true or $false

# Ignore self-signed certificate in vCenter if I encounter one...
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false | Out-Null

Write-Output "Connecting to $vCenterServer"
try {
  Connect-VIServer -Server $vCenterServer -Protocol https -User $user -Password $pass -ErrorAction Stop
}
catch {
  Write-Error "Can't login to vCenter $vCenterServer."
  exit 1
}

# Read in the list of Alarm Definition Names that need to be updated...
[string[]]$AlarmNames = Get-Content -Path $vCenterAlarmsFile

#--------------------------------------------------------------------#
# Delete Alarm Trigger;
#--------------------------------------------------------------------#
Write-Output "Clearing all existing notification AlarmActions..."
Get-AlarmDefinition -Name $AlarmNames | Get-AlarmAction | Remove-AlarmAction -Confirm:$false
#--------------------------------------------------------------------#
# Create Alarm Trigger;
#--------------------------------------------------------------------#
Write-Output "Creating email AlarmAction..."
Get-AlarmDefinition -Name $AlarmNames | New-AlarmAction -Email -To "$MailTo" -Subject "From $vCenterServer - {alarmName} - {newStatus}" | Out-Null
Write-Output "Adding AlarmActionTrigger from Green to Yellow..."
Get-AlarmDefinition -Name $AlarmNames | Get-AlarmAction | New-AlarmActionTrigger -StartStatus "Green" -EndStatus "Yellow" | Out-Null
# Write-Output "Adding AlarmActionTrigger from Yellow to Red..."
# Get-AlarmDefinition -Name $AlarmNames | Get-AlarmAction | New-AlarmActionTrigger -StartStatus "Yellow" -EndStatus "Red" | Out-Null
Write-Output "Adding AlarmActionTrigger back to Green..."
Get-AlarmDefinition -Name $AlarmNames | Get-AlarmAction | New-AlarmActionTrigger -StartStatus "Red" -EndStatus "Green" | Out-Null

#--------------------------------------------------------------------#
# Make sure all Alarm Definitions are enabled...
#--------------------------------------------------------------------#
Write-Output "Making sure all the alarm definitions are 'enabled'."
Get-AlarmDefinition -Name $AlarmNames | Set-AlarmDefinition -Enabled:$true | Out-Null

#--------------------------------------------------------------------#
# Disconnect vCenter server;
#--------------------------------------------------------------------#
Disconnect-VIServer -Server $vCenterServer -Force:$true -Confirm:$false
#--------------------------------------------------------------------#

exit 0
