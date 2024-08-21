#!/usr/bin/env bash

# Script to prepare the jumpbox with the CLIs (tanzu, kubectl, kapp, ytt, etc.)
# Run this from your home directory.
cd $HOME

echo
echo 'Get the CLI bundles (tanzu, velero, tkg-carvel-tools) from vmware. Do not bother getting kubectl at this time.'
echo See: https://docs.vmware.com/en/VMware-Tanzu-Kubernetes-Grid/1.6/vmware-tanzu-kubernetes-grid-16/GUID-install-cli.html
echo 'Or go directly to: https://customerconnect.vmware.com/downloads/details?downloadGroup=TKG-161&productId=988'
echo I am assuming that the files will end up in your Downloads subdirectory.
echo This can be skipped if the 'tanzu' and 'velero' commands are already on this system.
echo Hit return when done.
read ANS

echo "=================================== Download kubectl vsphere-plugin"
echo "Use your browser to go to your vCenter, navigate to Inventory and find your namespace."
echo "If there is only a supervisor cluster, then you can go to the IP of one of the supervisor cluster IPs."
echo "From there, find the 'Status' panel. Then click the 'Open' link which will lead you"
echo "to downloading the kubectl CLI tools."
echo This can be skipped if the 'kubectl' with the vsphere plugins are already on this system.
echo "Hit return when you have it downloaded."
read ANS

# check for tanzu download...
tanzu_available=false
ls Downloads | grep -qE "^tanzu.*gz$"
if [[ $? == 0 ]]; then
    gunzip Downloads/tanzu*.gz
    tanzu_available=true
fi

# check for the velero download...
velero_available=false
ls Downloads | grep -qE "^velero.*gz$"
if [[ $? == 0 ]]; then
    gunzip Downloads/velero*.gz
    velero_available=true
fi

echo "==================================== Running apt to get necessary packages..."
sudo apt update
sudo apt install python3-pip -y
sudo apt install git -y
sudo apt install openssh-server -y
sudo apt install curl -y

# install helm this way...
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm

echo "Adding python libraries needed for automation..."
pip3 install pyVmomi
pip3 install pyVim
pip3 install requests
pip3 install pyyaml
pip3 install jinja2
pip3 install paramiko

if [[ $tanzu_available ]]; then
  echo "==================================== Installing 'tanzu' CLI..."
  mkdir Downloads/tanzu
  tar xvf Downloads/tanzu*.tar -C Downloads/tanzu
  sudo install Downloads/tanzu/cli/core/v0.25.4/tanzu-core-linux_amd64 /usr/local/bin/tanzu
  # Version 0.90.1: sudo install Downloads/tanzu/v*/tanzu-*amd64 /usr/local/bin/tanzu
fi

# Try to initialize tanzu for this user in case it is already in /usr/local/bin
tanzu init
tanzu version
tanzu plugin clean
tanzu plugin sync
tanzu plugin list

if [[ -d Downloads/tanzu ]]; then
echo "==================================== Installing 'tkg-carvel-tools'..."
# for vsphere 8: Downloads/cli
# cd Downloads
# gunzip tkg-carvel-tools*.gz
# tar xvf tkg-carvel-tools*.tar
# subdir=cli
echo "==================================== Installing 'ytt' CLI..."
gunzip Downloads/tanzu/cli/ytt*.gz
chmod ugo+x Downloads/tanzu/cli/ytt*.1
sudo install Downloads/tanzu/cli/ytt*.1 /usr/local/bin/ytt
ytt version

echo "==================================== Installing 'kapp' CLI..."
gunzip Downloads/tanzu/cli/kapp*.gz
chmod ugo+x Downloads/tanzu/cli/kapp*.1
sudo install Downloads/tanzu/cli/kapp*.1 /usr/local/bin/kapp
kapp version

echo "==================================== Installing 'kbld' CLI..."
gunzip Downloads/tanzu/cli/kbld*.gz
chmod ugo+x Downloads/tanzu/cli/kbld*.1
sudo install Downloads/tanzu/cli/kbld*.1 /usr/local/bin/kbld
kbld version

echo "==================================== Installing 'imgpkg' CLI..."
gunzip Downloads/tanzu/cli/imgpkg*.gz
chmod ugo+x Downloads/tanzu/cli/imgpkg*.1
sudo install Downloads/tanzu/cli/imgpkg*.1 /usr/local/bin/imgpkg
imgpkg version
fi

if [[ -f Downloads/vsphere-plugin.zip ]]; then
  unzip Downloads/vsphere-plugin.zip
  echo "==================================== Installing 'kubectl' and the vsphere plugin CLI..."
  sudo install bin/kubectl /usr/local/bin/kubectl
  sudo install bin/kubectl-vsphere /usr/local/bin/kubectl-vsphere
fi

echo "==================================== Installing 'Terraform..."
sudo apt-get update
sudo apt-get install -y gnupg software-properties-common curl
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main" --yes
sudo apt-get update && sudo apt-get install -y terraform

echo "==================================== Installing 'Golang..."
sudo apt-get remove --auto-remove golang-go
sudo rm -rvf /usr/local/go
wget https://go.dev/dl/go1.20.2.linux-amd64.tar.gz -P Downloads
sudo tar -xzvf Downloads/go1.20.2.linux-amd64.tar.gz -C Downloads
sudo mv Downloads/go /usr/local

# Check for go already in PATH
echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
echo "export GOPATH=$HOME/go" >> ~/.bashrc
echo "export PATH=$PATH:$HOME/go/bin" >> ~/.bashrc
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$HOME/go/bin
echo "NOTE: Run $ source ~/.bashrc  # when this script finishes."
go version
echo "Go-lang Installed now"

echo "==================================== Installing 'Govmomi..."
mkdir Downloads/govmomi
chmod +x Downloads/govmomi
#git clone https://github.com/vmware/govmomi.git Downloads/govmomi
git clone https://github.com/adamfowleruk/govmomi.git Downloads/govmomi
cd Downloads/govmomi/
go get -u github.com/vmware/govmomi
echo "Govmomi library is enabled" 
echo "==================================== Installing 'govc..."
go install github.com/vmware/govmomi/govc@latest 
cd $HOME

echo "==================================== Building the terraform-provider-namespace-management using GO ..."
rm -rf Downloads/terraform-provider-namespace-management
cd Downloads
git clone https://github.com/vmware-tanzu-labs/terraform-provider-namespace-management.git
cd terraform-provider-namespace-management/
go mod download github.com/a8m/tree
go build -o terraform-provider-namespace-management
echo "WARNING: Change the Makefile OS_ARCH to linux_amd64 before proceeding."
mv Makefile orig_Makefile
cat orig_Makefile | sed 's/OS_ARCH=darwin_amd64/OS_ARCH=linux_amd64/' > Makefile
make install
cd $HOME
echo "====== All the required tooling has been installed and configured on VSphere Tanzu Jumpbox..."

echo "================================ install docker CLI ========================"
sudo apt-get remove docker docker-engine docker.io
sudo apt-get update
sudo apt install docker.io -y
sudo snap install docker
docker --version

newgrp docker

echo "================================ install PowerShell ========================"
# Update the list of packages
sudo apt-get update
# Install pre-requisite packages.
sudo apt-get install -y wget apt-transport-https software-properties-common
# Download the Microsoft repository GPG keys
wget -q "https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb"
# Register the Microsoft repository GPG keys
sudo dpkg -i packages-microsoft-prod.deb
# Delete the the Microsoft repository GPG keys file
rm packages-microsoft-prod.deb
# Update the list of packages after we added packages.microsoft.com
sudo apt-get update
# Install PowerShell
sudo apt-get install -y powershell

# Install stuff so the jumpbox can send email
sudo apt install postfix
sudo apt install mailutils

echo "NOTE: Run $ source ~/.bashrc"
