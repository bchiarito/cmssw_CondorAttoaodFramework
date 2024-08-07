#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import argparse
from functools import reduce
import shutil
import ROOT
import helper.plotting_util as util

# command line options
parser = argparse.ArgumentParser(description="sums with hadd for atto/histo job output")
parser.add_argument("multidirs", nargs='+', help='Job_ or MultiJob_ dir or eos area')
parser.add_argument("-o", "--out", help='')
parser.add_argument("--retain", action='store_true', default=False, help='')
parser.add_argument("--rehadd", action='store_true', default=False, help='')
parser.add_argument("--nomove", action='store_true', default=False, help='')
args = parser.parse_args()

# constants
hadd_dir_name = "hadd"

# init
multijob_dirs = []
for multidir in args.multidirs: multijob_dirs.append(multidir)

# hadd
for multijob_dir in multijob_dirs:
  if not os.path.isdir(multijob_dir): continue
  hadd_dir = os.path.join(multijob_dir, hadd_dir_name)
  if args.rehadd and os.path.isdir(hadd_dir): shutil.rmtree(hadd_dir)
  if not os.path.isdir(hadd_dir): os.mkdir(hadd_dir)
  summed_multijob = os.path.join(hadd_dir, "fullsum_{}.root".format(os.path.dirname(multijob_dir+'/').replace('Multijob_', '').replace('Job_', '')))
  if multijob_dir.startswith("MultiJob_"):
      multijob_subdirs = os.listdir(multijob_dir)
      summed_files = []
      for subdir in multijob_subdirs:
        if not os.path.isdir(os.path.join(multijob_dir, subdir)): continue
        if subdir == hadd_dir_name: continue
        job_dir = os.path.join(multijob_dir, subdir)
        sys.path.append(os.path.join(multijob_dir, subdir))
        import job_info as job
        output_area = job.output
        sys.path.pop()
        sys.modules.pop("job_info")
        output_list = os.listdir(output_area)
        rootfiles = []
        for item in output_list:
          if not os.path.isfile(os.path.join(output_area, item)): continue
          if not item.endswith(".root"): continue
          rootfiles.append(os.path.join(output_area, item))
        summed_file = os.path.join(hadd_dir, "sum_{}_{}.root".format(os.path.dirname(multijob_dir+'/').replace('MultiJob_', '').replace('Job_', ''), subdir))
        summed_files.append(summed_file)
        command = " ".join(["hadd -f", summed_file, " ".join(rootfiles)])
        if os.path.isfile(summed_file): continue
        os.system(command)
      command = " ".join(["hadd -f", summed_multijob, " ".join(summed_files)])
      if os.path.isfile(summed_multijob): continue
      os.system(command)
      final_sum_filename = args.out if args.out else summed_multijob
      if not args.nomove: os.system("mv -f "+summed_multijob+" ./"+final_sum_filename)
      if not args.retain: shutil.rmtree(hadd_dir)
  elif multijob_dir.startswith("Job_"):
    job_dir = multijob_dir 
    sys.path.append(job_dir)
    import job_info as job
    output_area = job.output
    sys.path.pop()
    sys.modules.pop("job_info")
    output_list = os.listdir(output_area)
    rootfiles = []
    for item in output_list:
      if not os.path.isfile(os.path.join(output_area, item)): continue
      if not item.endswith(".root"): continue
      rootfiles.append(os.path.join(output_area, item))
    summed_file = os.path.join(hadd_dir, "sum.root".format(job_dir))
    command = " ".join(["hadd -f", summed_file, " ".join(rootfiles)])
    if not os.path.isfile(summed_file):
        os.system(command)
    final_sum_filename = args.out if args.out else summed_multijob
    if not args.nomove: os.system("mv -f "+summed_file+" ./"+final_sum_filename)
    if not args.retain: shutil.rmtree(hadd_dir)
