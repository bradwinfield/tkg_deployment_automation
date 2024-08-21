#!/usr/bin/env bash

# Update the coredns deployment...
kubectl -n kube-system set resources deployment/coredns --limits=memory=256Mi
