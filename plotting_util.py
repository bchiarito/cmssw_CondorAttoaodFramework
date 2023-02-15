#!/usr/bin/env python
import imp
import os
import sys
import ROOT
import json

# hadd directory and return the result
def get_hadd(jobdir):
  job = imp.load_source("job", jobdir+"job_info.py")
  output_path = job.output
  if not os.path.isfile(output_path+'/summed.root'):
    os.system('hadddir '+output_path+' '+output_path+'/summed.root')
  fi = ROOT.TFile(output_path+'/summed.root')
  return fi

# return metadata dictionary from jobdir
def get_meta(path, jobdir=True):
  if jobdir:
    job = imp.load_source("job", path+"job_info.py")
    output_path = job.output
    path = output_path
  d = {}
  metadata_chain = ROOT.TChain('Metadata')
  for fi in os.listdir(path):
    if fi.endswith('.root') and fi.startswith('attoaod'): metadata_chain.Add(path+'/'+fi)
  evtWritten, evtProcessed, evtPassDatafilter = 0, 0, 0
  for entry in metadata_chain:
    dataset_id = entry.dataset_id
    evtWritten += entry.evtWritten
    evtProcessed += entry.evtProcessed
    evtPassDatafilter += entry.evtPassDatafilter
    xs = entry.xs
  d['dataset_id'] = dataset_id
  d['evtWritten'] = evtWritten
  d['evtProcessed'] = evtProcessed
  d['evtPassDatafilter'] = evtPassDatafilter
  d['xs'] = xs
  return d
