#!/usr/bin/env python
import os
import sys
import imp
import argparse
from functools import reduce
import ROOT

# command line options
parser = argparse.ArgumentParser(description="")
# input/output
parser.add_argument("prefix", help='include Job_ part of jobdir, and final underscore')
parser.add_argument("--out", default='plots.pdf', help='name of output file')
parser.add_argument("--scale", action='store_true', default=False, help='scale data and mc to unit integral')
args = parser.parse_args()

def get_file(jobdir):
  job = imp.load_source("job", jobdir+"job_info.py")
  path = job.output
  print('got for path '+path)
  if not os.path.isfile(path+'/summed.root'):
    print('hadding '+jobdir)
    os.system('hadddir '+path+' '+path+'/summed.root')
  fi = ROOT.TFile(path+'/summed.root')
  return fi

datadirs = []
datadirs.append(args.prefix + 'egamma18a/')
datadirs.append(args.prefix + 'egamma18b/')
datadirs.append(args.prefix + 'egamma18c/')
datadirs.append(args.prefix + 'egamma18d/')
mcdirs = []
mcdirs.append(args.prefix + 'gjets40to100/')
mcdirs.append(args.prefix + 'gjets100to200/')
mcdirs.append(args.prefix + 'gjets200to400/')
mcdirs.append(args.prefix + 'gjets400to600/')
mcdirs.append(args.prefix + 'gjets600toInf/')

# process data into one list of TH1's
data_files = []
col_data_histos = []
for datadir in datadirs:
  data_file = get_file(datadir)
  data_files.append(data_file)
  col_data_histos.append( [key.ReadObj() for key in (data_file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()] )
data_histos = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_data_histos)  

# process mc into one list of TH1's
color = ROOT.kGreen
mc_files = []
col_mc_histos = []
for mc_jobdir in mcdirs:
  mc_file = get_file(mc_jobdir)
  mc_files.append(mc_file)
  col_mc_histos.append( [key.ReadObj() for key in (mc_file.GetListOfKeys()[0].ReadObj()).GetListOfKeys()] )
mc_histos = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], col_mc_histos)  
# make hthat plot
c = ROOT.TCanvas()
c.cd()
c.SetLogy()
c.Print(args.out+'[')
for hists in zip(*col_mc_histos):
  if (hists[0].GetName()).startswith('cutflow'):
    print("plotting mc "+hists[0].GetName())
    for i, hist in enumerate(hists):
      hist.SetLineColor(ROOT.kRed+i)
      hist.SetFillColor(ROOT.kRed+i)
      hist.Draw('hist')
      c.Print(args.out)
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
c.SetLogy(0)
for hist in mc_histos:
  hist.SetLineColor(color)
  hist.SetFillColor(color)

# add mcs into big collection
all_mc_histos = [mc_histos]

# main sanity plots
for hists in zip(data_histos, *all_mc_histos):
  if (hists[0].GetName()).startswith('MC_'): continue
  if (hists[0].GetName()).startswith('cutflow'):
    print("plotting data "+hists[0].GetName())
    c.SetLogy()
    hist_data = hists[0]
    hist_data.Draw()
    c.Print(args.out)
    c.SetLogy(0)
  else:
    print("plotting "+hists[0].GetName())
    leg = ROOT.TLegend(0.8, 0.8, 1.0, 1.0)
    hist_data = hists[0]
    hist_mcs = []
    for hist in hists[1:]:
      hist_mcs.append(hist)
    if args.scale and not hist_data.Integral()==0: hist_data.Scale(1.0/hist_data.Integral())
    data_integral = hist_data.Integral()
    data_underflow = hist_data.GetBinContent(0)
    data_overflow = hist_data.GetBinContent(hist_data.GetNbinsX()+1)
    hist_data.SetLineColor(ROOT.kBlack)
    hist_data.Sumw2()
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
    leg.AddEntry(hist_mcs[0], 'GJets', 'f')
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
c.Print(args.out+']')
