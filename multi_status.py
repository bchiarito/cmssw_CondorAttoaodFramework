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
for d in os.listdir('.'):
  if os.path.isdir(d) and d.startswith(args.prefix):
    if not args.plots: command = './condor_status.py -s '+d
    else: command = './condor_status.py -s '+d+'/plotting_jobs/'
    print('>>> '+command)
    os.system(command)
    print()

sys.exit()

## mc must have --numJobs=1
add_job(tag='egamma18a', options='--data --filesPerJob=20',
        loc=locs['egamma18a'])
add_job(tag='egamma18b', options='--data --filesPerJob=20',
        loc=locs['egamma18b'])
add_job(tag='egamma18c', options='--data --filesPerJob=20',
        loc=locs['egamma18c'])
add_job(tag='egamma18d', options='--data --filesPerJob=20',
        loc=locs['egamma18d'])
add_job(tag='gjets40to100', options='--mc --numJobs=1',
        loc=locs['gjets40to100'])
add_job(tag='gjets100to200', options='--mc --numJobs=1',
        loc=locs['gjets100to200'])
add_job(tag='gjets200to400', options='--mc --numJobs=1',
        loc=locs['gjets200to400'])
add_job(tag='gjets400to600', options='--mc --numJobs=1',
        loc=locs['gjets400to600'])
add_job(tag='gjets600toInf', options='--mc --numJobs=1',
        loc=locs['gjets600toInf'])

for job in jobs:
  command = './condor_status.py '
  #command = command + ' ' + job['input'] + ' ' + full_output_path+job['tag']
  command = command + ' ' + job['input'] + ' -'
  for option in job['options']:
    command = command + ' ' + option
  command += ' '
  for option in common_options:
    command = command + ' ' + option
  #command += ' --dir='+jobdir_prefix+job['tag']
  command += ' --auto'
  print(command+'\n')
  if not args.test: os.system(command)
