#!/usr/bin/env python
import os
import sys
import imp
import argparse
from functools import reduce
from array import array
import ROOT

# command line options
parser = argparse.ArgumentParser(description="")
# input/output
parser.add_argument("jobdir", help='')
args = parser.parse_args()

job = imp.load_source("job", args.jobdir+"job_info.py")
path = job.output

metadata_chain = ROOT.TChain('Metadata')
for fi in os.listdir(path):
  if fi.endswith('.root'):
    #print(fi)
    metadata_chain.Add(path+'/'+fi)

#for entry in metadata_chain:
#  print(entry.dataset_id)

def add_branch(tree, char, name):
  temp_array = array(char, [0])
  tree.Branch(name, temp_array, name+'/'+char.upper())
  return temp_array

tree = ROOT.TTree('metadata', 'metadata')
dataset_id = add_branch(tree, 'i', 'dataset_id')
flag = add_branch(tree, 'i', 'flag')
evtWritten = add_branch(tree, 'i', 'evtWritten')
evtProcessed = add_branch(tree, 'i', 'evtProcessed')
evtPassDatafilter = add_branch(tree, 'i', 'evtPassDatafilter')
xs = add_branch(tree, 'f', 'xs')

for branch in metadata_chain.GetListOfBranches():
  print(branch.GetName())
'''
for entry in metadata_chain:
  #print(entry.dataset_id)
  dataset_id[0] = entry.dataset_id
  flag[0] = entry.flag
  evtWritten[0] = entry.evtWritten
  evtProcessed[0] = entry.evtProcessed
  evtPassDatafilter[0] = entry.evtPassDatafilter
  xs[0] = entry.xs
  tree.Fill()
'''

s_dataset_id = 0
s_evtWritten = 0
s_evtProcessed = 0
s_evtPassDatafilter = 0
s_xs = 0

for entry in metadata_chain:
  #print(entry.dataset_id)
  s_dataset_id = entry.dataset_id
  s_evtWritten += entry.evtWritten
  s_evtProcessed += entry.evtProcessed
  s_evtPassDatafilter += entry.evtPassDatafilter
  s_xs = entry.xs

dataset_id[0] = s_dataset_id
evtWritten[0] = s_evtWritten
evtProcessed[0] = s_evtProcessed
evtPassDatafilter[0] = s_evtPassDatafilter
xs[0] = s_xs
tree.Fill()

for entry in tree:
  print(entry.dataset_id)
  print(entry.evtWritten)
  print(entry.evtProcessed)
  print(entry.evtPassDatafilter)
  print(entry.xs)

print([entry.dataset_id for entry in tree])

outfile = ROOT.TFile('full_metadata.root', 'recreate')
tree.Write()
outfile.Close()
os.system('mv full_metadata.root '+path)
