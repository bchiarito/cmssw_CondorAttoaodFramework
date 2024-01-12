#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import imp
import socket
import argparse
from datetime import datetime, timedelta, date
import yaml

parser = argparse.ArgumentParser(description='Executes multiple condor_[submit/status].py commands')
parser.add_argument('input', help='input YAML file to submit, or Job_MultiJob_ directory to check')
parser.add_argument('--test', default=False, action='store_true', help="just print commands, don't execute")
submit_args = parser.add_argument_group("submitting")
submit_args.add_argument('--tag', default="", help="append to 'name' parameter from .yml file")
submit_args.add_argument('--partial', default=False, action='store_true', help="ask before processing each section of the input")
submit_args.add_argument('--manual', default=False, action='store_true', help="manually confirm all submissions")
status_args = parser.add_argument_group("status checking")
status_args.add_argument('--full', default=False, action='store_true', help="don't use --summary")
status_args.add_argument('--hadd', default=False, action='store_true', help="hadd all outputs")
args = parser.parse_args()

# get site
hostname = socket.gethostname()
if 'hexcms' in hostname: site = 'hexcms'
elif 'fnal.gov' in hostname: site = 'cmslpc'
elif 'cern.ch' in hostname: site = 'lxplus'
else: raise SystemExit('ERROR: Unrecognized site: not hexcms, cmslpc, or lxplus')

# check status
if (args.input).startswith("Job_MultiJob") and os.path.exists(args.input):
  dir_list = os.listdir(args.input)
  if args.hadd: summed_files = []
  for subdir in dir_list:
    if not os.path.isdir(os.path.join(args.input, subdir)): continue
    script = "./condor_status.py"
    job_dir = os.path.join(args.input, subdir)
    options = "-s" if not args.full else ""
    command = " ".join([script, job_dir, options])
    print(command)
    if not args.test: os.system(command)
    print('')
    if args.hadd:
      sys.path.append(os.path.join(args.input, subdir))
      import job_info as job
      output_area = job.output
      output_eos = True if output_area[0:7] == '/store/' else False
      print(output_area)
      sys.path.pop()
      sys.modules.pop("job_info")
      if output_eos:
        pass
      else:
        output_list = os.listdir(output_area)
        rootfiles = []
        for item in output_list:
          if not os.path.isfile(os.path.join(output_area, item)): continue
          if not item.endswith(".root"): continue
          rootfiles.append(os.path.join(output_area, item))
        summed_file = "tempsum_{}.root".format(subdir)
        summed_files.append(summed_file)
        command = " ".join(["hadd -f", summed_file," ".join(rootfiles)])
        os.system(command)
      print('')

  if args.hadd:
    summed_job = "sum_{}.root".format(os.path.dirname(args.input+'/')[13:])
    command = " ".join(["hadd -f", summed_job, " ".join(summed_files)])
    os.system(command)
    for temp in summed_files:
      os.remove(temp)
  
  # finished with status mode
  exit()

# submit
with open(args.input) as yaml_input:

  try:
    jobs = yaml.safe_load_all(yaml_input)
  except yaml.YAMLError as err:
    print(err)

  for config in jobs:
    if not config: continue
    try:
      parent_dir = "_".join(["MultiJob", args.tag, config["name"]])
      N_subjobs = len(config["inputs"])
      assert N_subjobs == len(config["dests"]), "ERROR: lists 'inputs' and 'dests' are not the same length in yaml file!"
      print("Job", config["name"], "has", N_subjobs, "subjob(s):\n")
      if args.partial:
        choice = ""
        while (choice != "y" and choice != "n"):
          choice = input("Process? [y/n] ")
        if choice == "n": continue
      if os.path.exists(parent_dir):
        raise SystemExit("ERROR: directory {} already exists!".format(parent_dir))
      else:
        # submit
        for i in range(N_subjobs):
          script = "./condor_submit.py"
          mode = config["mode"]
          job_input = config["inputs"][i]
          job_output = config["dests"][i]
          options = " ".join((config["common_options"]))
          if not args.manual: options += " --auto"
          options += " -x "
          job_dir = "--dir " + "/".join([parent_dir, "subjob_"+str(i+1)])
          command = " ".join([script, mode, job_input, job_output, options, job_dir])
          print(command)
          if not args.test: os.system(command)
          print('')

    except KeyError as err:
      print("ERROR:", err, "expected as key but not found! dumping config:")
      for key in config:
        print("  ", key, ":", config[key])
