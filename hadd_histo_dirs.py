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
parser = argparse.ArgumentParser(description="Makes pdf from histo job directories")
parser.add_argument("multidirs", nargs='+', help='DATA MC1 MC2 ...')
parser.add_argument("--names", nargs='+', help='')
parser.add_argument("--signal", help='multijobdir')
parser.add_argument("--signalnames", nargs='+', help='multijobdir')
parser.add_argument("-r", "--rehadd", action='store_true', help='rebuild hadds')
parser.add_argument("-g", "--gjets_scale_up", action='store_true', help='scale gjets up to data')
parser.add_argument("--nosanity", action='store_true', help='omit sanity plots')
parser.add_argument("--trigger_eff", action='store_true', help='display trigger efficiencies')
parser.add_argument("--signalplots", action='store_true', help='add signal plots')
parser.add_argument("--cutflow", action='store_true', help='add cutflow plots')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
parser.add_argument("--saveroot", default=False, action='store_true', help='store .root and .cpp files for plots')
parser.add_argument("-t", "--test", default=False, action='store_true', help='only one plot')
args = parser.parse_args()

# constants
hadd_dir_name = "hadd"
main_pdf = args.out+'_main.pdf'
cutflow_pdf = args.out+'_cutflow.pdf'
signal_pdf = args.out+'_signal.pdf'
leg_x1, leg_y1, leg_x2, leg_y2 = 0.7, 0.60, 0.89, 0.9
signal_tag = 'SIGNAL_'
data_color = ROOT.kBlack
signal_color = [ROOT.kRed, ROOT.kRed+1, ROOT.kBlue, ROOT.kBlue+1, ROOT.kPink, ROOT.kPink+1]
mccolors = [ROOT.kOrange, ROOT.kGreen, ROOT.kYellow+1, ROOT.kViolet, ROOT.kTeal]

# init
mc_filenames_list = []
mc_color = []
mc_legend = []
mc_hat_tag = []
mc_hist_collections = []
mc_hists_collections = []
mc_tfiles_collection = []
signal_legend = []
signal_hist_collections = []
signal_hists_collections = []
signal_tfiles_collection = []
GJETS_POSITION = 1
if args.names:
  data_legend = args.names[0]
  mcnames = args.names[1:]
else:
  data_legend = 'DATA'
  mcnames = ['MC1', 'MC2', 'MC3', 'MC4', 'MC5', 'MC6', 'MC7']
multijob_dirs = []
for multidir in args.multidirs: multijob_dirs.append(multidir)
if args.signal: multijob_dirs.append(args.signal)
signalnames = ['sig1', 'sig2', 'sig3']

# hadd if necessary
for multijob_dir in multijob_dirs:
  if not os.path.isdir(multijob_dir): continue
  hadd_dir = os.path.join(multijob_dir, hadd_dir_name)
  if not os.path.isdir(hadd_dir): os.mkdir(hadd_dir)
  summed_multijob = os.path.join(hadd_dir, "fullsum_{}.root".format(os.path.dirname(multijob_dir+'/')[13:]))
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
    summed_file = os.path.join(hadd_dir, "sum_{}_{}.root".format(os.path.dirname(multijob_dir+'/')[13:], subdir))
    summed_files.append(summed_file)
    command = " ".join(["hadd -f", summed_file, " ".join(rootfiles)])
    if os.path.isfile(summed_file): continue
    os.system(command)
  command = " ".join(["hadd -f", summed_multijob, " ".join(summed_files)])
  if os.path.isfile(summed_multijob): continue
  os.system(command)
  os.system("mv "+summed_multijob+" .")
  shutil.rmtree(hadd_dir)
