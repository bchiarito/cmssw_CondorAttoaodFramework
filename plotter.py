#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import imp
import argparse
import subprocess
from functools import reduce
import shutil
import ROOT
import helper.plotting_util as util

# constants
HADD_DIR_NAME = "hadd"
FULLSUM_PREFIX = 'fullsum'
main_pdf = '_main.pdf'
cutflow_pdf = '_cutflow.pdf'
signal_pdf = '_signal.pdf'
leg_x1, leg_y1, leg_x2, leg_y2 = 0.7, 0.60, 0.89, 0.9

# helper routines
def check_and_hadd(*paths):
    for path in paths:
        if not os.path.isdir(os.path.join(path, HADD_DIR_NAME)):
            subprocess.call("./hadd_histo_dirs.py --retain --rehadd " + path, shell=True)

def make_hist_collection(*jobdirs):
    hist_collection = []
    hist_collections = []
    for num, jobdir in enumerate(jobdirs):
        check_and_hadd(jobdir)
        rootfiles = [os.path.join(jobdir, HADD_DIR_NAME, filename) for filename in os.listdir(os.path.join(jobdir, HADD_DIR_NAME))]
        if jobdir.startswith('MultiJob_'): filenames = [filename for filename in rootfiles if not os.path.basename(filename).startswith(FULLSUM_PREFIX)]
        elif jobdir.startswith('Job_'): filenames = [filename for filename in rootfiles if os.path.basename(filename).startswith(FULLSUM_PREFIX)]
        else: raise SystemExit("directory "+jobdir+" does not start with MultiJob_ nor Job_!")
        tfiles = [ROOT.TFile(filename) for filename in filenames]
        global_var_name = jobdir.replace('/', '').replace('-','')+str(num)
        globals()["tfiles_"+global_var_name] = tfiles
        temp_hist_collection = [ [key.ReadObj() for key in file.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for file in tfiles ]
        hist_collections.append(temp_hist_collection)
        hist_collection.append(reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], temp_hist_collection))
    return reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], hist_collection), reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], hist_collections)

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from histo job directories")
input_arguments = parser.add_argument_group("input")
input_arguments.add_argument("--data", nargs='+', help='')
input_arguments.add_argument("--gjets", nargs='+', help='')
input_arguments.add_argument("--qcd", nargs='+', help='')
input_arguments.add_argument("--mc", nargs='+', help='')
input_arguments.add_argument("--signal", nargs='+', help='')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
parser.add_argument("-t", "--test", default=False, action='store_true', help='only one plot')
parser.add_argument("-g", "--scale_gjets", action='store_true', help='scale gjets up to data')
parser.add_argument("-s", "--scale", action='store_true', help='scale gjets up to data')
args = parser.parse_args()

# color and legends
data_legend = 'DATA'
data_color = ROOT.kBlack
gjets_legend = 'GJETS'
gjets_color = ROOT.kGreen
qcd_legend = 'QCD'
qcd_color = ROOT.kOrange
mc_legend = ['MC']*9
mc_color = [ROOT.kViolet, ROOT.kViolet+2] + [ROOT.kPink]*9
signal_color = [ROOT.kRed, ROOT.kBlue, ROOT.kYellow+1] + [ROOT.kTeal]*9
signal_legend = ['signal']*9

# init
cutflow_pdf = args.out + cutflow_pdf
signal_pdf = args.out + signal_pdf
main_pdf = args.out + main_pdf

# config
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)

# build histogram collections
if args.data: data_hist_collection, _ = make_hist_collection(*args.data)
if args.gjets: gjets_hist_collection, gjets_hist_collections = make_hist_collection(*args.gjets)
if args.qcd: qcd_hist_collection, qcd_hist_collections = make_hist_collection(*args.qcd)
if args.mc: mc_hist_collection, mc_hist_collections = make_hist_collection(*args.mc)
if args.signal: _, signal_hist_collections = make_hist_collection(*args.signal)

# plot
c = ROOT.TCanvas()
c.Print(main_pdf+'[')

if args.gjets:
    for hists in zip(*(gjets_hist_collections)):
      if not (hists[0].GetName()).startswith("GJETS_"): continue
      hists[0].SetLineColor(gjets_color)
      hists[0].SetFillColor(gjets_color)
      hists[0].SetMinimum(1.0)
      hists[0].SetMaximum(1e10)
      hists[0].Draw('hist')
      for j, hist in enumerate(hists[1:]):
        hist.SetLineColor(gjets_color+(j+1))
        hist.SetFillColor(gjets_color+(j+1))
        hist.Draw('hist same')
      c.SetLogy()
      c.Print(main_pdf)

if args.qcd:
    for hists in zip(*(qcd_hist_collections)):
      if not (hists[0].GetName()).startswith("QCD_"): continue
      hists[0].SetLineColor(qcd_color)
      hists[0].SetFillColor(qcd_color)
      hists[0].SetMinimum(1.0)
      hists[0].SetMaximum(1e10)
      hists[0].Draw('hist')
      for j, hist in enumerate(hists[1:]):
        hist.SetLineColor(qcd_color+(j+1))
        hist.SetFillColor(qcd_color+(j+1))
        hist.Draw('hist same')
      c.SetLogy()
      c.Print(main_pdf)

if args.scale_gjets:
    if not args.data or not args.gjets: raise SystemExit("Must use --data and --gjets with --scale_gjets !")
    data_count = data_hist_collection[0].GetEntries()
    gjets_count = gjets_hist_collection[0].GetEntries()
    mc_count = 0
    if args.qcd: mc_count += qcd_hist_collection[0].GetEntries()
    if args.mc:
        for k, hist_collection in enumerate(mc_hist_collections):
            mc_count+= hist_collection[0].GetEntries()
    gjets_k_factor = (data_count - mc_count) / gjets_count

if args.scale:
    mc_integral = 0
    if args.gjets: mc_integral += gjets_hist_collection[0].GetEntries()
    if args.qcd: mc_integral += qcd_hist_collection[0].GetEntries()
    if args.mc:
        for k, hist_collection in enumerate(mc_hist_collections):
            mc_integral += hist_collection[0].GetEntries()

for i in range(len(data_hist_collection)):
    if (data_hist_collection[i].GetName()).startswith('cutflow'): continue

    leg = ROOT.TLegend(leg_x1, leg_y1, leg_x2, leg_y2)
    data_hist = data_hist_collection[i]
    data_hist.SetLineColor(data_color)
    data_hist.Sumw2()
    if args.scale: data_hist.Scale(100.0 / data_hist.Integral())
    leg.AddEntry(data_hist, data_legend+' ({:,.0f})'.format(data_hist.Integral()), 'l')

    mc_stack = ROOT.THStack('hs', 'hs')
    if args.gjets:
        mc_hist = gjets_hist_collection[i]
        mc_hist.SetLineColor(gjets_color)
        mc_hist.SetFillColor(gjets_color)
        if args.scale_gjets: mc_hist.Scale(gjets_k_factor)
        if args.scale: mc_hist.Scale(100.0 / mc_integral)
        mc_stack.Add(mc_hist)
        if args.scale_gjets: leg.AddEntry(mc_hist, gjets_legend+' (k={:.3f}) ({:,.0f})'.format(gjets_k_factor, mc_hist.Integral()), 'f')
        else: leg.AddEntry(mc_hist, gjets_legend+' ({:,.0f})'.format(mc_hist.Integral()), 'f')
    if args.qcd:
        mc_hist = qcd_hist_collection[i]
        mc_hist.SetLineColor(qcd_color)
        mc_hist.SetFillColor(qcd_color)
        if args.scale: mc_hist.Scale(100.0 / mc_integral)
        mc_stack.Add(mc_hist)
        leg.AddEntry(mc_hist, qcd_legend+' ({:,.0f})'.format(mc_hist.Integral()), 'f')
    if args.mc:
        for k, hist_collection in enumerate(mc_hist_collections):
            mc_hist = hist_collection[i]
            mc_hist.SetLineColor(mc_color[k])
            mc_hist.SetFillColor(mc_color[k])
            if args.scale: mc_hist.Scale(100.0 / mc_integral)
            mc_stack.Add(mc_hist)
            leg.AddEntry(mc_hist, mc_legend[k]+' ({:,.0f})'.format(mc_hist.Integral()), 'f')

    signal_hists = []
    if args.signal:
        for k, coll in enumerate(signal_hist_collections):
            signal_hist = signal_hist_collections[k][i]
            signal_hist.SetLineColor(signal_color[k])
            signal_hists.append(signal_hist)
            if args.scale: signal_hist.Scale(100.0 / signal_hist.Integral())
            leg.AddEntry(signal_hist, signal_legend[k]+' ({:,.0f})'.format(signal_hist.Integral()), 'f')

    c.SetLogy(0)
    data_hist.SetMinimum(0)
    data_hist.Draw()
    mc_stack.Draw('hist same')
    for hist in signal_hists: hist.Draw("same")
    data_hist.Draw("same")
    leg.Draw('same')
    c.Print(main_pdf)

    c.SetLogy(1)
    data_hist.SetMinimum(1e-1)
    data_hist.Draw()
    mc_stack.Draw('hist same')
    for hist in signal_hists: hist.Draw("same")
    data_hist.Draw("same")
    leg.Draw('same')
    c.Print(main_pdf)

    if args.test: break

c.Print(main_pdf+']')
