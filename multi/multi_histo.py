#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import imp
import socket
import argparse
from datetime import datetime, timedelta, date
import yaml
from functools import reduce

parser = argparse.ArgumentParser(description='')
#parser.add_argument('multidirs', nargs='+', help='')
parser.add_argument('tag', help='')
args = parser.parse_args()

base = "MultiJob_{}-{}"
samples = ['muon18', 'dy', 'dy', 'wjets', 'ttbar', 'minor_electroweak']
multidirs = [base.format(args.tag, sample) for sample in samples]

def loop(run=False):
    for i, multidir in enumerate(multidirs):
        if i == 0: datamc = '--data '
        if i == 1: datamc = '--sigRes '
        if i == 2: datamc = '--sigNonRes '
        if i >= 3: datamc = '--mc '
        command = "./multi_run.py -f histo " + datamc + multidir
        if i == 1: command += ' --subtag sigRes'
        if i == 2: command += ' --subtag sigNonRes'
        print(command)
        if run: os.system(command)

loop()
response = input("Proceed? (y/n): ")
if response == 'y':
    loop(run=True)
