#!/usr/bin/env python
import imp
import os
import sys
import ROOT
import json

# global to prevent files from closing when going out of scope
files = []

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
    job = imp.load_source("job", path+"/job_info.py")
    output_path = job.output
    path = output_path
  d = {}
  metadata_chain = ROOT.TChain('Metadata')
  for fi in os.listdir(path):
    if fi.endswith('.root') and fi.startswith('ATTOAOD'): metadata_chain.Add(path+'/'+fi)
  evtWritten, evtProcessed, evtPassDatafilter = 0, 0, 0
  print(path)
  print(metadata_chain.GetEntries())
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

def get_histo_collection(dir_list):
  '''
  Takes a list of directories with histogram-level rootfiles
  
  first hadds each directory
  then collects the histograms into a list

  Returns a list, 1-1 with the original directories, each entry of which is a list of TH1's from the rootfiles
  '''
  col_histos = []
  for dir in dir_list:
    file = get_hadd(dir)
    files.append(file)
    col_histos.append( [key.ReadObj() for key in (file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()])
  return col_histos

def get_flat_histo_collection(dir_list):
  '''
  Similar to get_histo_collection but additionally adds the corresponding histograms from each directory
  only appropriate if each directory in the list corresponds to the same dataset
  
  Returns a list of TH1's, summed across both files and directories
  '''
  col_histos = []
  for dir in dir_list:
    file = get_hadd(os.path.join(os.path.normpath(dir),""))
    files.append(file)
    col_histos.append( [key.ReadObj() for key in (file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()])
  return reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_histos)

def get_effs(dir_list, jobdir=True):
  '''
  Takes a list of directories with atto-level rootfiles (incl metadata)
  
  Returns a list of data filter efficiencies, 1-1 with the original directories
  '''
  effs = []
  for dir in dir_list:
    metadata = get_meta(dir, jobdir)
    total = float(metadata['evtProcessed'])
    passfilter = float(metadata['evtPassDatafilter'])
    effs.append(passfilter/total)
  return effs
