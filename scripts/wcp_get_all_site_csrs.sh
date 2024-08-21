#!/usr/bin/env bash

# Cycles through all the sites and runs the pipeline to generate a CSR; one for each site.

SITES_DIR="/usr/src/cloud-development/tanzu-cluster-config"
SITES_DIR="/tmp/tanzu-cluster-config"

# walk through all the sites and configs
for SITE in $(ls ${SITES_DIR}); do
    CONFIG=${SITES_DIR}/${SITE}/config.yaml
    ACCESS=${SITES_DIR}/${SITE}/access.yaml
    ./run_pipeline.py -c ${CONFIG} -s steps_wcp_csr.conf -p ${ACCESS}
done

# For this site's config, run the pipeline to generate a wcp CSR...
