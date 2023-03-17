#!/usr/bin/env python
import os
import sys
import imp
import argparse
from functools import reduce
from array import array
import ROOT

# command line options
parser = argparse.ArgumentParser(description="produce full metadata for local directory with attoaod")
parser.add_argument("path", help='')
parser.add_argument("--outfile", default='full_metadata.root', help='')
args = parser.parse_args()

metadata_chain = ROOT.TChain('Metadata')
for fi in os.listdir(args.path):
  if fi.endswith('.root') and fi.startswith('ATTOAOD'):
    metadata_chain.Add(args.path+'/'+fi)

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

s_dataset_id = 0
s_evtWritten = 0
s_evtProcessed = 0
s_evtPassDatafilter = 0
s_xs = 0

for entry in metadata_chain:
  dataset_id[0] = entry.dataset_id
  flag[0] = entry.flag
  evtWritten[0] = entry.evtWritten
  evtProcessed[0] = entry.evtProcessed
  evtPassDatafilter[0] = entry.evtPassDatafilter
  xs[0] = entry.xs
  tree.Fill()

for entry in tree:
  print(entry.dataset_id)
  print(entry.flag)
  print(entry.evtWritten)
  print(entry.evtProcessed)
  print(entry.evtPassDatafilter)
  print(entry.xs)

outfile = ROOT.TFile(args.outfile, 'recreate')
tree.Write()
outfile.Close()
os.system('mv '+args.outfile+' '+args.path)
