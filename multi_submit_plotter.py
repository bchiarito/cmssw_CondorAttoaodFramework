from __future__ import print_function
jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

##############################################################################

output_dir       = 'twoprong/sanity_plots/plots/'
job_tag          = 'plots_fullrun_feb3'
common_options   = [
'--lumi=59830'
]
jobdir_prefix    = job_tag + '_'
full_output_path = '/cms/chiarito/condor/' + output_dir + '/' + job_tag

## mc must have --numJobs=1
add_job(tag='egamma18a', options='--data --filesPerJob=10',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/egamma18a/2023-02-03-19-22-45/fv0p9-12-3f99')
add_job(tag='egamma18b', options='--data --filesPerJob=25',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/egamma18b/2023-02-03-19-22-49/fv0p9-12-3f99')
add_job(tag='egamma18c', options='--data --filesPerJob=25',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/egamma18c/2023-02-03-19-22-52/fv0p9-12-3f99')
add_job(tag='egamma18d', options='--data --filesPerJob=1000',
        loc='')
add_job(tag='gjets40to100', options='--mc --numJobs=1',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/gjets40to100/2023-02-03-19-23-00/fv0p9-12-3f99')
add_job(tag='gjets100to200', options='--mc --numJobs=1',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/gjets100to200/2023-02-03-19-23-07/fv0p9-12-3f99')
add_job(tag='gjets200to400', options='--mc --numJobs=1',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/gjets200to400/2023-02-03-19-23-10/fv0p9-12-3f99')
add_job(tag='gjets400to600', options='--mc --numJobs=1',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/gjets400to600/2023-02-03-19-23-13/fv0p9-12-3f99')
add_job(tag='gjets600toInf', options='--mc --numJobs=1',
        loc='/cms/chiarito/condor/twoprong/sanity_plots/atto/fullrun_feb3/gjets600toInf/2023-02-03-19-23-16/fv0p9-12-3f99')

##############################################################################

import os
import argparse
parser = argparse.ArgumentParser(description='Executes multiple condor_submit.py commands, configuration inside script')
parser.add_argument('-t', '--test', action='store_true', help='print command but do not run')
args = parser.parse_args()

for job in jobs:
  command = './condor_submit.py plotting'
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
