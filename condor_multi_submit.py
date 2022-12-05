from __future__ import print_function
import os

# multirunner for nano>atto

inputs = [
('/store/user/bchiari1/full_dataset_runs/gjets_40to100_UL18_10per/2022-09-06-10-29-01/fv1p4-12-b296_bv1p1-1-331c/', 'gjets40to100'),
('/store/user/bchiari1/full_dataset_runs/gjets_100to200_UL18_10per/2022-09-10-14-52-10/fv1p4-12-b296_bv1p1-1-331c/', 'gjets100to200'),
('/store/user/bchiari1/full_dataset_runs/gjets_200to400_UL18/2022-09-02-20-27-08/fv1p4-12-b296_bv1p1-1-331c/', 'gjets200to400'),
('/store/user/bchiari1/full_dataset_runs/gjets_400to600_UL18_10per/2022-09-05-12-58-43/fv1p4-12-b296_bv1p1-1-331c/', 'gjets400to600'),
('/store/user/bchiari1/full_dataset_runs/gjets_600toInf_UL18_10per/2022-09-05-13-02-50/fv1p4-12-b296_bv1p1-1-331c/', 'gjets600toInf'),
]
output_head = '/store/user/bchiari1/bkg_est/atto/gjets_10per/'
other_commands = '--mc --filesPerJob=2 --auto'
jobname = 'nov22gjets'

for i in inputs:
  path, name = i[0], i[1]
  command = './condor_submit.py '+path+' '+output_head+name+'/ '+other_commands+' --dir='+jobname+'_'+name
  print(command)
  os.system(command)
