from __future__ import print_function
import os
import sys
import imp
import argparse
parser = argparse.ArgumentParser(description='Executes multiple condor_submit.py commands, configuration inside script')
parser.add_argument('-t', '--test', action='store_true', help='print command but do not run')
parser.add_argument('prefix', help='full run on all matching jobs directories')
args = parser.parse_args()
jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

#job_tag          = 'plots_'+args.prefix[4:]
#output_dir       = 'twoprong/sanity_plots/plots/'
common_options   = [
'--lumi=59830',
'--filesPerJob=1',
#'--numJobs=1',
'-f'
]
#jobdir_prefix    = job_tag
#full_output_path = '/cms/chiarito/eos/' + output_dir + '/' + job_tag

locs = {}
for d in os.listdir('.'):
  if os.path.isdir(d) and d.startswith(args.prefix):
    tag = d[d.rfind('_')+1:]
    #job = imp.load_source("job", d+"/job_info.py")
    #path = job.output
    #locs[tag] = path
    locs[tag] = d
#for key in locs: print(key, locs[key])

## mc must have --numJobs=1
add_job(tag='egamma18a', options='--data',
        loc=locs['egamma18a'])
add_job(tag='egamma18b', options='--data',
        loc=locs['egamma18b'])
add_job(tag='egamma18c', options='--data',
        loc=locs['egamma18c'])
add_job(tag='egamma18d', options='--data',
        loc=locs['egamma18d'])
add_job(tag='gjets40to100', options='--mc',
        loc=locs['gjets40to100'])
add_job(tag='gjets100to200', options='--mc',
        loc=locs['gjets100to200'])
add_job(tag='gjets200to400', options='--mc',
        loc=locs['gjets200to400'])
add_job(tag='gjets400to600', options='--mc',
        loc=locs['gjets400to600'])
add_job(tag='gjets600toInf', options='--mc',
        loc=locs['gjets600toInf'])

##############################################################################
# run the metadata summing script on each directory

##############################################################################

for job in jobs:
  command = './condor_submit.py plotting'
  #command = command + ' ' + job['input'] + ' ' + full_output_path+job['tag']
  command = command + ' ' + job['input'] + ' -'
  for option in job['options']:
    command = command + ' ' + option
  command += ' '
  for option in common_options:
    command = command + ' ' + option
  #command += ' --dir='+jobdir_prefix+job['tag']
  command += ' --auto'
  print('\n'+command+'\n')
  if not args.test: os.system(command)
