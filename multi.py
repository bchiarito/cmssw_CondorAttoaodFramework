#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import socket
import argparse
from datetime import datetime, timedelta, date
import yaml

parser = argparse.ArgumentParser(description='Executes multiple condor_[submit/status].py commands')
parser.add_argument('mode', choices=['yaml', 'histo', 'status'], help='operation mode')
parser.add_argument('input', nargs='+', help='any number of input YAML files or Job_MultiJob_XXX directories')
parser.add_argument('--manual', default=False, action='store_true', help="confirm all command execution")
parser.add_argument('-f', '--force', default=False, action='store_true', help=argparse.SUPPRESS)
parser.add_argument('-t', '--test', default=False, action='store_true', help=argparse.SUPPRESS)
yaml_args = parser.add_argument_group("yaml mode")
yaml_args.add_argument('--runname', default='RUN', help="append to 'name' parameter from .yml file")
yaml_args.add_argument('--partial', default=False, action='store_true', help="ask before processing each section of the input")
histo_args = parser.add_argument_group("histo mode")
histo_args.add_argument('--year', default='18', choices=['18', '17', '16'], help='')
histo_args.add_argument('--lumi', default=None, help='')
status_args = parser.add_argument_group("status mode")
status_args.add_argument('--full', default=False, action='store_true', help="don't use --summary")
datamc_args = parser.add_mutually_exclusive_group()
datamc_args.add_argument("--data", action="store_true", default=False, help=argparse.SUPPRESS)
datamc_args.add_argument("--mc", action="store_true", default=False, help=argparse.SUPPRESS)
datamc_args.add_argument("--sigRes", action="store_true", default=False, help=argparse.SUPPRESS)
datamc_args.add_argument("--sigNonRes", action="store_true", default=False, help=argparse.SUPPRESS)
args = parser.parse_args()

# check data/mc
if args.mc: datamc_str = "mc"
elif args.data: datamc_str = "data"
elif args.sigRes: datamc_str = "sigRes"
elif args.sigNonRes: datamc_str = "sigNonRes"
else:
  if args.mode == "histo": raise SystemExit("Missing Option: Specification of --data / --mc / --sigRes / --sigNonRes required!")
  else: datamc_str = "data"

# constants
hadd_dir_name = "hadd"

# init
hostname = socket.gethostname()
if 'hexcms' in hostname: site = 'hexcms'
elif 'fnal.gov' in hostname: site = 'cmslpc'
elif 'cern.ch' in hostname: site = 'lxplus'
else: raise SystemExit('ERROR: Unrecognized site: not hexcms, cmslpc, or lxplus')

# main
if args.mode == 'status':

  for in_dir in args.input:
    if not in_dir.startswith("MultiJob"): continue
    dir_list = os.listdir(in_dir)
    for subdir in dir_list:
      if not os.path.isdir(os.path.join(in_dir, subdir)): continue
      if subdir == hadd_dir_name: continue
      script = "./condor_status.py"
      job_dir = os.path.join(in_dir, subdir)
      options = "-s" if not args.full else ""
      command = " ".join([script, job_dir, options])
      print(command)
      if not args.test: os.system(command)
      print('')
    
if args.mode == 'histo':

  for in_dir in args.input:
    if not in_dir.startswith("MultiJob"): continue
    if not "atto" in in_dir: raise SystemExit('ERROR: source directories must contain pattern "atto"')
    parent_dir = in_dir.replace("atto", "histo")
    #if os.path.exists(parent_dir):
    #  raise SystemExit("ERROR: directory {} already exists!".format(parent_dir)) # I think this is a bug, delete this check
    # loop over jobdirs inside multijob
    dir_list = os.listdir(in_dir)
    for subdir in dir_list:
      if not os.path.isdir(os.path.join(in_dir, subdir)): continue
      if subdir == hadd_dir_name: continue
      # get output area of atto input from jobdir
      sys.path.append(os.path.join(in_dir, subdir))
      import job_info as job
      output_area = job.output
      output_eos = True if output_area[0:7] == '/store/' else False
      if output_eos: pass
      sys.path.pop()
      sys.modules.pop("job_info")
      # prepare command
      script = "./condor_submit.py"
      mode = "plotting"
      job_input = output_area
      job_output = "-"
      if args.year=="18":
        photon_str = "CBL220"
        lumi_str = "59830" # https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
      elif args.year=="17":
        photon_str = "CBL220"
        lumi_str = "41480"
      elif args.year=="16":
        photon_str = "CBL185"
        lumi_str = "36310"
      else:
        photon_str = "CBL"
        lumi_str = "1"
      if args.lumi: lumi_str = str(args.lumi)
      lumi = "--lumi=" + lumi_str
      year = "--year=UL" + args.year
      datamc = "--" + datamc_str
      options = " ".join([datamc, lumi, "--plotter=sanity", "--photon="+photon_str, "--filesPerJob=4", year])
      if not args.manual: options += " --auto"
      if args.force: options += " --force"
      options += " -x"
      job_dir = "--dir " + "/".join([parent_dir, subdir])
      command = " ".join([script, mode, job_input, job_output, options, job_dir])
      print(command)
      if not args.test: os.system(command)
      print('')

if args.mode == 'yaml':

  for yaml_file in args.input:
    with open(yaml_file) as yaml_input:
      try:
        jobs = yaml.safe_load_all(yaml_input)
      except yaml.YAMLError as err:
        print(err)
      for config in jobs:
        if not config: continue
        try:
          parent_dir = "_".join(["MultiJob", config["name"], args.runname])
          N_subjobs = len(config["inputs"])
          assert N_subjobs == len(config["dests"]), "ERROR: lists 'inputs' and 'dests' are not the same length in yaml file!"
          print("Job", config["name"], "has", N_subjobs, "subjob(s):\n")
          if args.partial:
            choice = ""
            while (choice != "y" and choice != "n" and choice != "q"):
              choice = raw_input("Process? [y/n/q] ")
            if choice == "q": exit()
            if choice == "n": continue
          if os.path.exists(parent_dir):
            raise SystemExit("ERROR: directory {} already exists!".format(parent_dir))
          else:
            # submit
            for i in range(N_subjobs):
              script = "./condor_submit.py"
              mode = config["mode"]
              job_input = config["inputs"][i]
              job_output = "/".join([config["dest"], args.runname, config["dests"][i]])
              job_output = os.path.normpath(job_output)
              options = " ".join((config["common_options"]))
              if "options" in config:
                options += " " + " ".join(config["options"][i])
              if not args.manual: options += " --auto"
              if args.force: options += " --force"
              options += " -x"
              job_dir = "--dir " + "/".join([parent_dir, os.path.normpath(config["dests"][i]).replace("/","-")])
              command = " ".join([script, mode, job_input, job_output, options, job_dir])
              print(command)
              if not args.test: os.system(command)
              print('')
        except KeyError as err:
          print("ERROR:", err, "expected as key but not found! dumping config:")
          for key in config:
            print("  ", key, ":", config[key])
