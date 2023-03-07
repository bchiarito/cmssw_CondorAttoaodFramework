#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import argparse
from functools import reduce
import ROOT
import helper.plotting_util as util

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from atto+nano job directories")
parser.add_argument("prefix", help='prefix of job directories, include "Job_" part')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
parser.add_argument("--scale", action='store_true', default=False, help='scale data and mc to unit integral')
args = parser.parse_args()

# constants
plotting_jobs = 'plotting_jobs/'
gjets_color = ROOT.kGreen
dy_color = ROOT.kViolet
qcd_color = ROOT.kOrange #41
signal_color = ROOT.kRed
ROOT.gStyle.SetOptStat(0)
main = args.out+'.pdf'
cutflow = args.out+'_cutflow.pdf'
SIGNAL_NORM = 10000
lumi = 59830 # pb^-1

# define job directories
# data
datadirs = []
datadirs.append(args.prefix + 'egamma18a/' + plotting_jobs)
datadirs.append(args.prefix + 'egamma18b/' + plotting_jobs)
datadirs.append(args.prefix + 'egamma18c/' + plotting_jobs)
datadirs.append(args.prefix + 'egamma18d/' + plotting_jobs)
# mc
gjetsdirs = []
gjetsdirs.append(args.prefix + 'gjets40to100/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets100to200/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets200to400/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets400to600/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets600toInf/' + plotting_jobs)
dydirs = []
dydirs.append(args.prefix + 'dy50/' + plotting_jobs)
qcddirs = []
qcddirs.append(args.prefix + 'qcd50to100/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd100to200/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd200to300/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd300to500/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd700to1000/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd1000to1500/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd1500to2000/' + plotting_jobs)
qcddirs.append(args.prefix + 'qcd2000toInf/' + plotting_jobs)
# signal
signaldirs = []
signaldirs.append('Job_signal_500_eta/plotting_jobs/')

# process into TH1's
data_histos = util.get_flat_histo_collection(datadirs)
gjets_histos = util.get_flat_histo_collection(gjetsdirs)
dy_histos = util.get_flat_histo_collection(dydirs)
qcd_histos = util.get_flat_histo_collection(qcddirs)
signal_histos = util.get_flat_histo_collection(signaldirs)
col_gjets_histos = util.get_histo_collection(gjetsdirs)
col_qcd_histos = util.get_histo_collection(qcddirs)

# diagnostic event totals
for data_hist, gjets_hist, dy_hist, qcd_hist, signal_hist in zip(data_histos, gjets_histos, dy_histos, qcd_histos, signal_histos):
  data_integral = data_hist.Integral() + data_hist.GetBinContent(0) + data_hist.GetBinContent(data_hist.GetNbinsX()+1)
  gjets_integral = gjets_hist.Integral() + gjets_hist.GetBinContent(0) + gjets_hist.GetBinContent(gjets_hist.GetNbinsX()+1)
  qcd_integral = qcd_hist.Integral() + qcd_hist.GetBinContent(0) + qcd_hist.GetBinContent(qcd_hist.GetNbinsX()+1)
  dy_integral = dy_hist.Integral() + dy_hist.GetBinContent(0) + dy_hist.GetBinContent(dy_hist.GetNbinsX()+1)
  signal_integral = signal_hist.Integral() + signal_hist.GetBinContent(0) + signal_hist.GetBinContent(signal_hist.GetNbinsX()+1)
  print('')
  print("Data Events {:,.0f}".format(data_integral))
  print("GJets Events {:,.0f}".format(gjets_integral))
  print("QCD Events {:,.0f}".format(qcd_integral))
  print("DY Events {:,.0f}".format(dy_integral))
  print("MC Events {:,.0f}".format(gjets_integral + qcd_integral + dy_integral))
  print("Data/MC {}".format(data_integral/(gjets_integral + qcd_integral + dy_integral)))
  print('')
  break

gjets_scale_factor = (data_integral - qcd_integral) / gjets_integral
print("GJets factor:", gjets_scale_factor)

print("")
for data_hist in data_histos:
  if (data_hist.GetName()).startswith('cutflow'):
    print("data trigger eff", float(data_hist.GetBinContent(4))/float(data_hist.GetBinContent(3)))
for hists in zip(*col_gjets_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    for i, hist in enumerate(hists):
      if not hist.GetBinContent(3) == 0: print("gjets trigger eff", float(hist.GetBinContent(4))/float(hist.GetBinContent(3)))
for dy_hist in dy_histos:
  if (dy_hist.GetName()).startswith('cutflow'):
    if not dy_hist.GetBinContent(3) == 0: print("dy trigger eff", float(dy_hist.GetBinContent(4))/float(dy_hist.GetBinContent(3)))
for hists in zip(*col_qcd_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    for i, hist in enumerate(hists):
      if not hist.GetBinContent(3) == 0: print("qcd trigger eff", float(hist.GetBinContent(4))/float(hist.GetBinContent(3)))
for signal_hist in signal_histos:
  if (signal_hist.GetName()).startswith('cutflow'):
    print("signal trigger eff", float(signal_hist.GetBinContent(4))/float(signal_hist.GetBinContent(3)))

print('\nData Filter efficiencies:')
effs = util.get_effs(datadirs)
for dir, eff in zip(datadirs, effs):
  print(dir, eff)
