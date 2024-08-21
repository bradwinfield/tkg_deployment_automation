#!/usr/bin/env bash

# assumes context to workload cluster is already set.
# assumes you are logged into the cluster.

NODE_COUNT=0
RESIZE_COUNT=0
for node in $(kubectl get nodes | grep -vE 'NAME|control.plane' | awk '{print $1}'); do
  NODE_COUNT=$(($NODE_COUNT+1))
  MEM=$(kubectl get node $node  -o jsonpath='{.status.capacity.memory}')
  echo "$MEM is on node $node"
  if [[ $MEM =~ "32" ]]; then
    echo "found 32."
    RESIZE_COUNT=$(($RESIZE_COUNT+1))
  else
    echo "found $MEM... node not resized yet."
  fi
done

echo "-----------------------------------------------------------"
echo "Of $NODE_COUNT worker nodes, $RESIZE_COUNT have been resized."
