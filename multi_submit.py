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
parser.add_argument('tag', help='name of run (atto) or prefix of job directories (plotting)')
parser.add_argument('-t', '--test', action='store_true', help='print command but do not run')
parser.add_argument('-p', '--photon', default='CBL', choices=['HPID', 'CBL'], help='HPID or CBL')
parser.add_argument('-f', '--force', action='store_true', help='delete old job dirs if they exist')
parser.add_argument('--output', help='use in plotting mode, specify output location directory instead of subdirectory of atto output')
parser.add_argument('--fast', action='store_true', help='only 2 files')
args = parser.parse_args()

full_output_path = '/cms/chiarito/eos/twoprong/sanity_plots/atto/' + args.tag # for atto only

if args.mode == 'atto':
  common_options   = [
  '-x',
  '--filesPerJob=60',
  '--scheddLimit=30',
  '--filter="one_either_photon"',
  ]
if args.mode == 'plotting':
  common_options = [
  '--plotter=sanity', 
  '-x',
  '--lumi=59830',
  '--filesPerJob=4',
  '--photon='+args.photon
  ]
if args.force: common_options.append('-f')
if args.fast: common_options.append('--files=2')

locs = {}
if args.mode == 'atto':
  locs['egamma18a'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18a/fv1p4-10-44c4_bv1p1-1-331c/'
  locs['egamma18b'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18b/fv1p4-12-b296_bv1p1-1-331c/'
  locs['egamma18c'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18c/fv1p4-16-9f1a_bv1p1-1-331c/'
  locs['egamma18d'] = '/cms/twoprong/chiarito/nano/egamma/egamma_18d/'
  locs['gjets40to100'] = '/cms/twoprong/chiarito/nano/gjets/gjets40to100/'
  locs['gjets100to200'] = '/cms/twoprong/chiarito/nano/gjets/gjets100to200/fv1p4-23-d5d2_bv1p1-2-3aa0/'
  locs['gjets200to400'] = '/cms/twoprong/chiarito/nano/gjets/gjets200to400/'
  locs['gjets400to600'] = '/cms/twoprong/chiarito/nano/gjets/gjets400to600/fv1p4-15-f8f9_bv1p1-1-331c/'
  locs['gjets600toInf'] = '/cms/twoprong/chiarito/nano/gjets/gjets600toInf/fv1p4-15-f8f9_bv1p1-1-331c/'
  locs['dy50'] = '/cms/twoprong/chiarito/nano/dy/dy_m50/fv1p4-23-d5d2_bv1p1-2-3aa0/'
  locs['wjets'] = '/cms/twoprong/chiarito/nano/wjets/v1p3_plus2_g78bad40_2022-08-18-12-25/'
  locs['ttbar'] = '/cms/twoprong/smd376/2022-06-15-20-08/'
  locs['qcd50to100'] = '/cms/twoprong/chiarito/nano/qcd/qcd50to100/2023-01-17-17-45-30/fv1p4-18-10c5_bv1p1-2-3aa0/'
  locs['qcd100to200'] = '/cms/twoprong/chiarito/nano/qcd/qcd100to200/2023-01-18-13-50-06/fv1p4-19-ee0c_bv1p1-2-3aa0/'
  locs['qcd200to300'] = '/cms/twoprong/chiarito/nano/qcd/qcd200to300/fv1p4-21-62e6_bv1p1-2-3aa0/'
  locs['qcd300to500'] = '/cms/twoprong/chiarito/nano/qcd/qcd300to500/fv1p4-23-d5d2_bv1p1-2-3aa0/'
  locs['qcd500to700'] = '/cms/twoprong/chiarito/nano/qcd/qcd500to700/fv1p5-1-303b_bv1p1-2-3aa0/'
  locs['qcd700to1000'] = '/cms/twoprong/chiarito/nano/qcd/qcd700to1000/fv1p4-19-ee0c_bv1p1-2-3aa0/'
  locs['qcd1000to1500'] = '/cms/twoprong/chiarito/nano/qcd/qcd1000to1500/fv1p4-19-ee0c_bv1p1-2-3aa0/'
  locs['qcd1500to2000'] = '/cms/twoprong/chiarito/nano/qcd/qcd1500to2000/fv1p4-19-ee0c_bv1p1-2-3aa0/'
  locs['qcd2000toInf'] = '/cms/twoprong/chiarito/nano/qcd/qcd2000toInf/'
  locs['signalM125m0p55'] = '/cms/chiarito/rootfiles/signal/SingleM125m0p55-1mil-Apr2023Run2/'
  locs['signalM500meta'] = '/cms/chiarito/rootfiles/signal/NANOAOD_phi_500_omega_eta.root'
  locs['signalM690m1p225'] = '/cms/chiarito/rootfiles/signal/10x10/nano/Phi_690_omega_1p225/2023-06-01-10-45-18/fv1p6-1-f947_bv1p3-0-539a/NANOAOD_v1p3c0_0.root'
  locs['signalM1200m0p5'] = '/cms/chiarito/rootfiles/signal/NANOAOD_phi_1200_omega_0p5.root'
  locs['signalM1280m2p2'] = '/cms/chiarito/rootfiles/signal/10x10/nano/Phi_1280_omega_2p2/2023-06-01-10-44-23/fv1p6-1-f947_bv1p3-0-539a/NANOAOD_v1p3c0_0.root'
  locs['signalM3050m3p175'] = '/cms/chiarito/rootfiles/signal/10x10/nano/Phi_3050_omega_3p175/2023-06-01-10-44-44/fv1p6-1-f947_bv1p3-0-539a/NANOAOD_v1p3c0_0.root'
if args.mode == 'plotting':
  for d in os.listdir('.'):
    if os.path.isdir(d) and d.startswith(args.tag):
      tag = d[d.rfind('_')+1:]
      locs[tag] = d

add_job(tag='egamma18a', options='--data --datasetname=egamma18a', loc=locs['egamma18a'])
add_job(tag='egamma18b', options='--data --datasetname=egamma18b', loc=locs['egamma18b'])
add_job(tag='egamma18c', options='--data --datasetname=egamma18c', loc=locs['egamma18c'])
add_job(tag='egamma18d', options='--data --datasetname=egamma18d --scheddLimit=60', loc=locs['egamma18d'])
add_job(tag='gjets40to100', options='--mc --xs=18650 --datasetname=gjets40to100', loc=locs['gjets40to100'])
add_job(tag='gjets100to200', options='--mc --xs=8639 --datasetname=gjets100to200', loc=locs['gjets100to200'])
add_job(tag='gjets200to400', options='--mc --xs=2173 --datasetname=gjets200to400', loc=locs['gjets200to400'])
add_job(tag='gjets400to600', options='--mc --xs=260.7 --datasetname=gjets400to600', loc=locs['gjets400to600'])
add_job(tag='gjets600toInf', options='--mc --xs=86.55 --datasetname=gjets600toInf', loc=locs['gjets600toInf'])
add_job(tag='dy50', options='--mc --xs=6077 --datasetname=dy50', loc=locs['dy50'])
add_job(tag='wjets', options='--mc --xs=61526.7 --datasetname=wjets', loc=locs['wjets'])
add_job(tag='ttbar', options='--mc --xs=831.76 --datasetname=ttbar', loc=locs['ttbar'])
add_job(tag='qcd50to100', options='--mc --xs=187700000.0 --datasetname=qcd50to100', loc=locs['qcd50to100'])
add_job(tag='qcd100to200', options='--mc --xs=23500000.0 --datasetname=qcd100to200', loc=locs['qcd100to200'])
add_job(tag='qcd200to300', options='--mc --xs=1552000.0 --datasetname=qcd200to300', loc=locs['qcd200to300'])
add_job(tag='qcd300to500', options='--mc --xs=321100.0 --datasetname=qcd300to500', loc=locs['qcd300to500'])
add_job(tag='qcd500to700', options='--mc --xs=30250.0 --datasetname=qcd500to700', loc=locs['qcd500to700'])
add_job(tag='qcd700to1000', options='--mc --xs=6398.0 --datasetname=qcd700to1000', loc=locs['qcd700to1000'])
add_job(tag='qcd1000to1500', options='--mc --xs=1122.0 --datasetname=qcd1000to1500', loc=locs['qcd1000to1500'])
add_job(tag='qcd1500to2000', options='--mc --xs=109.4 --datasetname=qcd1500to2000', loc=locs['qcd1500to2000'])
add_job(tag='qcd2000toInf', options='--mc --xs=21.74 --datasetname=qcd2000toInf', loc=locs['qcd2000toInf'])
add_job(tag='signalM125m0p55', options='--sigRes --xs=202.315 --datasetname=signalM125m0p55 --branches branch_selection_atto_signal.txt', loc=locs['signalM125m0p55'])
add_job(tag='signalM690m1p225', options='--sigRes --xs=80.292484 --datasetname=signalM690m1p225 --branches branch_selection_atto_signal.txt', loc=locs['signalM690m1p225'])
add_job(tag='signalM1280m2p2', options='--sigRes --xs=2.3405524 --datasetname=signalM1280m2p2 --branches branch_selection_atto_signal.txt', loc=locs['signalM1280m2p2'])
add_job(tag='signalM3050m3p175', options='--sigRes --xs=.00439953 --datasetname=signalM3050m3p175 --branches branch_selection_atto_signal.txt', loc=locs['signalM3050m3p175'])

for job in jobs:
  command = './condor_submit.py ' + args.mode
  if args.mode == 'atto': output = full_output_path + '/' + job['tag']
  if args.mode == 'plotting':
    if not args.output: output = '-'
    else: output = args.output
  command = command + ' ' + job['input'] + ' ' + output
  for option in common_options:
    command = command + ' ' + option
  for option in job['options']:
    command = command + ' ' + option
  command += ' '
  if args.mode == 'atto': command += ' --dir='+args.tag+'_'+job['tag']
  if args.output: command += ' --dir='+args.tag+'plotting_'+job['tag']
  command += ' --auto'
  print('\n'+command+'\n')
  if not args.test: os.system(command)
