#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import imp
import argparse
from datetime import datetime, timedelta, date

jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

parser = argparse.ArgumentParser(description='Executes multiple condor_submit.py commands, configuration inside script')
parser.add_argument('mode', choices=['atto', 'plotting'], help='atto or plotting')
parser.add_argument('--prefix', required='plotting' in sys.argv, help='match condition when running plotting step')
parser.add_argument('-t', '--test', action='store_true', help='print command but do not run')
parser.add_argument('-f', '--force', action='store_true', help='delete old job dirs if they exist')
parser.add_argument('--fast', action='store_true', help='only 2 files')
parser.add_argument('-d', '--dir', default='mutlirun_'+date.today().strftime("%b-%d-%Y"), help='for atto, name for job directories')
args = parser.parse_args()

# for atto
full_output_path = '/cms/chiarito/eos/twoprong/sanity_plots/atto/' + args.dir

if args.mode == 'atto':
  common_options = [
  '--lumi=59830',
  '--filesPerJob=1',
  ]
if args.mode == 'plotting':
  common_options   = [
  '--filesPerJob=20',
  '--scheddLimit=100',
  '--filter="one_hpid_photon"',
  '--recophiphoton=HPID',
  ]
if args.force: common_options.append('-f')
if args.fast: common_options.append('--files=2')

locs = {}
if args.mode == 'atto':
  locs['egamma18a'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18a/fv1p4-10-44c4_bv1p1-1-331c/'
  locs['egamma18b'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18b/fv1p4-12-b296_bv1p1-1-331c/'
  locs['egamma18c'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18c/fv1p4-16-9f1a_bv1p1-1-331c/'
  locs['egamma18d'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18d/'
  locs['gjets40to100'] = '/cms/twoprong/chiarito/nano/gjets-10percent/gjets40to100/'
  locs['gjets100to200'] = '/cms/twoprong/chiarito/nano/gjets-10percent/gjets100to200/'
  locs['gjets200to400'] = '/cms/twoprong/chiarito/nano/gjets-10percent/gjets200to400/'
  locs['gjets400to600'] = '/cms/twoprong/chiarito/nano/gjets-10percent/gjets400to600/'
  locs['gjets600toInf'] = '/cms/twoprong/chiarito/nano/gjets-10percent/gjets600toInf/'
if args.mode == 'plotting':
  for d in os.listdir('.'):
    if os.path.isdir(d) and d.startswith(args.prefix):
      tag = d[d.rfind('_')+1:]
      locs[tag] = d

add_job(tag='egamma18a', options='--data --datasetname=egamma18a', loc=locs['egamma18a'])
add_job(tag='egamma18b', options='--data --datasetname=egamma18b', loc=locs['egamma18b'])
add_job(tag='egamma18c', options='--data --datasetname=egamma18c', loc=locs['egamma18c'])
add_job(tag='egamma18d', options='--data --datasetname=egamma18d', loc=locs['egamma18d'])
add_job(tag='gjets40to100', options='--mc --xs=20810 --datasetname=gjets40to100', loc=locs['gjets40to100'])
add_job(tag='gjets100to200', options='--mc --xs=9223 --datasetname=gjets100to200', loc=locs['gjets100to200'])
add_job(tag='gjets200to400', options='--mc --xs=2303 --datasetname=gjets200to400', loc=locs['gjets200to400'])
add_job(tag='gjets400to600', options='--mc --xs=274.5 --datasetname=gjets400to600', loc=locs['gjets400to600'])
add_job(tag='gjets600toInf', options='--mc --xs=93.52 --datasetname=gjets600toInf', loc=locs['gjets600toInf'])

for job in jobs:
  command = './condor_submit.py ' + args.mode
  if args.mode == 'atto': output = full_output_path + '/' + job['tag']
  if args.mode == 'plotting': output = '-'
  command = command + ' ' + job['input'] + ' ' + output
  for option in job['options']:
    command = command + ' ' + option
  command += ' '
  for option in common_options:
    command = command + ' ' + option
  if args.mode == 'atto': command += ' --dir='+args.dir+'_'+job['tag']
  command += ' --auto'
  print('\n'+command+'\n')
  if not args.test: os.system(command)
