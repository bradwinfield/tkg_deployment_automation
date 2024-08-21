#!/usr/bin/env python3

# Prints out what is in the environment

import os
import re

for key in os.environ.keys():
    if re.search('pass|cert|TF_VAR_', key) is not None:
        continue
    print(key + ": " + os.environ[key])
print("Sensitive variables and TF_VAR_ variables have been ignored.")
