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

parser = argparse.ArgumentParser(description='Executes multiple condor_[submit/status].py commands')
parser.add_argument('mode', choices=['atto', 'histo', 'status'], help='operation mode')
parser.add_argument('input', nargs='+', help='any number of YAML files or MultiJob_ directories or rootfile directories')
parser.add_argument('--askall', default=False, action='store_true', help="confirm all command execution")
parser.add_argument('-f', '--force', default=False, action='store_true', help=argparse.SUPPRESS)
parser.add_argument('-t', '--test', default=False, action='store_true', help=argparse.SUPPRESS)
parser.add_argument('--quick', default=False, action='store_true', help='only one file per job')
parser.add_argument('--runname', default="Run-"+date.today().strftime("%b-%d-%Y"), help="not used in 'histo' mode if input is atto MultiJob dir")
atto_args = parser.add_argument_group("atto mode")
atto_args.add_argument('-c', '--config', help='file for options when input is directory of nano rootfiles')
histo_args = parser.add_argument_group("histo mode")
histo_args.add_argument('-y', '--year', default='18', choices=['18', '17', '16'], help='')
histo_args.add_argument('--lumi', default=None, help='if using non-official lumi')
histo_args.add_argument('--outdir', help='instead of default "-"')
histo_args.add_argument('--subtag', default=None, help='optional extra ending for jobdir and outdir')
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
elif args.mode == "histo": raise SystemExit("Missing Option: Specification of --data / --mc / --sigRes / --sigNonRes required for 'histo' mode!")
else: pass

# constants
hadd_dir_name = "hadd"

# init
hostname = socket.gethostname()
if 'hexcms' in hostname: site = 'hexcms'
elif 'fnal.gov' in hostname: site = 'cmslpc'
elif 'cern.ch' in hostname: site = 'lxplus'
else: raise SystemExit('ERROR: Unrecognized site: not hexcms, cmslpc, or lxplus')

def gettag(path):
    i = path.rindex('/')
    return path[i+1:]

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
    if in_dir.startswith("Job_"): subdirs = [in_dir]
    else: subdirs = os.listdir(in_dir)

    for subdir in subdirs:
      if not os.path.isdir(os.path.join(in_dir, subdir)): continue
      if subdir == hadd_dir_name: continue
      if in_dir.startswith("MultiJob_"):
          job_dir_parent = in_dir.replace('/','')+"_HistoMode"
          if args.subtag: job_dir_parent+="_"+args.subtag
          # get output area of atto input from jobdir
          sys.path.append(os.path.join(in_dir, subdir))
          import job_info as job
          output_area = job.output
          output_eos = True if output_area[0:7] == '/store/' else False
          if output_eos: pass
          sys.path.pop()
          sys.modules.pop("job_info")
          job_input = output_area
      elif in_dir.startswith("Job_"): 
          job_dir_parent = in_dir.replace('/','')+"_HistoMode"
          if args.subtag: job_dir_parent+="_subtag"
          # get output area of atto input from jobdir
          sys.path.append(os.path.join(in_dir, subdir))
          import job_info as job
          output_area = job.output
          output_eos = True if output_area[0:7] == '/store/' else False
          if output_eos: pass
          sys.path.pop()
          sys.modules.pop("job_info")
          job_input = output_area
      else:
          job_dir_parent = "_".join(["MultiJob", "-".join([args.runname, "HistoMode"])])
          job_input = os.path.normpath(os.path.join(in_dir, subdir))
          if 'GenericMultirun-' in args.runname:
            args.runname = (in_dir.replace('/',''))+"-"+date.today().strftime("%b-%d-%Y")

      # prepare command
      script = "./condor_submit.py"
      mode = "plotting"
      job_output = args.outdir if args.outdir else "-"
      if args.year=="18":
        photon_str = "CBL220"
        #lumi_str = "59830" # https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2
      elif args.year=="17":
        photon_str = "CBL220"
        #lumi_str = "41480"
      elif args.year=="16":
        photon_str = "CBL185"
        #lumi_str = "36310"
      else:
        photon_str = "CBL"
        #lumi_str = "1"
      #if args.lumi: lumi_str = str(args.lumi)
      #lumi = "--lumi=" + lumi_str
      year = "--year=UL" + args.year
      datamc = "--" + datamc_str
      options = " ".join([datamc, "--plotter=zttplot", "--photon="+photon_str, "--filesPerJob=10", "--scheddLimit=30", year])
      if not args.askall: options += " --auto"
      if args.force: options += " --force"
      options += " -x"
      job_dir = "--dir " + "/".join([job_dir_parent, subdir])
      command = " ".join([script, mode, job_input, job_output, options, job_dir])
      print(command)
      if not args.test: os.system(command)
      print('')

    if not args.test:
      with open(os.path.join(job_dir_parent, "blank.txt"), 'w') as logfile:
        logfile.write(reduce(lambda t1, t2 : t1+" "+t2, sys.argv, ""))

if args.mode == 'atto':

  for input_item in args.input:
    if input_item.endswith(".yml"):

        with open(input_item) as yaml_input:
          try:
            jobs = yaml.safe_load_all(yaml_input)
          except yaml.YAMLError as err:
            print(err)
          for config in jobs:
            if not config: continue
            try:
              parent_dir = "_".join(["MultiJob", "-".join([args.runname, config["name"]])])
              if 'top_level_input' in config:
                top_level_input = config['top_level_input']
                inputs = []
                for subdir in os.listdir(top_level_input): inputs.append(subdir)
              else: inputs = config["inputs"]
              N_subjobs = len(inputs)
              assert N_subjobs == len(config["dests"]), "ERROR: lists 'inputs' and 'dests' are not the same length in yaml file!"
              print("Section", config["name"], "of YAML fie has", N_subjobs, "job(s):\n")
              choice = ""
              while (choice != "y" and choice != "n" and choice != "q"):
                choice = input("Proceed? [y/n/q] ")
              if choice == "q": exit()
              if choice == "n": continue
              #if os.path.exists(parent_dir):
              #  raise SystemExit("ERROR: directory {} already exists!".format(parent_dir))
              #else:
              # submit
              for i in range(N_subjobs):
                  script = "./condor_submit.py"
                  if "" in config: mode = config["mode"]
                  else: mode = "atto"
                  job_input = inputs[i]
                  #job_output = "/".join([config["dest"], "-".join([args.runname, config["name"]]), config["dests"][i]])
                  job_output = "/".join([config["dests"][i], "-".join([args.runname, config["name"]])])
                  job_output = os.path.normpath(job_output)
                  options = " ".join((config["options"]))
                  if "extra_options" in config:
                    options += " " + " ".join(config["extra_options"][i])
                  if not args.askall: options += " --auto"
                  if args.force: options += " --force"
                  if args.quick: options += " --files=1"
                  options += " -x"
                  tag = gettag(config["dests"][i])
                  job_dir = "--dir " + "/".join([parent_dir, tag])
                  command = " ".join([script, mode, job_input, job_output, options, job_dir])
                  print(command)
                  if not args.test: os.system(command)
                  print('')
            except KeyError as err:
              print("ERROR:", err, "expected as key but not found! dumping config:")
              for key in config:
                print("  ", key, ":", config[key])

    else:
      print("not yaml")
      subdirs = os.listdir(input_item)
      numjobs = len(subdirs)
      script = "./condor_submit.py"
      mode = 'atto'
      for i, subdir in enumerate(subdirs):
          if not args.config:
            config = {}
            config["output"] = [ "/cms/chiarito/eos/test/subjob"+str(j) for j in range(numjobs)]
            config["jobdir"] = [ "MultiJob_PlaceHolder/subjob"+str(j) for j in range(numjobs)]
            config["options"] = [["--files=2 --year=UL18 --sigRes -a=main"]] * numjobs
          else:
            print("get from config file")
          job_input = os.path.join(input_item, subdir)
          job_output = config["output"][i]
          job_dir = "--dir " + config["jobdir"][i]
          options = " ".join(config["options"][i])
          if not args.askall: options += " --auto"
          if args.force: options += " --force"
          options += " -x"
          command = " ".join([script, mode, job_input, job_output, options, job_dir])
          print(command)
          if not args.test: os.system(command)
          print('')
