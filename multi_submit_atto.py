from __future__ import print_function
jobs = []
def add_job(tag, options, loc):
  job = {}; job['input'] = loc; job['tag'] = tag; job['options'] = options.split(); jobs.append(job)

##############################################################################

job_tag          = 'fullrun_feb4'
output_dir       = 'twoprong/sanity_plots/atto'
common_options   = [
'--filesPerJob=40',
'--scheddLimit=100',
'--recophiphoton=HPID'
]
jobdir_prefix    = job_tag + '_'
full_output_path = '/cms/chiarito/eos/' + output_dir + '/' + job_tag

add_job(tag='egamma18a', options='--data --input_cmslpc --datasetname=egamma18a',
        loc='/store/user/bchiari1/full_dataset_runs_egamma_18a_full/2022-08-23-18-32-47/fv1p4-10-44c4_bv1p1-1-331c')
add_job(tag='egamma18b', options='--data --input_cmslpc --datasetname=egamma18b',
        loc='/store/user/lpcrutgers/sthayil/pseudoaxions/nano/egamma2018b_09-22/2022-09-16-10-48-54/fv1p4-12-b296_bv1p1-1-331c')
add_job(tag='egamma18c', options='--data --input_cmslpc --datasetname=egamma18c',
        loc='/store/user/bchiari1/full_dataset_runs/egamma_18c_full/2022-12-05-20-00-01/fv1p4-16-9f1a_bv1p1-1-331c')
add_job(tag='egamma18d', options='--data --datasetname=egamma18d',
        loc='/cms/twoprong/jwf82/condor_miniaod_runs/egamma_datasets/egamma_2018D/2022-08-24-09-17-01')
add_job(tag='gjets40to100', options='--mc --input_cmslpc --xs=20810 --datasetname=gjets40to100',
        loc='/store/user/bchiari1/full_dataset_runs/gjets_40to100_UL18_10per/2022-09-06-10-29-01/fv1p4-12-b296_bv1p1-1-331c/')
add_job(tag='gjets100to200', options='--mc --input_cmslpc --xs=9223 --datasetname=gjets100to200',
        loc='/store/user/bchiari1/full_dataset_runs/gjets_100to200_UL18_10per/2022-09-10-14-52-10/fv1p4-12-b296_bv1p1-1-331c/')
add_job(tag='gjets200to400', options='--mc --input_cmslpc --xs=2303 --datasetname=gjets200to400',
        loc='/store/user/bchiari1/full_dataset_runs/gjets_200to400_UL18_10per/2022-11-22-20-09-46/fv1p4-16-9f1a_bv1p1-1-331c/')
add_job(tag='gjets400to600', options='--mc --input_cmslpc --xs=274.5 --datasetname=gjets400to600',
        loc='/store/user/bchiari1/full_dataset_runs/gjets_400to600_UL18_10per/2022-09-05-12-58-43/fv1p4-12-b296_bv1p1-1-331c/')
add_job(tag='gjets600toInf', options='--mc --input_cmslpc --xs=93.52 --datasetname=gjets600toInf',
        loc='/store/user/bchiari1/full_dataset_runs/gjets_600toInf_UL18_10per/2022-09-05-13-02-50/fv1p4-12-b296_bv1p1-1-331c/')

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
