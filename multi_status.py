#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import imp
import argparse
parser = argparse.ArgumentParser(description='Executes multiple condor_submit.py commands, configuration inside script')
parser.add_argument('-t', '--test', action='store_true', help='print command but do not run')
parser.add_argument('-p', '--plots', action='store_true', help='check plotting jobs under plotting_jobs/')
parser.add_argument('prefix', help='full run on all matching jobs directories')
args = parser.parse_args()
jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

locs = {}
for d in sorted(os.listdir('.')):
  if os.path.isdir(d) and d.startswith(args.prefix):
    if not args.plots: command = './condor_status.py -s '+d
    else: command = './condor_status.py -s '+d+'/plotting_jobs/'
    print('>>> '+command)
    os.system(command)
    print()

