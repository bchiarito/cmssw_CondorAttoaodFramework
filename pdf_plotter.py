#!/usr/bin/env python
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
parser.add_argument("-g", "--gjets_scale", type=float, default=1.21967655618, help='scale factor for gjets')
args = parser.parse_args()

# constants
plotting_jobs = 'plotting_jobs/'
gjets_color = ROOT.kGreen
dy_color = ROOT.kViolet
qcd_color = ROOT.kOrange #41
signal_color = ROOT.kRed
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)
main = args.out+'.pdf'
cutflow = args.out+'_cutflow.pdf'
SIGNAL_NORM = 10000
GJETS_FACTOR = args.gjets_scale #1.199
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
signaldirs.append('Job_signal_1200_0p5/plotting_jobs/')

# process into TH1's
data_histos = util.get_flat_histo_collection(datadirs)
gjets_histos = util.get_flat_histo_collection(gjetsdirs)
dy_histos = util.get_flat_histo_collection(dydirs)
qcd_histos = util.get_flat_histo_collection(qcddirs)
signal_histos = util.get_flat_histo_collection(signaldirs)
col_signal_histos = util.get_histo_collection(signaldirs)
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
for signal_hist in signal_histos:
  if (signal_hist.GetName()).startswith('cutflow'):
    signal_hist.SetLineColor(signal_color)
    signal_hist.Draw()
    c.Print(cutflow)

# sanity plots
for data_hist, gjets_hist, dy_hist, qcd_hist, signal_hist in zip(data_histos, gjets_histos, dy_histos, qcd_histos, signal_histos):
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
  #if not signal_hist.Integral()==0: signal_hist.Scale(SIGNAL_NORM/signal_hist.Integral())
  if args.scale and not signal_hist.Integral()==0: signal_hist.Scale(1.0/signal_hist.Integral())
  signal_integral = signal_hist.Integral()
  signal_underflow = signal_hist.GetBinContent(0)
  signal_overflow = signal_hist.GetBinContent(signal_hist.GetNbinsX()+1)
  # color
  data_hist.SetLineColor(ROOT.kBlack)
  data_hist.Sumw2()
  gjets_hist.SetLineColor(gjets_color)
  gjets_hist.SetFillColor(gjets_color)
  dy_hist.SetLineColor(dy_color)
  dy_hist.SetFillColor(dy_color)
  qcd_hist.SetLineColor(qcd_color)
  qcd_hist.SetFillColor(qcd_color)
  signal_hist.SetLineColor(signal_color)
  # legend
  leg = ROOT.TLegend(0.7, 0.60, 0.9, 0.9)
  leg.AddEntry(data_hist, 'Data ({:,.0f})'.format(data_hist.Integral()), 'l')
  leg.AddEntry(hist_mcs[2], 'GJets ({:,.0f})'.format(gjets_hist.Integral()), 'f')
  leg.AddEntry(hist_mcs[0], 'DY m50 ({:,.0f})'.format(dy_hist.Integral()), 'f')
  leg.AddEntry(hist_mcs[1], 'QCD ({:,.0f})'.format(qcd_hist.Integral()), 'f')
  leg.AddEntry(signal_hist, 'Signal 500|eta ({:,.0f})'.format(signal_hist.Integral()), 'f')
  if not data_underflow==0 or not data_overflow==0: leg.AddEntry('', "Data uo {:,.0f},{:,.0f}".format(data_underflow, data_overflow), '')
  if not mc_underflow==0 or not mc_overflow==0: leg.AddEntry('', "MC uo {:,.0f},{:,.0f}".format(mc_underflow, mc_overflow), '')
  if not signal_underflow==0 or not signal_overflow==0: leg.AddEntry('', "Signal uo {:,.0f},{:,.0f}".format(signal_underflow, signal_overflow), '')
  # draw linear
  c.SetLogy(0)
  data_hist.Draw()
  stack.Draw('hist same')
  signal_hist.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
  # draw log
  c.SetLogy(1)
  data_hist.Draw()
  stack.Draw('hist same')
  signal_hist.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
c.Print(main+']')
c.Print(cutflow+']')

print('\nData Filter efficiencies:')
effs = util.get_effs(datadirs)
for dir, eff in zip(datadirs, effs):
  print(dir, eff)
