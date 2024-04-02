#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import argparse
from functools import reduce
import shutil
import ROOT
import helper.plotting_util as util

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from histo job directories")
parser.add_argument("--ask", default=False, action='store_true', help='')
parser.add_argument("--data", nargs='+', default=[], help='')
parser.add_argument("--mc", nargs='+', default=[], help='')
parser.add_argument("--othermc", nargs='+', default=[], help='')
parser.add_argument("--signal", nargs='+', default=[], help='')

parser.add_argument("-r", "--rehadd", action='store_true', help='rebuild hadds')

parser.add_argument("-p", "--prefix", help='prefix of job directories including "Job_Multijob_"')
parser.add_argument("-g", "--gjets_scale_up", action='store_true', help='scale gjets up to data')
parser.add_argument("--nosanity", action='store_true', help='omit sanity plots')
parser.add_argument("--trigger_eff", action='store_true', help='display trigger efficiencies')
parser.add_argument("--signalplots", action='store_true', help='add signal plots')
parser.add_argument("--cutflow", action='store_true', help='add cutflow plots')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
parser.add_argument("--saveroot", default=False, action='store_true', help='store .root and .cpp files for plots')
args = parser.parse_args()

# constants
hadd_dir_name = "hadd"
main_pdf = args.out+'_main.pdf'
cutflow_pdf = args.out+'_cutflow.pdf'
signal_pdf = args.out+'_signal.pdf'
leg_x1, leg_y1, leg_x2, leg_y2 = 0.7, 0.60, 0.89, 0.9
data_legend = 'Data'
signal_tag = 'SIGNAL_'
data_color = ROOT.kBlack
signalcolors = [ROOT.kRed, ROOT.kRed+1, ROOT.kBlue, ROOT.kBlue+1, ROOT.kPink, ROOT.kPink+1]
mccolors = [ROOT.kOrange, ROOT.kGreen]
othermccolors = [ROOT.kYellow+1, ROOT.kViolet, ROOT.kTeal]

# config
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)

# init
othermcnames = []
mcnames = []
signalnames = []
mc_filenames_list = []
mc_color = []
mc_legend = []
mc_hat_tag = []
mc_hist_collections = []
mc_hists_collections = []
mc_tfiles_collection = []
signal_legend = []
signal_color = []
signal_hist_collections = []
signal_hists_collections = []
signal_tfiles_collection = []
GJETS_POSITION = 1

# ask for names
print()
for multidir in args.othermc:
  othermcnames.append(raw_input("Input name for {}: ".format(multidir)))
for multidir in args.mc:
  mcnames.append(raw_input("Input name for {}: ".format(multidir)))
for multidir in args.signal:
  for subdir in os.listdir(multidir):
    if subdir == hadd_dir_name: continue
    signalnames.append(raw_input("Input name for {}/{}: ".format(multidir, subdir)))

# get directories to use
if args.ask:
  data_multijob_dir = raw_input("Enter MultiJob for data: ")
  othermc_multijob_dir = raw_input("Enter MultiJob for othermc: ")
  qcd_multijob_dir = raw_input("Enter MultiJob for qcd: ")
  gjets_multijob_dir = raw_input("Enter MultiJob for gjets: ")
  signal_multijob_dir = raw_input("Enter MultiJob for signal: ")
  multijob_dirs = [data_multijob_dir, othermc_multijob_dir, qcd_multijob_dir, gjets_multijob_dir, signal_multijob_dir]
else:
  #prefix = args.prefix
  #if not 'histograms_' in prefix: prefix = args.prefix + 'histograms_'
  #multijob_dirs = [d for d in os.listdir(".") if d.startswith(prefix)]
  multijob_dirs = []
  multijob_dirs.extend(args.data)
  multijob_dirs.extend(args.mc)
  multijob_dirs.extend(args.othermc)
  multijob_dirs.extend(args.signal)

# hadd
hadd_dirs = set()
for multijob_dir in multijob_dirs:
  if not os.path.isdir(multijob_dir): continue
  hadd_dir = os.path.join(multijob_dir, hadd_dir_name)
  hadd_dirs.add(hadd_dir)
  if args.rehadd: shutil.rmtree(hadd_dir)
  if not os.path.isdir(hadd_dir): os.mkdir(hadd_dir)
  summed_multijob = os.path.join(hadd_dir, "fullsum_{}.root".format(os.path.dirname(multijob_dir+'/')[13:]))
  multijob_subdirs = os.listdir(multijob_dir)
  summed_files = []
  for subdir in multijob_subdirs:
    if not os.path.isdir(os.path.join(multijob_dir, subdir)): continue
    if subdir == hadd_dir_name: continue
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
    if os.path.isfile(summed_file): continue
    os.system(command)
  command = " ".join(["hadd -f", summed_multijob, " ".join(summed_files)])
  if os.path.isfile(summed_multijob): continue
  os.system(command)

# retreive list of rootfiles
if args.ask:
  data_hadd_rootfiles = [os.path.join(data_multijob_dir, hadd_dir_name, filename) for filename in os.listdir(os.path.join(data_multijob_dir, hadd_dir_name))]
  othermc_hadd_rootfiles = [os.path.join(othermc_multijob_dir, hadd_dir_name, filename) for filename in os.listdir(os.path.join(othermc_multijob_dir, hadd_dir_name))]
  qcd_hadd_rootfiles = [os.path.join(qcd_multijob_dir, hadd_dir_name, filename) for filename in os.listdir(os.path.join(qcd_multijob_dir, hadd_dir_name))]
  gjets_hadd_rootfiles = [os.path.join(gjets_multijob_dir, hadd_dir_name, filename) for filename in os.listdir(os.path.join(gjets_multijob_dir, hadd_dir_name))]
  signal_hadd_rootfiles = [os.path.join(signal_multijob_dir, hadd_dir_name, filename) for filename in os.listdir(os.path.join(signal_multijob_dir, hadd_dir_name))]
  data_filenames = [filename for filename in data_hadd_rootfiles if not 'fullsum' in filename]
  mc_filenames_list.append([filename for filename in othermc_hadd_rootfiles if not 'fullsum' in filename])
  mc_filenames_list.append([filename for filename in qcd_hadd_rootfiles if not 'fullsum' in filename])
  mc_filenames_list.append([filename for filename in gjets_hadd_rootfiles if not 'fullsum' in filename])
  signal_filenames_list = [[filename] for filename in signal_hadd_rootfiles if not 'fullsum' in filename]
else:
  hadd_rootfiles = []
  for hadd_dir in hadd_dirs:
    hadd_rootfiles.extend([os.path.join(hadd_dir, filename) for filename in os.listdir(hadd_dir) if not filename.startswith('fullsum')])
  for multidir in args.data:
    data_filenames = [filename for filename in hadd_rootfiles if multidir[13:] in filename]
  for n, multidir in enumerate(args.othermc):
    mc_filenames_list.append([filename for filename in hadd_rootfiles if multidir[13:] in filename])
    mc_hat_tag.append(False)
    mc_color.append(othermccolors[n])
    mc_legend.append(othermcnames[n])
    GJETS_POSITION += 1
  for n, multidir in enumerate(args.mc):
    mc_filenames_list.append([filename for filename in hadd_rootfiles if multidir[13:] in filename])
    if 'qcd' in multidir: mc_hat_tag.append('QCD_')
    elif 'gjets' in multidir: mc_hat_tag.append('GJETS_')
    else: mc_hat_tag.append('UNKNOWN_')
    mc_color.append(mccolors[n])
    mc_legend.append(mcnames[n])
    if 'gjets' in multidir: GJETS_POSITION += n
  counter = 0
  signal_filenames_list = []
  for multidir in args.signal:
    signal_filenames_list.extend([[filename] for filename in hadd_rootfiles if multidir[13:] in filename])
    for subdir in os.listdir(multidir):
      if subdir == hadd_dir_name: continue
      signal_color.append(signalcolors[counter])
      signal_legend.append(signalnames[counter])
      counter += 1

# build histogram collections

data_tfiles = [ ROOT.TFile(filename) for filename in data_filenames]
col_histos = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in data_tfiles]
data_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_histos)

for signal_filenames in signal_filenames_list:
  signal_tfiles = [ ROOT.TFile(filename) for filename in signal_filenames]
  signal_tfiles_collection.append(signal_tfiles)
  col_histos = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in signal_tfiles]

  signal_hists_collection = col_histos
  signal_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_histos)

  signal_hists_collections.append(signal_hists_collection)
  signal_hist_collections.append(signal_hist_collection)

for mc_filenames in mc_filenames_list:
  mc_tfiles = [ ROOT.TFile(filename) for filename in mc_filenames]
  mc_tfiles_collection.append(mc_tfiles)
  col_histos = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in mc_tfiles]

  mc_hists_collection = col_histos
  mc_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_histos)

  mc_hists_collections.append(mc_hists_collection)
  mc_hist_collections.append(mc_hist_collection)

# start plotting
c = ROOT.TCanvas()

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

# signal plots
if args.signalplots:
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
      hists[0].Draw('hist')
      for j, hist in enumerate(hists[1:]):
        hist.SetLineColor(mc_color[i]+(j+1))
        hist.SetFillColor(mc_color[i]+(j+1))
        hist.Draw('hist same')
      c.Print(main_pdf)

  # rest of plots
  for i in range(len(data_hist_collection)):
    #if i >= 2: continue
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
    signal_hists = [coll[i] for coll in signal_hist_collections]
    mc_stack = ROOT.THStack('hs', 'hs')
    for mc_hist in mc_hists: mc_stack.Add(mc_hist)
    # color
    data_hist.SetLineColor(data_color)
    for j, mc_hist in enumerate(mc_hists):
      mc_hist.SetLineColor(mc_color[j])
      mc_hist.SetFillColor(mc_color[j])
    for j, signal_hist in enumerate(signal_hists):
      signal_hist.SetLineColor(signal_color[j])
    # legend
    leg = ROOT.TLegend(leg_x1, leg_y1, leg_x2, leg_y2)
    leg.AddEntry(data_hist, data_legend+' ({:,.0f})'.format(data_hist.Integral()), 'l')
    for j, mc_hist in enumerate(mc_hists):
      leg.AddEntry(mc_hist, mc_legend[j]+' ({:,.0f})'.format(mc_hist.Integral()), 'f')
    for j, signal_hist in enumerate(signal_hists):
      leg.AddEntry(signal_hist, signal_legend[j]+' ({:,.0f})'.format(signal_hist.Integral()), 'f')
    # draw linear
    c.SetLogy(0)
    data_hist.SetMinimum(0)
    data_hist.Draw()
    mc_stack.Draw('hist same')
    for signal_hist in signal_hists: signal_hist.Draw('hist same')
    data_hist.Draw("same")
    leg.Draw('same')
    c.Print(main_pdf)
    # draw log
    c.SetLogy(1)
    data_hist.SetMinimum(1e-1)
    data_hist.Draw()
    mc_stack.Draw('hist same')
    for signal_hist in signal_hists: signal_hist.Draw('hist same')
    data_hist.Draw("same")
    leg.Draw('same')
    c.Print(main_pdf)
    if args.saveroot: c.SaveSource("source_"+str(data_hist.GetName())+".cpp")
    if args.saveroot: c.SaveAs("rootplots_"+str(data_hist.GetName())+".root")
  c.Print(main_pdf+']')

# cutflows
if args.cutflow:
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
  for i, hist_collection in enumerate(signal_hist_collections):
    for hist in hist_collection:
      if not (hist.GetName()).startswith('cutflow'): continue
      hist.SetLineColor(signal_color[i])
      hist.Draw('hist')
      c.Print(cutflow_pdf)
  c.Print(cutflow_pdf+']')
