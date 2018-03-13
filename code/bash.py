import logging
import os
import subprocess


def check_output(cmd, lvl=logging.INFO, purpose=""):
    output = check_output_without_log(cmd, purpose)
    if purpose: purpose = " # out; purpose: " + purpose
    for line in output.splitlines():
        logging.log(lvl, line.strip() + purpose)
    return output


def check_output_without_log(cmd, purpose=""):
    if purpose: purpose = " # purpose: " + purpose
    logging.info(cmd + purpose)
    output = subprocess.check_output(cmd, shell=True, executable='/bin/bash')
    encoded_output = output.decode('utf-8').rstrip()
    return encoded_output


def call_silent(cmd):
    logging.info(cmd)
    with open(os.devnull, 'w') as devnull:
        return subprocess.call(cmd, shell=True, executable='/bin/bash', stderr=devnull, stdout=devnull)
