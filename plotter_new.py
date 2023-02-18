#!/usr/bin/env python
import os
import sys
import imp
import argparse
from functools import reduce
import ROOT
import plotting_util as util

# command line options
parser = argparse.ArgumentParser(description="")
# input/output
parser.add_argument("prefix", help='include Job_ part of jobdir, and final underscore')
parser.add_argument("--out", default='plots.pdf', help='name of output file')
parser.add_argument("--scale", action='store_true', default=False, help='scale data and mc to unit integral')
args = parser.parse_args()

# define job directories
plotting_jobs = 'plotting_jobs/'
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

# process data into one list of TH1's
data_files = []
col_data_histos = []
for datadir in datadirs:
  data_file = util.get_hadd(datadir)
  data_files.append(data_file)
  col_data_histos.append( [key.ReadObj() for key in (data_file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()] )
  metadata = util.get_meta(os.path.join(os.path.dirname(os.path.dirname(datadir)),''))
  total = float(metadata['evtProcessed']); passfilter = float(metadata['evtPassDatafilter'])
  print(datadir + " data filter efficiency: " + str(passfilter/total))
data_histos = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_data_histos)  

# process gjets into one list of TH1's
gjets_files = []
col_gjets_histos = []
for mc_jobdir in gjetsdirs:
  mc_file = util.get_hadd(mc_jobdir)
  gjets_files.append(mc_file)
  col_gjets_histos.append( [key.ReadObj() for key in (mc_file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()] )
gjets_histos = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_gjets_histos)  

# process dy into one list of TH1's
dy_files = []
col_dy_histos = []
for mc_jobdir in dydirs:
  mc_file = util.get_hadd(mc_jobdir)
  dy_files.append(mc_file)
  col_dy_histos.append( [key.ReadObj() for key in (mc_file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()] )
dy_histos = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_dy_histos)  

# add mcs into big collection
all_mc_histos = [gjets_histos, dy_histos]

# style
ROOT.gStyle.SetOptStat(0)

# make gjets hthat plot
c = ROOT.TCanvas('c1','c1')
c.SetLogy()
c.Print('aux.pdf[')
c.Print(args.out+'[')
for hists in zip(*col_gjets_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    print("plotting mc "+hists[0].GetName())
    for i, hist in enumerate(hists):
      hist.SetLineColor(ROOT.kRed+i)
      hist.SetFillColor(ROOT.kRed+i)
      hist.Draw('hist')
      c.Print('aux.pdf')
  else:
    if not (hists[0].GetName()).startswith('MC_'): continue
    print("plotting "+hists[0].GetName())
    hists[0].SetLineColor(ROOT.kRed)
    hists[0].SetFillColor(ROOT.kRed)
    hists[0].Draw('hist')
    for i, hist in enumerate(hists[1:]):
      hist.SetLineColor(ROOT.kRed+(i+1))
      hist.SetFillColor(ROOT.kRed+(i+1))
      hist.Draw('hist same')
    c.Print(args.out)

# main sanity plots
c.SetLogy(0)
color = ROOT.kGreen
for hist in gjets_histos:
  hist.SetLineColor(color)
  hist.SetFillColor(color)
color = ROOT.kRed
for hist in dy_histos:
  hist.SetLineColor(color)
  hist.SetFillColor(color)
#for hists in zip(data_histos, *all_mc_histos):
for data_hist, gjets_hist, dy_hist in zip(data_histos, gjets_histos, dy_histos):
  if (data_hist.GetName()).startswith('MC_'): continue
  if (data_hist.GetName()).startswith('cutflow'):
    print("plotting data "+data_hist.GetName())
    c.SetLogy()
    hist_data = data_hist
    hist_data.Draw()
    c.Print('aux.pdf')
  else:
    print("plotting "+data_hist.GetName())
    leg = ROOT.TLegend(0.75, 0.75, 1.0, 1.0)
    hist_data = data_hist
    hist_mcs = [dy_hist, gjets_hist]
    if args.scale and not hist_data.Integral()==0: hist_data.Scale(1.0/hist_data.Integral())
    data_integral = hist_data.Integral()
    data_underflow = hist_data.GetBinContent(0)
    data_overflow = hist_data.GetBinContent(hist_data.GetNbinsX()+1)
    hist_data.SetLineColor(ROOT.kBlack)
    hist_data.Sumw2()
    # draw linear
    c.SetLogy(0)
    hist_data.Draw()
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
    stack.Draw('hist same')
    hist_data.Draw("same")
    leg.AddEntry(hist_data, 'Data', 'l')
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
    leg.Draw('same')
    c.Print(args.out)
    # draw log
    c.SetLogy(1)
    hist_data.Draw()
    stack.Draw('hist same')
    hist_data.Draw("same")
    leg.Draw('same')
    c.Print(args.out)
c.Print(args.out+']')
c.Print('aux.pdf]')
