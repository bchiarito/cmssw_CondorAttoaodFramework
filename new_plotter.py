#!/usr/bin/env python
import os
import sys
import imp
import argparse
from functools import reduce
import ROOT
import helper.plotting_util as util

# init
plotting_jobs = 'plotting_jobs/'
mc_dirs_list = []
mc_color = []
mc_legend = []
mc_hat_tag = []
signal_dirs_list = []
signal_color = []
signal_legend = []

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from atto+nano job directories")
parser.add_argument("prefix", help='prefix of job directories, include "Job_" part')
#parser.add_argument("--scale", action='store_true', default=False, help='scale data and mc to unit integral')
parser.add_argument("-g", "--gjets_scale", action='store_true', help='scale gjets up to data')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
args = parser.parse_args()

# data config
data_legend = 'Data'
data_color = ROOT.kBlack
data_dirs = [
  args.prefix+'egamma18a/'+plotting_jobs,
  args.prefix+'egamma18b/'+plotting_jobs,
]

# mc config
mc_legend.append('GJets')
mc_color.append(ROOT.kGreen)
mc_dirs_list.append([
  args.prefix+'gjets400to600/'+plotting_jobs,
])
mc_hat_tag.append('GJETS_')

mc_legend.append('QCD')
mc_color.append(ROOT.kOrange)
mc_dirs_list.append([
  args.prefix+'qcd2000toInf/'+plotting_jobs,
])
mc_hat_tag.append(False)

# signal config
signal_legend.append('Signal 500|eta')
signal_color.append(ROOT.kRed)
signal_dirs_list.append(['Job_signal_500_eta/'+plotting_jobs])

signal_legend.append('Signal 1200|0.5')
signal_color.append(ROOT.kBlue)
signal_dirs_list.append(['Job_signal_1200_0p5/'+plotting_jobs])

# other config
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)
leg_x1, leg_x2, leg_y1, leg_y2 = 0.7, 0.60, 0.9, 0.9
main = args.out+'.pdf'
cutflow = args.out+'_cutflow.pdf'

############################
c = ROOT.TCanvas()
c.Print(main+'[')
c.Print(cutflow+'[')

# mc hat plots
for i in range(len(mc_hat_tag)):
  if mc_hat_tag[i] == False: continue
  mc_collections = util.get_histo_collection(mc_dirs_list[i])
  for hist_list in zip(*mc_collections):
    if not (hist_list[0].GetName()).startswith(mc_hat_tag[i]): continue
    hist_list[0].SetLineColor(mc_color[i])
    hist_list[0].SetFillColor(mc_color[i])
    #hist_list[0].GetYaxis().SetRangeUser(1e3, 1e9)
    hist_list[0].Draw('hist')
    for j, hist in enumerate(hist_list[1:]):
      hist.SetLineColor(mc_color[i]+(j+1))
      hist.SetFillColor(mc_color[i]+(j+1))
      hist.Draw('hist same')
    c.Print(main)

# cutflow plots

# sanity plots
data_hist_collection = util.get_flat_histo_collection(data_dirs)
mc_hist_collections = [util.get_flat_histo_collection(mc_dirs) for mc_dirs in mc_dirs_list]
signal_hist_collections = [util.get_flat_histo_collection(signal_dirs) for signal_dirs in signal_dirs_list]

for i in range(len(data_hist_collection)):
  data_hist = data_hist_collection[i]
  data_hist.Sumw2()
  mc_hists = [coll[i] for coll in mc_hist_collections]
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
  leg = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2)
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
  c.Print(main)
  # draw log
  c.SetLogy(1)
  data_hist.SetMinimum(1e-1)
  data_hist.Draw()
  mc_stack.Draw('hist same')
  for signal_hist in signal_hists: signal_hist.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
c.Print(main+']')
c.Print(cutflow+']')

sys.exit()







# process into TH1's


data_histos = util.get_flat_histo_collection(datadirs)
gjets_histos = util.get_flat_histo_collection(gjetsdirs)
dy_histos = util.get_flat_histo_collection(dydirs)
qcd_histos = util.get_flat_histo_collection(qcddirs)
signal1_histos = util.get_flat_histo_collection(signal1dirs)
signal2_histos = util.get_flat_histo_collection(signal2dirs)
col_gjets_histos = util.get_histo_collection(gjetsdirs)
col_qcd_histos = util.get_histo_collection(qcddirs)

# start pdf files
c = ROOT.TCanvas()
c.Print(main+'[')
c.Print(cutflow+'[')

# hthat plot for gjets
c.SetLogy()
for hists in zip(*col_gjets_histos):
  if not (hists[0].GetName()).startswith('GJETS_'): continue
  hists[0].SetLineColor(gjets_color)
  hists[0].SetFillColor(gjets_color)
  hists[0].GetYaxis().SetRangeUser(1e3, 1e9)
  hists[0].Draw('hist')
  for i, hist in enumerate(hists[1:]):
    hist.SetLineColor(gjets_color+(i+1))
    hist.SetFillColor(gjets_color+(i+1))
    hist.Draw('hist same')
  c.Print(main)

# hthat plot for qcd
c.SetLogy()
for hists in zip(*col_qcd_histos):
  if not (hists[0].GetName()).startswith('QCD_'): continue
  hists[0].SetLineColor(qcd_color)
  hists[0].SetFillColor(qcd_color)
  hists[0].GetYaxis().SetRangeUser(1e2, 1e11)
  hists[0].Draw('hist')
  for i, hist in enumerate(hists[1:]):
    hist.SetLineColor(qcd_color+(i+1))
    hist.SetFillColor(qcd_color+(i+1))
    hist.Draw('hist same')
  c.Print(main)

# cutflow plots
c.SetLogy()
for data_hist in data_histos:
  if (data_hist.GetName()).startswith('cutflow'):
    data_hist.SetLineColor(ROOT.kBlack)
    data_hist.Draw()
    c.Print(cutflow)
for hists in zip(*col_gjets_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    for i, hist in enumerate(hists):
      hist.SetLineColor(gjets_color+i)
      hist.SetFillColor(gjets_color+i)
      hist.Draw('hist')
      c.Print(cutflow)
for dy_hist in dy_histos:
  if (dy_hist.GetName()).startswith('cutflow'):
    dy_hist.SetLineColor(dy_color)
    dy_hist.SetFillColor(dy_color)
    dy_hist.Draw()
    c.Print(cutflow)
for hists in zip(*col_qcd_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    for i, hist in enumerate(hists):
      hist.SetLineColor(qcd_color+i)
      hist.SetFillColor(qcd_color+i)
      hist.Draw('hist')
      c.Print(cutflow)
for signal_hist in signal1_histos:
  if (signal_hist.GetName()).startswith('cutflow'):
    signal_hist.SetLineColor(signal1_color)
    signal_hist.Draw()
    c.Print(cutflow)
for signal_hist in signal2_histos:
  if (signal_hist.GetName()).startswith('cutflow'):
    signal_hist.SetLineColor(signal2_color)
    signal_hist.Draw()
    c.Print(cutflow)



for data_hist, gjets_hist, dy_hist, qcd_hist, signal1_hist, signal2_hist in zip(
    data_histos, gjets_histos, dy_histos, qcd_histos, signal1_histos, signal2_histos):
  if (data_hist.GetName()).startswith('GJETS_'): continue
  if (data_hist.GetName()).startswith('QCD_'): continue
  if (data_hist.GetName()).startswith('cutflow'): continue
  # prepare data
  if args.scale and not data_hist.Integral()==0: data_hist.Scale(1.0/data_hist.Integral())
  data_integral = data_hist.Integral()
  data_underflow = data_hist.GetBinContent(0)
  data_overflow = data_hist.GetBinContent(data_hist.GetNbinsX()+1)
  # prepare mc
  if not gjets_hist.Integral()==0: gjets_hist.Scale(GJETS_FACTOR)
  hist_mcs = [dy_hist, qcd_hist, gjets_hist] # determines order in stack
  stack = ROOT.THStack('hs', 'hs')
  scale = 0
  if args.scale:
    integrals = [hist.Integral() for hist in hist_mcs]
    scale = reduce(lambda a,b: a+b, integrals)
  mc_integral = 0
  mc_underflow = 0
  mc_overflow = 0
  for hist in hist_mcs:
    if args.scale and not scale == 0: hist.Scale(1.0/scale)
    stack.Add(hist)
    mc_integral += hist.Integral()
    mc_underflow += hist.GetBinContent(0)
    mc_overflow += hist.GetBinContent(hist.GetNbinsX()+1)
  # prepare signal
  if args.scale and not signal1_hist.Integral()==0: signal1_hist.Scale(1.0/signal1_hist.Integral())
  signal1_integral = signal1_hist.Integral()
  signal1_underflow = signal1_hist.GetBinContent(0)
  signal1_overflow = signal1_hist.GetBinContent(signal1_hist.GetNbinsX()+1)
  if args.scale and not signal2_hist.Integral()==0: signal2_hist.Scale(1.0/signal2_hist.Integral())
  signal2_integral = signal2_hist.Integral()
  signal2_underflow = signal2_hist.GetBinContent(0)
  signal2_overflow = signal2_hist.GetBinContent(signal2_hist.GetNbinsX()+1)
  # color
  data_hist.SetLineColor(ROOT.kBlack)
  data_hist.Sumw2()
  gjets_hist.SetLineColor(gjets_color)
  gjets_hist.SetFillColor(gjets_color)
  dy_hist.SetLineColor(dy_color)
  dy_hist.SetFillColor(dy_color)
  qcd_hist.SetLineColor(qcd_color)
  qcd_hist.SetFillColor(qcd_color)
  signal1_hist.SetLineColor(signal1_color)
  signal2_hist.SetLineColor(signal2_color)
  # legend
  leg = ROOT.TLegend(0.7, 0.60, 0.9, 0.9)
  leg.AddEntry(data_hist, 'Data ({:,.0f})'.format(data_hist.Integral()), 'l')
  leg.AddEntry(hist_mcs[2], 'GJets ({:,.0f})'.format(gjets_hist.Integral()), 'f')
  leg.AddEntry(hist_mcs[0], 'DY m50 ({:,.0f})'.format(dy_hist.Integral()), 'f')
  leg.AddEntry(hist_mcs[1], 'QCD ({:,.0f})'.format(qcd_hist.Integral()), 'f')
  leg.AddEntry(signal1_hist, 'Signal 500|eta ({:,.0f})'.format(signal1_hist.Integral()), 'f')
  leg.AddEntry(signal2_hist, 'Signal 1200|0.5 ({:,.0f})'.format(signal2_hist.Integral()), 'f')
  if not data_underflow==0 or not data_overflow==0: leg.AddEntry('', "Data uo {:,.0f},{:,.0f}".format(data_underflow, data_overflow), '')
  if not mc_underflow==0 or not mc_overflow==0: leg.AddEntry('', "MC uo {:,.0f},{:,.0f}".format(mc_underflow, mc_overflow), '')
  if not signal1_underflow==0 or not signal1_overflow==0: leg.AddEntry('', "Signal1 uo {:,.0f},{:,.0f}".format(signal1_underflow, signal1_overflow), '')
  if not signal2_underflow==0 or not signal2_overflow==0: leg.AddEntry('', "Signal2 uo {:,.0f},{:,.0f}".format(signal2_underflow, signal2_overflow), '')
  # draw linear
  c.SetLogy(0)
  data_hist.Draw()
  data_hist.SetMinimum(0)
  stack.Draw('hist same')
  signal1_hist.Draw('hist same')
  signal2_hist.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
  # draw log
  c.SetLogy(1)
  data_hist.SetMinimum(1e-1)
  data_hist.Draw()
  stack.Draw('hist same')
  signal1_hist.Draw('hist same')
  signal2_hist.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
c.Print(main+']')
c.Print(cutflow+']')
