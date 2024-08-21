#!/usr/bin/env bash

set -x
# Removes all files in temp used by this run of the pipeline

# Get rid of the scripts temp files
rm -rf /tmp/${USER}_${site_name}*

# Get rid of the site_terraform/$site_name files...
rm -rf site_terraform/${site_name} site_terraform/${site_name}/.t*
