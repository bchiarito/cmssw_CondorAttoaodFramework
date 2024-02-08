#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import argparse
from functools import reduce
import ROOT
import helper.plotting_util as util

# init
plotting_jobs = 'plotting_jobs/'
mc_filenames_list = []
mc_color = []
mc_legend = []
mc_hat_tag = []
signal_dirs_list = []
signal_color = []
signal_legend = []

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from atto+nano job directories")
parser.add_argument("prefix", help='prefix of job directories, include "Job_" part')
parser.add_argument("-g", "--gjets_scale_up", action='store_true', help='scale gjets up to data')
parser.add_argument("--nocutflow", action='store_true', help='omit cutflow plots')
parser.add_argument("--nosanity", action='store_true', help='omit sanity plots')
parser.add_argument("--trigger_eff", action='store_true', help='display trigger efficiencies')
parser.add_argument("--filter_eff", action='store_true', help='display data filter efficiencies')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
parser.add_argument("--saveroot", default=False, action='store_true', help='store .root and .cpp files for plots')
args = parser.parse_args()

# other config
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)
leg_x1, leg_x2, leg_y1, leg_y2 = 0.7, 0.60, 0.9, 0.9
main_pdf = args.out+'.pdf'
cutflow_pdf = args.out+'_cutflow.pdf'
signal_pdf = args.out+'_signal.pdf'

prefix = args.prefix
hadd_dir = "hadd_"+prefix
if hadd_dir[-1] == '_': hadd_dir = hadd_dir[:-1]
multijob_dirs = [d for d in os.listdir(".") if d.startswith(prefix)]

# make hadds
if not os.path.isdir(hadd_dir):
  if not os.path.isdir(hadd_dir): os.mkdir(hadd_dir)
  for multijob_dir in multijob_dirs:
    #print("#######################")
    #print("#######################")
    #print(multijob_dir)
    multijob_subdirs = os.listdir(multijob_dir)
    summed_files = []
    for subdir in multijob_subdirs:
      if not os.path.isdir(os.path.join(multijob_dir, subdir)): continue
      job_dir = os.path.join(multijob_dir, subdir)
      sys.path.append(os.path.join(multijob_dir, subdir))
      import job_info as job
      output_area = job.output
      sys.path.pop()
      sys.modules.pop("job_info")
      output_list = os.listdir(output_area)
      rootfiles = []
      for item in output_list:
        if not os.path.isfile(os.path.join(output_area, item)): continue
        if not item.endswith(".root"): continue
        rootfiles.append(os.path.join(output_area, item))
      summed_file = os.path.join(hadd_dir, "sum_{}_{}.root".format(os.path.dirname(multijob_dir+'/')[13:], subdir))
      summed_files.append(summed_file)
      command = " ".join(["hadd -f", summed_file," ".join(rootfiles)])
      #print(command)
      os.system(command)
      #print("")
    summed_multijob = "sum_{}.root".format(os.path.dirname(multijob_dir+'/')[13:])
    command = " ".join(["hadd -f", os.path.join(hadd_dir, summed_multijob), " ".join(summed_files)])
    #print(command)
    os.system(command)
    #print("")

hadd_rootfiles = [os.path.join(hadd_dir, filename) for filename in os.listdir(hadd_dir)]
  
# data config
data_legend = 'Data'
data_color = ROOT.kBlack
data_filenames = [
#  args.prefix+'egamma18a/'+plotting_jobs,
#  args.prefix+'egamma18b/'+plotting_jobs,
#  args.prefix+'egamma18c/'+plotting_jobs,
#  args.prefix+'egamma18d/'+plotting_jobs,
#'sum_FullRun9_Jan13_histograms_egamma_fullrun.root'
]
data_filenames.extend([filename for filename in hadd_rootfiles if 'egamma' in filename])

# mc config (order is order of appearance)
GJETS_POSITION = 1 # starting from 1, record gjets position in list for purpose of scaling gjets
'''
mc_legend.append('DY')
mc_hat_tag.append(False)
mc_color.append(ROOT.kViolet)
mc_dirs_list.append([
  args.prefix+'dy50/'+plotting_jobs,
])
mc_legend.append('TTbar')
mc_hat_tag.append(False)
mc_color.append(ROOT.kPink+10)
mc_dirs_list.append([
  args.prefix+'ttbar/'+plotting_jobs,
])
mc_legend.append('WJets')
mc_hat_tag.append(False)
mc_color.append(ROOT.kYellow+1)
mc_dirs_list.append([
  args.prefix+'wjets/'+plotting_jobs,
])
mc_legend.append('QCD')
mc_hat_tag.append('QCD_')
mc_color.append(ROOT.kOrange)
mc_dirs_list.append([
  args.prefix+'qcd50to100/'+plotting_jobs,
  args.prefix+'qcd100to200/'+plotting_jobs,
  args.prefix+'qcd200to300/'+plotting_jobs,
  args.prefix+'qcd300to500/'+plotting_jobs,
  args.prefix+'qcd500to700/'+plotting_jobs,
  args.prefix+'qcd700to1000/'+plotting_jobs,
  args.prefix+'qcd1000to1500/'+plotting_jobs,
  args.prefix+'qcd1500to2000/'+plotting_jobs,
  args.prefix+'qcd2000toInf/'+plotting_jobs,
])
'''
mc_legend.append('GJets')
mc_hat_tag.append('GJETS_')
mc_color.append(ROOT.kGreen)
gjets_filenames = [filename for filename in hadd_rootfiles if 'egamma' in filename]
mc_filenames_list.append(
#'Job_MultiJob_FullRun9_Jan13_histograms_gjets_fullrun/subjob_1/'
#  args.prefix+'gjets40to100/'+plotting_jobs,
#  args.prefix+'gjets100to200/'+plotting_jobs,
#  args.prefix+'gjets200to400/'+plotting_jobs,
#  args.prefix+'gjets400to600/'+plotting_jobs,
#  args.prefix+'gjets600toInf/'+plotting_jobs,
#'sum_FullRun9_Jan13_histograms_gjets_fullrun_gjets100to200.root'
gjets_filenames
)

# signal config
'''
signal_legend.append('Signal 125,0.55')
signal_dirs_list.append([args.prefix+'signalM125m0p55/'+plotting_jobs])
signal_color.append(ROOT.kRed)
#signal_legend.append('Signal 690,1.225')
#signal_dirs_list.append([args.prefix+'signalM690m1p225/'+plotting_jobs])
#signal_color.append(ROOT.kRed+2)
signal_legend.append('Signal 1280,2.2')
signal_dirs_list.append([args.prefix+'signalM1280m2p2/'+plotting_jobs])
signal_color.append(ROOT.kBlue)
signal_legend.append('Signal 3050,3.175')
signal_dirs_list.append([args.prefix+'signalM3050m3p175/'+plotting_jobs])
signal_color.append(ROOT.kBlue+2)
signal_tag = 'SIGNAL_'
'''

print(data_filenames)
print(mc_filenames_list)
############################
c = ROOT.TCanvas()

#data_hist_collection = util.get_flat_histo_collection(data_dirs)
#mc_hist_collections = [util.get_flat_histo_collection(mc_dirs) for mc_dirs in mc_dirs_list]
#mc_hists_collections = [util.get_histo_collection(mc_dirs) for mc_dirs in mc_dirs_list]
#signal_hist_collections = [util.get_flat_histo_collection(signal_dirs) for signal_dirs in signal_dirs_list]

data_files = [ ROOT.TFile(filename) for filename in data_filenames]
col_histos = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in data_files]
data_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_histos)

#master_mc_files = [ [ROOT.TFile(filename) for filename in mc_filenames] for mc_filenames in mc_filenames_list]

mc_hist_collections = []
mc_hists_collections = []
for mc_filenames in mc_filenames_list:
  mc_files = [ ROOT.TFile(filename) for filename in mc_filenames]
  col_histos = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in mc_files]

  mc_hists_collection = col_histos
  mc_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_histos)

  mc_hists_collections.append(mc_hists_collection)
  mc_hist_collections.append(mc_hist_collection)

"""
mc_hists_collections = []
for mc_filenames in mc_filenames_list:
  mc_files = [ ROOT.TFile(filename) for filename in mc_filenames]
  col_histos = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in mc_files]
  mc_hists_collection = col_histos
  mc_hists_collections.append(mc_hists_collection)
"""
print(data_hist_collection)
print(mc_hist_collections[0])
print(mc_hists_collections[0])
'''
  col_histos = []
  for dir in dir_list:
    file = get_hadd(dir)
    files.append(file)
    col_histos.append( [key.ReadObj() for key in (file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()])
  return col_histos
'''

# gjets scale factor
if args.gjets_scale_up:
  k = GJETS_POSITION - 1 # position -> index conversion
  data_hist = data_hist_collection[0]
  data_total = data_hist.Integral() + data_hist.GetBinContent(0) + data_hist.GetBinContent(data_hist.GetNbinsX()+1)
  mc_hists = [coll[0] for coll in mc_hist_collections]
  mc_total = 0
  for mc_hist in mc_hists: mc_total += mc_hist.Integral() + mc_hist.GetBinContent(0) + mc_hist.GetBinContent(mc_hist.GetNbinsX()+1)
  gjets_hist = mc_hists[k]
  gjets_total = gjets_hist.Integral() + gjets_hist.GetBinContent(0) + gjets_hist.GetBinContent(gjets_hist.GetNbinsX()+1)
  GJETS_SCALE_FACTOR = (data_total - mc_total + gjets_total) / gjets_total
  print("\nGJets factor:", GJETS_SCALE_FACTOR, "\n")

# trigger efficiency
if args.trigger_eff:
  print('')
  for data_hist in data_hist_collection:
    if (data_hist.GetName()).startswith('cutflow'):
      print("data trigger eff", float(data_hist.GetBinContent(4))/float(data_hist.GetBinContent(3)))
  for i, hists_collection in enumerate(mc_hists_collections):
    for hists in zip(*hists_collection):
      if (hists[0].GetName()).startswith('cutflow'):
        for hist in hists:
          if not hist.GetBinContent(3)==0: print(mc_legend[i]+" trigger eff", float(hist.GetBinContent(4))/float(hist.GetBinContent(3)))
  for i, hist_collection in enumerate(signal_hist_collections):
    for hist in hist_collection:
      if (hist.GetName()).startswith('cutflow'):
        if not hist.GetBinContent(3)==0: print(signal_legend[i]+" trigger eff", float(hist.GetBinContent(4))/float(hist.GetBinContent(3)))
  print('')

# data filter efficiency
if args.filter_eff:
  print('')
  print('Data Filter efficiencies:')
  effs = util.get_effs(data_dirs)
  for dir, eff in zip(data_dirs, effs):
    print(dir, eff)
  print('')

"""
# signal plots
c.Print(signal_pdf+'[')
c.SetLogy(0)
for i, coll in enumerate(signal_hist_collections):
  numer_plots = []
  denom_plots = []
  for hist in coll:
    if not (hist.GetName()).startswith(signal_tag): continue
    if 'NUMER' in hist.GetName(): numer_plots.append(hist)
    if 'DENOM' in hist.GetName(): denom_plots.append(hist)
    hist.SetLineColor(signal_color[i])
    hist.Draw('hist')
    c.Print(signal_pdf)
  for numer, denom in zip(numer_plots, denom_plots):
    eff = ROOT.TEfficiency(numer, denom)
    eff.SetLineColor(signal_color[i])
    eff.SetMarkerColor(signal_color[i])
    eff.SetTitle(numer.GetTitle()[:-5]+'efficiency')
    eff.Draw('AP')
    c.Print(signal_pdf)
    if args.saveroot: c.SaveSource("source_"+str(eff.GetName())+".cpp")
    if args.saveroot: c.SaveAs("rootplots_"+str(eff.GetName())+".root")
c.Print(signal_pdf+']')
"""

# sanity plots
if not args.nosanity:
  c.Print(main_pdf+'[')

  # mc hat plots
  c.SetLogy()
  for i in range(len(mc_hat_tag)):
    if mc_hat_tag[i] == False: continue
    for hists in zip(*(mc_hists_collections[i])):
      if not (hists[0].GetName()).startswith(mc_hat_tag[i]): continue
      hists[0].SetLineColor(mc_color[i])
      hists[0].SetFillColor(mc_color[i])
      hists[0].SetMinimum(1.0)
      hists[0].SetMaximum(1e10)
      #hists[0].GetYaxis().SetRangeUser(1e3, 1e9)
      hists[0].Draw('hist')
      for j, hist in enumerate(hists[1:]):
        hist.SetLineColor(mc_color[i]+(j+1))
        hist.SetFillColor(mc_color[i]+(j+1))
        hist.Draw('hist same')
      c.Print(main_pdf)

  # rest of plots
  for i in range(len(data_hist_collection)):
    data_hist = data_hist_collection[i]
    # skip cutflow and mchat
    if (data_hist.GetName()).startswith('cutflow'): continue
    skip = False
    for tag in mc_hat_tag:
      if tag and (data_hist.GetName()).startswith(tag): skip = True
    if skip: continue
    # continue with plotting
    data_hist.Sumw2()
    mc_hists = [coll[i] for coll in mc_hist_collections]
    if args.gjets_scale_up: mc_hists[k].Scale(GJETS_SCALE_FACTOR)
#    signal_hists = [coll[i] for coll in signal_hist_collections]
    mc_stack = ROOT.THStack('hs', 'hs')
    for mc_hist in mc_hists: mc_stack.Add(mc_hist)
    # color
    data_hist.SetLineColor(data_color)
    for j, mc_hist in enumerate(mc_hists):
      mc_hist.SetLineColor(mc_color[j])
      mc_hist.SetFillColor(mc_color[j])
#    for j, signal_hist in enumerate(signal_hists):
#      signal_hist.SetLineColor(signal_color[j])
    # legend
    leg = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2)
    leg.AddEntry(data_hist, data_legend+' ({:,.0f})'.format(data_hist.Integral()), 'l')
    for j, mc_hist in enumerate(mc_hists):
      leg.AddEntry(mc_hist, mc_legend[j]+' ({:,.0f})'.format(mc_hist.Integral()), 'f')
#    for j, signal_hist in enumerate(signal_hists):
#      leg.AddEntry(signal_hist, signal_legend[j]+' ({:,.0f})'.format(signal_hist.Integral()), 'f')
    # draw linear
    c.SetLogy(0)
    data_hist.SetMinimum(0)
    data_hist.Draw()
    mc_stack.Draw('hist same')
#    for signal_hist in signal_hists: signal_hist.Draw('hist same')
    data_hist.Draw("same")
    leg.Draw('same')
    c.Print(main_pdf)
    # draw log
    c.SetLogy(1)
    data_hist.SetMinimum(1e-1)
    data_hist.Draw()
    mc_stack.Draw('hist same')
#    for signal_hist in signal_hists: signal_hist.Draw('hist same')
    data_hist.Draw("same")
    leg.Draw('same')
    c.Print(main_pdf)
    if args.saveroot: c.SaveSource("source_"+str(data_hist.GetName())+".cpp")
    if args.saveroot: c.SaveAs("rootplots_"+str(data_hist.GetName())+".root")
  c.Print(main_pdf+']')

# cutflows
if not args.nocutflow:
  c.Print(cutflow_pdf+'[')
  c.SetLogy()
  for hist in data_hist_collection:
    if not (hist.GetName()).startswith('cutflow'): continue
    hist.SetLineColor(data_color)
    hist.Draw('hist')
    c.Print(cutflow_pdf)
  for i, hists_collection in enumerate(mc_hists_collections):
    for hists in zip(*hists_collection):
      if not (hists[0].GetName()).startswith('cutflow'): continue
      for j, hist in enumerate(hists):
        hist.SetLineColor(mc_color[i]+j)
        hist.SetFillColor(mc_color[i]+j)
        hist.Draw('hist')
        c.Print(cutflow_pdf)
  """
  for i, hist_collection in enumerate(signal_hist_collections):
    for hist in hist_collection:
      if not (hist.GetName()).startswith('cutflow'): continue
      hist.SetLineColor(signal_color[i])
      hist.Draw('hist')
      c.Print(cutflow_pdf)
  """
  c.Print(cutflow_pdf+']')
