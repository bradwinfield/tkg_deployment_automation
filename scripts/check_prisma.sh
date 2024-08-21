#!/usr/bin/env bash

# This script installs Prisma Twistlock

kubectl get ds -n twistlock |grep -qE 'twistlock'

if [[ $? -eq 0 ]]; then
  echo "Prisma Twistlock installed ok."
  exit 0
fi

cd /usr/src/cloud-development
helm install twistlock-defender twistlock-defender --set cluster=$workload_cluster --create-namespace -n twistlock
