from __future__ import print_function
import os

# multirunner for nano>atto
output_head = '/store/user/bchiari1/atto/datamc_full/'
jobname_prefix = 'jan16_fullrun2'
for_all = '--filesPerJob=20 --auto --sel=one_hpid_photon'

###
o = output_head
jobs = [
('egamma18a', '/store/user/bchiari1/full_dataset_runs_egamma_18a_full/2022-08-23-18-32-47/fv1p4-10-44c4_bv1p1-1-331c', o+'egamma18a', '--data', '--datasetname=egamma18a'),
('egamma18b', '/store/user/lpcrutgers/sthayil/pseudoaxions/nano/egamma2018b_09-22/2022-09-16-10-48-54/fv1p4-12-b296_bv1p1-1-331c', o+'egamma18b', '--data', '--datasetname=egamma18b'),
('egamma18c', '/store/user/bchiari1/full_dataset_runs/egamma_18c_full/2022-12-05-20-00-01/fv1p4-16-9f1a_bv1p1-1-331c', o+'egamma18c', '--data', '--datasetname=egamma18c'),
('gjets40to100', '/store/user/bchiari1/full_dataset_runs/gjets_40to100_UL18_10per/2022-09-06-10-29-01/fv1p4-12-b296_bv1p1-1-331c/', o+'gjets40to100', '--xs=20810', '--mc', '--datasetname=gjets40to100'),
('gjets100to200', '/store/user/bchiari1/full_dataset_runs/gjets_100to200_UL18_10per/2022-09-10-14-52-10/fv1p4-12-b296_bv1p1-1-331c/', o+'gjets100to200', '--xs=9223', '--mc', '--datasetname=gjets100to200'),
('gjets200to400', '/store/user/bchiari1/full_dataset_runs/gjets_200to400_UL18_10per/2022-11-22-20-09-46/fv1p4-16-9f1a_bv1p1-1-331c/', o+'gjets200to400', '--xs=2303', '--mc', '--datasetname=gjets200to400'),
('gjets400to600', '/store/user/bchiari1/full_dataset_runs/gjets_400to600_UL18_10per/2022-09-05-12-58-43/fv1p4-12-b296_bv1p1-1-331c/', o+'gjets400to600', '--xs=274.5', '--mc', '--datasetname=400to600'),
('gjets600toInf', '/store/user/bchiari1/full_dataset_runs/gjets_600toInf_UL18_10per/2022-09-05-13-02-50/fv1p4-12-b296_bv1p1-1-331c/', o+'gjets600toInf', '--xs=93.52', '--mc', '--datasetname=gjets600toInf'),
]
for i,job in enumerate(jobs):
  command = './condor_submit.py'
  for block in job[1:]:
    command = command + ' ' + block
  command = command + ' ' + for_all + ' --dir='+jobname_prefix+'_'+job[0]
  print('\n'+command)
  os.system(command)
