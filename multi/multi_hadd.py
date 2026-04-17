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

base = "MultiJob_{}-{}_HistoMode"
samples = ['muon18', 'dy', 'dy', 'wjets', 'ttbar', 'minor_electroweak']
multidirs = [base.format(args.tag, sample) for sample in samples]
filenames = ['data_DATA_', 'wjets_WJETS_', 'ttjets_TTJETS_', 'dy_DYsig_', 'dy_DYbkg_']

def loop(run=False):
    for multidir, filename in zip(multidirs, filenames):
        command = "./hadd_histo_dirs.py " + str(multidir) + " -o "+str(filename)+args.tag+".root"
        print(command)
        if run: os.system(command)

loop()
response = input("Proceed? (y/n): ")
if response == 'y':
    loop(run=True)
