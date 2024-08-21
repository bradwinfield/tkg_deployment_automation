#!/usr/bin/env bash

# Changes all the config.yaml files found in /usr/src/cloud-development/tanzu-cluster-config/*/config.yaml
# Set $cluster_config_dir to override the default config directory.

USAGE="$0 <variable-name> <new-value>"
if [[ $# -ne 2 ]]; then
    echo "Usage: $USAGE"
    echo "Note: If you set the environment variable \"cluster_config_dir\", it will override the default."
    exit 1
fi

if [[ -z $cluster_config_dir ]]; then
    cluster_config_dir="/usr/src/cloud-development/tanzu-cluster-config"
fi

varname=$1
value=$2
tmp_suffix=$$

echo "Setting ${varname} to \"${value}\""
for config in $(ls $cluster_config_dir/*/config.yaml); do
    mv $config $config.$tmp_suffix
    echo "Updating $config..."
    cat $config.$tmp_suffix | sed "s/^${varname}:.*/${varname}: \"$value\"/" > $config
done

echo "Done."
