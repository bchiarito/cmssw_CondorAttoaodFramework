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
args = parser.parse_args()

# constants
plotting_jobs = 'plotting_jobs/'
gjets_color = ROOT.kGreen
dy_color = 41
ROOT.gStyle.SetOptStat(0)
main = args.out+'.pdf'
cutflow = args.out+'_cutflow.pdf'

# define job directories
datadirs = []
datadirs.append(args.prefix + 'egamma18a/' + plotting_jobs)
datadirs.append(args.prefix + 'egamma18b/' + plotting_jobs)
datadirs.append(args.prefix + 'egamma18c/' + plotting_jobs)
datadirs.append(args.prefix + 'egamma18d/' + plotting_jobs)
gjetsdirs = []
gjetsdirs.append(args.prefix + 'gjets40to100/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets100to200/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets200to400/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets400to600/' + plotting_jobs)
gjetsdirs.append(args.prefix + 'gjets600toInf/' + plotting_jobs)
dydirs = []
dydirs.append('Job_plotting2_dy50/')

# process into TH1's
data_histos = util.get_flat_histo_collection(datadirs)
gjets_histos = util.get_flat_histo_collection(gjetsdirs)
dy_histos = util.get_flat_histo_collection(dydirs)
col_gjets_histos = util.get_histo_collection(gjetsdirs)

# start pdf files
c = ROOT.TCanvas()
c.Print(main+'[')
c.Print(cutflow+'[')

# hthat plot for gjets
c.SetLogy()
for hists in zip(*col_gjets_histos):
  if not (hists[0].GetName()).startswith('MC_'): continue
  hists[0].SetLineColor(ROOT.kRed)
  hists[0].SetFillColor(ROOT.kRed)
  hists[0].Draw('hist')
  for i, hist in enumerate(hists[1:]):
    hist.SetLineColor(ROOT.kRed+(i+1))
    hist.SetFillColor(ROOT.kRed+(i+1))
    hist.Draw('hist same')
  c.Print(main)

# cutflow plots
c.SetLogy()
for data_hist in data_histos:
  if (data_hist.GetName()).startswith('cutflow'):
    data_hist.Draw()
    c.Print(cutflow)
for hists in zip(*col_gjets_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    for i, hist in enumerate(hists):
      hist.SetLineColor(ROOT.kRed+i)
      hist.SetFillColor(ROOT.kRed+i)
      hist.Draw('hist')
      c.Print(cutflow)

# sanity plots
for data_hist, gjets_hist, dy_hist in zip(data_histos, gjets_histos, dy_histos):
  if (data_hist.GetName()).startswith('MC_'): continue
  if (data_hist.GetName()).startswith('cutflow'): continue
  # prepare data
  if args.scale and not data_hist.Integral()==0: data_hist.Scale(1.0/data_hist.Integral())
  data_integral = data_hist.Integral()
  data_underflow = data_hist.GetBinContent(0)
  data_overflow = data_hist.GetBinContent(data_hist.GetNbinsX()+1)
  # prepare mc
  hist_mcs = [dy_hist, gjets_hist]
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
  # color
  data_hist.SetLineColor(ROOT.kBlack)
  data_hist.Sumw2()
  dy_hist.SetLineColor(dy_color)
  dy_hist.SetFillColor(dy_color)
  gjets_hist.SetLineColor(gjets_color)
  gjets_hist.SetFillColor(gjets_color)
  # legend
  leg = ROOT.TLegend(0.75, 0.75, 1.0, 1.0)
  leg.AddEntry(data_hist, 'Data', 'l')
  leg.AddEntry(hist_mcs[1], 'GJets', 'f')
  leg.AddEntry(hist_mcs[0], 'DY m50', 'f')
  if data_underflow==0 and data_overflow==0:
    leg.AddEntry('', "Data {:,.0f}".format(data_integral), '')
  else:
    leg.AddEntry('', "Data {:,.0f}, {:,.0f}|{:,.0f}".format(data_integral, data_underflow, data_overflow), '')
  if mc_underflow==0 and mc_overflow==0:
    leg.AddEntry('', "MC {:,.0f}".format(mc_integral), '')
  else:
    leg.AddEntry('', "MC {:,.0f}, {:,.0f}|{:,.0f}".format(mc_integral, mc_underflow, mc_overflow), '')
  # draw linear
  c.SetLogy(0)
  data_hist.Draw()
  stack.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
  # draw log
  c.SetLogy(1)
  data_hist.Draw()
  stack.Draw('hist same')
  data_hist.Draw("same")
  leg.Draw('same')
  c.Print(main)
c.Print(main+']')
c.Print(cutflow+']')

print('\nData Filter efficiencies:')
effs = util.get_effs(datadirs)
for dir, eff in zip(datadirs, effs):
  print(dir, eff)
