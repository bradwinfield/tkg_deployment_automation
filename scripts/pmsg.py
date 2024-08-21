#!/usr/bin/env python3

# Importable library of routines for printing messages with color.

import os

# CONSTANTS
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\033[36m'
class pmsg():
    """
    Class used to print messages in color.
    """
def __init__(self):
    pass

def print_log_file_msg():
    print("See logfile: " + log_filename())

def log_filename():
    # site_name = os.environ["site_name"]
    # return "logs/" + site_name + "_deployment.log"
    if "deployment_log" in os.environ.keys():
        return os.environ["deployment_log"]
    else:
        return "/tmp/deployment_log"

def printm(msg):
    print(msg)
    with open(log_filename(), 'a') as out:
        out.write(msg + '\n')

def notice(msg):
    printm (bcolors.HEADER + "NOTICE: " + bcolors.ENDC + " " + msg)

def dry_run(msg):
    printm (bcolors.WARNING + "WARNING: " + bcolors.ENDC + " " + msg + " " + bcolors.FAIL + "The dry_run flag is on." + bcolors.ENDC)

def warning(msg):
    printm (bcolors.WARNING + "WARNING: " + bcolors.ENDC + " " + msg)

def fail(msg):
    printm (bcolors.FAIL + "ERROR: " + bcolors.ENDC + " " + msg)

def green(msg):
    printm (bcolors.OKGREEN + msg + bcolors.ENDC)

def blue(msg):
    printm (bcolors.OKBLUE + msg + bcolors.ENDC)

def debug(msg):
    printm (bcolors.GREY + "  DEBUG: " + msg + bcolors.ENDC)

def normal(msg):
    printm (msg)

def running(msg):
    printm (bcolors.BOLD + "  Running: " + msg + bcolors.ENDC)

def underline(msg):
    printm ("   " + bcolors.UNDERLINE + bcolors.OKBLUE + msg + bcolors.ENDC)