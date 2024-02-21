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
parser.add_argument('mode', choices=['atto', 'histo', 'status'], help='')
parser.add_argument('-i', '--input', nargs='+', help='any number of input YAML files or Job_MultiJob_XXX directories')
parser.add_argument('-t', '--test', default=False, action='store_true', help="just print commands, don't execute")
submit_args = parser.add_argument_group("atto mode")
submit_args.add_argument('--name', default=None, help="append to 'name' parameter from .yml file")
submit_args.add_argument('--intag', default=None, help="use in place of IN_TAG in .yml file")
submit_args.add_argument('--manual', default=False, action='store_true', help="ask before processing each section of the input")
submit_args.add_argument('--fullmanual', default=False, action='store_true', help="manually confirm all submissions")
submit_args.add_argument('-f', '--force', default=False, action='store_true', help="add -f option")
status_args = parser.add_argument_group("status mode")
status_args.add_argument('--full', default=False, action='store_true', help="don't use --summary")
status_args.add_argument('--hadd', default=False, action='store_true', help="hadd all outputs")
args = parser.parse_args()

# constants
IN_TAG = "<IN_TAG>"
hadd_dir_name = "hadd"

# get site
hostname = socket.gethostname()
if 'hexcms' in hostname: site = 'hexcms'
elif 'fnal.gov' in hostname: site = 'cmslpc'
elif 'cern.ch' in hostname: site = 'lxplus'
else: raise SystemExit('ERROR: Unrecognized site: not hexcms, cmslpc, or lxplus')

# init
if not args.name and args.intag: args.name = args.intag

# main
if args.mode == 'status':
  for in_dir in args.input:
    if not in_dir.startswith("Job_MultiJob"): continue
    dir_list = os.listdir(in_dir)
    if args.hadd: summed_files = []
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
      if args.hadd:
        sys.path.append(os.path.join(in_dir, subdir))
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
          summed_file = "sum_{}_{}.root".format(os.path.dirname(in_dir+'/')[13:], subdir)
          summed_files.append(summed_file)
          command = " ".join(["hadd -f", summed_file," ".join(rootfiles)])
          os.system(command)
        print('')

    if args.hadd:
      summed_job = "sum_{}.root".format(os.path.dirname(in_dir+'/')[13:])
      command = " ".join(["hadd -f", summed_job, " ".join(summed_files)])
      os.system(command)
      #for temp in summed_files:
      #  os.remove(temp)
    
if args.mode == 'histo':
  for in_dir in args.input:
    if not in_dir.startswith("Job_MultiJob"): continue

    #if args.name: parent_dir = "_".join(["MultiJob", args.name, ""])
    #else: parent_dir = "_".join(["MultiJob", config["name"]])
    parent_dir = in_dir.replace("atto", "histo")[4:]
    if os.path.exists(parent_dir):
      raise SystemExit("ERROR: directory {} already exists!".format(parent_dir))

    # loop over jobdirs inside multijob
    dir_list = os.listdir(in_dir)
    for subdir in dir_list:
      print(subdir)
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

      script = "./condor_submit.py"
      mode = "plotting"
      job_input = output_area
      job_output = "-" #config["dest"] + (args.name if args.name else "") + config["dests"][i]
      datamc = "--mc"
      lumi = "--lumi=59830"
      year = "--year=UL18"
      options = " ".join([datamc, lumi, "--plotter=sanity", "--photon=CBL220", "--filesPerJob=4", year])
      if not args.fullmanual: options += " --auto"
      if args.force: options += " --force"
      options += " -x"
      job_dir = "--dir " + "/".join([parent_dir, subdir])
      command = " ".join([script, mode, job_input, job_output, options, job_dir])
      print(command)
      if not args.test: os.system(command)
      print('')

if args.mode == 'atto':
  with open(args.input[0]) as yaml_input:
    try:
      jobs = yaml.safe_load_all(yaml_input)
    except yaml.YAMLError as err:
      print(err)

    for config in jobs:
      if not config: continue
      try:
        if args.name: parent_dir = "_".join(["MultiJob", args.name, config["name"]])
        else: parent_dir = "_".join(["MultiJob", config["name"]])
        N_subjobs = len(config["inputs"])
        assert N_subjobs == len(config["dests"]), "ERROR: lists 'inputs' and 'dests' are not the same length in yaml file!"
        print("Job", config["name"], "has", N_subjobs, "subjob(s):\n")
        if args.manual:
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
            if IN_TAG in job_input:
              if args.intag: job_input = job_input.replace(IN_TAG, args.intag)
              else: raise SystemExit("ERROR: yaml contains {} but no option --intag specified!".format(IN_TAG))
            job_output = config["dest"] + (args.name if args.name else "") + config["dests"][i]
            if args.name: job_output = "/".join([config["dest"], args.name, config["dests"][i]])
            else: job_output = "/".join([config["dest"], config["dests"][i]])
            job_output = os.path.normpath(job_output)
            options = " ".join((config["common_options"]))
            if "options" in config:
              options += " " + " ".join(config["options"][i])
            if not args.fullmanual: options += " --auto"
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

else:
  pass
