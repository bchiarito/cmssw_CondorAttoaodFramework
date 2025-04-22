#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import argparse
from functools import reduce
import shutil
import constants as const
import ROOT
import helper.plotting_util as util

# ./hadd_and_scale <type> <multijob_dir>

# command line options
parser = argparse.ArgumentParser(description="")
parser.add_argument("type", help='')
parser.add_argument("jobdirs", nargs='+', help='MultiJob_ dir')
parser.add_argument("-y", "--year", help='')
parser.add_argument("-o", "--out", help='')
parser.add_argument("--rehadd", action='store_true', default=False, help='')
parser.add_argument("--retain", action='store_true', default=False, help='')
args = parser.parse_args()

# constants
hadd_dir_name = "hadd"

# init
job_dirs = []
for jobdir in args.jobdirs: job_dirs.append(jobdir)

# hadd
for multijob_dir in job_dirs:
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
      os.system("mv -f "+summed_multijob+" ./"+final_sum_filename)
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
    final_sum_filename = args.out if args.out else "out.root"
    os.system("mv -f "+summed_file+" ./"+final_sum_filename)
    if not args.retain: shutil.rmtree(hadd_dir)



if not args.type == 'data':
    xs = const.xses[args.type]
    ngen = const.ngen[args.type + args.year]
    lumi = const.lumi[args.year]
    xs_and_lumi_scale = xs * lumi / ngen
    print(xs_and_lumi_scale)
else:
    xs_and_lumi_scale = 1.0

final_file = ROOT.TFile(final_sum_filename, "READ")
hists = [key.ReadObj() for key in final_file.GetListOfKeys()[0].ReadObj().GetListOfKeys()]

outfile = ROOT.TFile("scaled_"+final_sum_filename, "RECREATE")
outfile.cd()
for hist in hists:
    hist.Scale(xs_and_lumi_scale)
    hist.Write()
