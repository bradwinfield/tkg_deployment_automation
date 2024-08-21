#!/usr/bin/env python3

# General purpose python functions

import os
import subprocess
import pmsg
import re
import time
import operator as op
from distutils.version import LooseVersion
import pdb

lookup = {'<': op.lt, '<=': op.le, '==': op.eq, '>=': op.ge, '>': op.gt}

class helper():
    """
    Class used to provide general purpose python functions.
    """


env_override_file = "/tmp/env_override_file"


# ########################################################
def __init__(self):
    pass


# ########################################################
def run_a_command_list(command):
    """
    :param command: List of command and all its arguments.
    :returns: Integer - Returns the number of errors the command caused.
    :rtype: int
    """

    # Split up 'command' so it can be run with the subprocess.run method...
    myenv = dict(os.environ)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=myenv)
    output, err = process.communicate()
    if err is not None:
        return 1
    return 0


# ########################################################
def run_a_command(command):
    """
    :param command: String of command and all its arguments.
    :returns: Integer - Returns the number of errors the command caused.
    :rtype: int
    """

    # Split up 'command' so it can be run with the subprocess.run method...
    pmsg.running(command)
    cmd_parts = command.split()
    myenv = dict(os.environ)
    returns = subprocess.run(cmd_parts, env=myenv)
    return returns.returncode

#############################################################
def run_a_command_get_stdout(command_and_args_list):
    """
    :param command: string array of command and all its arguments.
    :returns: String - stdout of command
    :rtype: str
    """
    tlines = []
    process = subprocess.Popen(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    # Split up the lines and decode each line and remove newlines...
    if output is not None:
        lines = output.splitlines()
        for line in lines:
            tlines.append(line.decode('utf-8').strip())

    return tlines


#############################################################
def check_for_result(command_and_args_list, expression):
    """Checks to see if a given command returns an expected value.

    Args:
        command_and_args_list (list): Run this command with arguments and capture the output.
        expression (string): Split the result of the command into lines and see if any line matches this expression.
    :returns: Boolean - Match or no match
    :rtype: Boolean
    """

    # Run the command capturing the stdout
    process = subprocess.Popen(command_and_args_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = process.communicate()
    lines = output.splitlines()
    for line in lines:
        if re.search(expression, line.decode("utf-8")) is not None:
            return True
    return False

def add_env_override(newfile, varname, value):
    """ Create (if newfile=True) or add to the environment override file and put the varname and value in it.

    Args:
        newfile (Boolean): create a new override file if True. Otherwise just add a new line to it.
        varname (string): name of environment variable to set (export).
        value (string): value of variable.
    :returns: Boolean - writing to envirnment override file success.
    :rtype: Boolean
    """
    openflag = 'a'
    if newfile:
        openflag = 'w'
    with open(env_override_file, openflag) as env_file:
        env_file.write(varname + ": |-\n")
        env_file.write('  ' + value.replace('\n', '\n  '))
        env_file.write("\n\n")


def check_for_result_for_a_time(command_and_args_list, expression, check_how_often, max_checks):
    """
    Run a command with arguments and check the output for a specific string of text (regular expression) over a time period.

    Args:
        command_and_args_list (list): Run this command with arguments and capture the output.
        expression (string): Split the result of the command into lines and see if any line matches this expression.
        check_how_often (int): check every <check_how_often> seconds for the expression.
        max_checks (int): check a maxiumum of this many times before giving up.

    :returns: Boolean - Match or no match
    :rtype: Boolean

    """
    found = False
    for i in range(max_checks):
        if check_for_result(command_and_args_list, expression):
            found = True
            break
        time.sleep(check_how_often)

    return found

def get_address_with_offset(ip_address, count):
    # Split this into 4 octets and add the count to the last octet and put it back together.
    parts = re.split('\.', ip_address)
    part4 = int(parts[3]) + count-1
    return parts[0] + "." + parts[1] + "." + parts[2] + "." + str(part4)

def check_versions(ver1, comparison_operator, ver2):
    """ Compares two version strings using only the numerics.
    Args:
        ver1 (string): a version string like "1.9.1+vmware.1-tkg.1"
        comparison_operator (string): '>' or '<' or '<=' or '==' or '>='
        ver2 (string): a version string like "1.26.2+vmware.1-tkg.1"
    :returns: Boolean - True or False
    :rtype: bool
    """
    v1 = re.sub('[^(.\d)]', '', ver1)
    v2 = re.sub('[^(.\d)]', '', ver2)
    try:
        return lookup[comparison_operator](LooseVersion(v1), LooseVersion(v2))
    except KeyError:
        # unknown specifier
        return False

def return_newest_version(list_of_lines):
    """ Given a list of lines, find which column contains a versioin number.
    Args:
        list of strings (e.g. list from 'tanzu package available list <packagename>')
    :returrn: largest version number found
    :rtype: str
    """

    # which column contains the version numbers?
    # Split line up and find the column with the version numbers
    parts = list_of_lines[len(list_of_lines)-1].split()
    vercol = 0
    for col in parts:
        if re.match('\\d+\\.\\d+', col):
            break
        vercol = vercol + 1

    if vercol < 1 or vercol > 5:
        pmsg.fail("Can't determine which column contains the version number when listing tanzu packages.")
        exit(1)

    # Create list with just the version columns...
    versions = []
    for line in list_of_lines:
        parts = line.split()
        if len(parts)-1 < vercol:
            continue
        versions.append(parts[vercol])

    # Determine the most recent version
    return find_newest_version(versions)

def find_newest_version(versions):
    """ compares all the elements of versions and returns the newest/most recent one.
    Args:
        versions string[]: an array of strings containing version numbers (e.g. ["1.9.1+vmware.1-tkg.1", "1.10.4+vmware.1-tkg.3"])
    :returns: largest version found
    :rtype: str
    """
    newest = "0"
    for version in versions:
        if check_versions(version, ">", newest):
            newest = version
    if newest == "0":
        return None
    return newest

def get_package_name_option():
    # Run tanzu version and get the version number. If it is v0.25.x, "--package-name"
    option_name = "--package"
    if check_for_result(["tanzu", "version"], "v0.25"):
        option_name = "--package-name"
    return option_name

def valid_certificate(cert_text_base64_encoded):
    """
    :param cert_text_base64_encoded: string value of certificate that is still base64 encoded.
    :returns: Boolean - cert or not
    :rtype: Boolean
    """

    cmd_parts = ["openssl", "x509", "-text"]

    pmsg.running("Checking certificate...")
    myenv = dict(os.environ)
    process = subprocess.Popen(cmd_parts, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=myenv)

    output, err = process.communicate(input=bytes(cert_text_base64_encoded,'utf-8'))

    # If no error, then return True
    if err == b'':
        return True
    return False