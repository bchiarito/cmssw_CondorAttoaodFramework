#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("tag", help='')
parser.add_argument("multidirs", nargs='+', help='')
args = parser.parse_args()

names = ['data_DATA_', 'wjets_WJETS_', 'ttjets_TTJETS_', 'dy_DYsig_', 'dy_DYbkg_']

if not len(args.multidirs) == len(names):
    print("too many/too few inputs")
    sys.exit()

for multidir, name in zip(args.multidirs, names):
    command = "./hadd_histo_dirs.py " + str(multidir) + " -o "+str(name)+args.tag+".root"
    print(command)

response = raw_input("Proceed? (y/n): ")
if not response == 'y': sys.exit()

for multidir, name in zip(args.multidirs, names):
    command = "./hadd_histo_dirs.py " + str(multidir) + " -o "+str(name)+args.tag+".root"
    print(command)
    os.system(command)
