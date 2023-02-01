from __future__ import print_function
jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

##############################################################################

output_dir       = 'dev_testing'
job_tag          = 'fullrun_2'
common_options   = [
'--lumi=59830'
]
jobdir_prefix    = job_tag + '_'
full_output_path = '/cms/chiarito/atto_plotting/' + output_dir + '/' + job_tag

## mc must have --numJobs=1
add_job(tag='egamma18a', options='--data --filesPerJob=10 --input_cmslpc',
        loc='/store/user/bchiari1/atto/datamc_full/egamma18a/2023-01-16-21-15-25/fd_bd')
add_job(tag='egamma18b', options='--data --input_cmslpc --datasetname=egamma18b --filesPerJob=25',
        loc='/store/user/bchiari1/atto/datamc_full/egamma18b/2023-01-16-21-15-28/fd_bd')
add_job(tag='egamma18c', options='--data --input_cmslpc --datasetname=egamma18c --filesPerJob=25',
        loc='/store/user/bchiari1/atto/datamc_full/egamma18c/2023-01-16-21-15-29/fd_bd')
add_job(tag='egamma18d', options='--data --datasetname=egamma18d --filesPerJob=1000',
        loc='/cms/chiarito/rootfiles/atto/egamma_18d')
add_job(tag='gjets40to100', options='--mc --input_cmslpc --numJobs=1',
        loc='/store/user/bchiari1/atto/datamc_full/gjets40to100/2023-01-16-21-15-30/fd_bd')
add_job(tag='gjets100to200', options='--mc --input_cmslpc --numJobs=1',
        loc='/store/user/bchiari1/atto/datamc_full/gjets100to200/2023-01-16-21-15-31/fd_bd')
add_job(tag='gjets200to400', options='--mc --input_cmslpc --numJobs=1',
        loc='/store/user/bchiari1/atto/datamc_full/gjets200to400/2023-01-16-21-15-31/fd_bd')
add_job(tag='gjets400to600', options='--mc --input_cmslpc --numJobs=1',
        loc='/store/user/bchiari1/atto/datamc_full/gjets400to600/2023-01-16-21-15-32/fd_bd')
add_job(tag='gjets600toInf', options='--mc --input_cmslpc --numJobs=1',
        loc='/store/user/bchiari1/atto/datamc_full/gjets600toInf/2023-01-16-21-15-32/fd_bd')

##############################################################################

import os
import argparse
parser = argparse.ArgumentParser(description='Executes multiple condor_submit.py commands, configuration inside script')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

for job in jobs:
  command = './condor_submit.py'
  command = command + ' ' + job['input'] + ' ' + full_output_path+job['tag']
  for option in job['options']:
    command = command + ' ' + option
  command += ' '
  for option in common_options:
    command = command + ' ' + option
  command += ' --dir='+jobdir_prefix+job['tag']
  command += ' --auto'
  print(command+'\n')
  if not args.test: os.system(command)
