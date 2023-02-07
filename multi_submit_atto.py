from __future__ import print_function
jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

##############################################################################

job_tag          = 'fullrun2_loctohex_wfilter_feb6'
output_dir       = 'twoprong/sanity_plots/atto'
common_options   = [
'--filesPerJob=20',
'--scheddLimit=100',
'--filter="one_hpid_photon"',
'--recophiphoton=HPID'
]
jobdir_prefix    = job_tag + '_'
full_output_path = '/cms/chiarito/eos/' + output_dir + '/' + job_tag

add_job(tag='egamma18a', options='--data --datasetname=egamma18a',
        loc='/cms/twoprong/chiarito/nano/egamma_18a/fv1p4-10-44c4_bv1p1-1-331c')
add_job(tag='egamma18b', options='--data --datasetname=egamma18b',
        loc='/cms/twoprong/chiarito/nano/egamma_18b/fv1p4-12-b296_bv1p1-1-331c')
add_job(tag='egamma18c', options='--data --datasetname=egamma18c',
        loc='/cms/twoprong/chiarito/nano/egamma_18c/fv1p4-16-9f1a_bv1p1-1-331c')
add_job(tag='egamma18d', options='--data --datasetname=egamma18d',
        loc='/cms/twoprong/chiarito/nano/egamma_18d/')
add_job(tag='gjets40to100', options='--mc --xs=20810 --datasetname=gjets40to100',
        loc='/cms/twoprong/chiarito/nano/gjets_10per/gjets40to100/')
add_job(tag='gjets100to200', options='--mc --xs=9223 --datasetname=gjets100to200',
        loc='/cms/twoprong/chiarito/nano/gjets_10per/gjets100to200')
add_job(tag='gjets200to400', options='--mc --xs=2303 --datasetname=gjets200to400',
        loc='/cms/twoprong/chiarito/nano/gjets_10per/gjets200to400')
add_job(tag='gjets400to600', options='--mc --xs=274.5 --datasetname=gjets400to600',
        loc='/cms/twoprong/chiarito/nano/gjets_10per/gjets400to600')
add_job(tag='gjets600toInf', options='--mc --xs=93.52 --datasetname=gjets600toInf',
        loc='/cms/twoprong/chiarito/nano/gjets_10per/gjets600toInf')

##############################################################################

import os
import argparse
parser = argparse.ArgumentParser(description='Executes multiple condor_submit.py commands, configuration inside script')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

for job in jobs:
  command = './condor_submit.py atto'
  command = command + ' ' + job['input'] + ' ' + full_output_path+'/'+job['tag']
  for option in job['options']:
    command = command + ' ' + option
  command += ' '
  for option in common_options:
    command = command + ' ' + option
  command += ' --dir='+jobdir_prefix+job['tag']
  command += ' --auto'
  print(command+'\n')
  if not args.test: os.system(command)
