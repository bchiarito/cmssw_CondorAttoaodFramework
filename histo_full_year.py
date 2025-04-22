#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import argparse

parser = argparse.ArgumentParser(description="")
parser.add_argument("tag", help='')
parser.add_argument("multidirs", nargs='+', help='')
parser.add_argument('-y', '--year', default='18', choices=['18', '17', '16'], help='')
args = parser.parse_args()

names = ['--data', '--mc', '--mc', '--sigRes', '--sigNonRes']
extras = ['', '', '', '_sigRes', '_sigNonRes']

if not len(args.multidirs) == len(names):
    print("too many/too few inputs")
    sys.exit()

for multidir, name, extra in zip(args.multidirs, names, extras):
    command = "./multi_run.py histo {} {} -y={} --subtag {}".format(multidir, name, args.year, args.tag+extra)
    print(command)

response = raw_input("Proceed? (y/n): ")
if not response == 'y': sys.exit()

for multidir, name, extra in zip(args.multidirs, names, extras):
    command = "./multi_run.py histo {} {} -y={} --subtag {}".format(multidir, name, args.year, args.tag+extra)
    print(command)
    os.system(command)
