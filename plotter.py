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
import cross_sections as XS

NAME_COUNT = 0
def getname(prefix='obj'):
  global NAME_COUNT
  NAME_COUNT += 1
  return prefix+str(NAME_COUNT)

def check_and_hadd(paths):
    for path in paths:
        if not os.path.isdir(os.path.join(path, HADD_DIR_NAME)):
            subprocess.call("./hadd_histo_dirs.py --retain --rehadd " + path, shell=True)

def scale_collections(hist_collections, ngens, xses, lumi, o1, o2):
    for coll, ngen, o1e, o2e in zip(hist_collections, ngens, o1, o2):
        if not o1==o2: raise SystemExit()
        xs = -1
        for e in xses:
            if e in o1e: xs = xses[e]
        sf = xs * lumi / ngen
        for hist in coll:
            hist.Scale(sf)

def make_hist_collections(jobdirs, ngen=None):
    if jobdirs == None: return [[]], []
    jobdir = jobdirs[0]
    check_and_hadd(jobdirs)
    rootfiles = [os.path.join(jobdir, HADD_DIR_NAME, filename) for filename in os.listdir(os.path.join(jobdir, HADD_DIR_NAME))]
    if jobdir.startswith('MultiJob_'): filenames = [filename for filename in rootfiles if not os.path.basename(filename).startswith(FULLSUM_PREFIX)]
    #elif jobdir.startswith('Job_'):    filenames = [filename for filename in rootfiles if     os.path.basename(filename).startswith(FULLSUM_PREFIX)]
    else: raise SystemExit("directory "+jobdir+" does not start with MultiJob_ nor Job_!")
    if len(filenames) == 0: return [[]], []
    tfiles = [ROOT.TFile(filename) for filename in filenames]
    if ngen:
        temp = [ [key.ReadObj().GetBinContent(1) for key in tfile.GetListOfKeys()[0].ReadObj().GetListOfKeys() if key.ReadObj().GetName().startswith('cutflow')] for tfile in tfiles ]
        return [entry[0] for entry in temp], [os.path.basename(tfile.GetName()) for tfile in tfiles]
    temp_hist_collections = [ [key.ReadObj() for key in tfile.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for tfile in tfiles ]
    global_var_name = jobdir.replace('/', '').replace('-','')+str(0)
    globals()["tfiles_"+global_var_name] = tfiles
    return temp_hist_collections, [os.path.basename(tfile.GetName()) for tfile in tfiles]

def make_hist_collections_from_file(*filenames):
    tfiles = [ROOT.TFile(filename) for filename in filenames]
    temp_hist_collections = [ [key.ReadObj() for key in tfile.GetListOfKeys()[0].ReadObj().GetListOfKeys()] for tfile in tfiles ]
    global_var_name = getname()
    globals()["tfiles_"+global_var_name] = tfiles
    return temp_hist_collections, [os.path.basename(tfile.GetName()) for tfile in tfiles]

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from histo job directories")
input_arguments = parser.add_argument_group("input")
input_arguments.add_argument("--data", nargs='*', help='')
input_arguments.add_argument("--gjets", nargs='*', help='')
input_arguments.add_argument("--qcd", nargs='*', help='')
input_arguments.add_argument("--mc", nargs='*', help='')
input_arguments.add_argument("--mcleg", nargs='*', help='')
input_arguments.add_argument("--signal", nargs='*', help='')
input_arguments.add_argument("--signalleg", nargs='*', help='')
parser.add_argument("--out", default='figs', help='prefix for the output pdf files')
parser.add_argument("-y", "--year", choices=['18','17','16'], help='')
parser.add_argument("--lumi", type=float, help='to override year lumi')
parser.add_argument("-t", "--test", default=False, action='store_true', help='only one plot')
parser.add_argument("-c", "--cutflow_only", default=False, action='store_true', help='')
parser.add_argument("--hthat_only", default=False, action='store_true', help='')
parser.add_argument("-g", "--scale_gjets", action='store_true', default=False, help='scale gjets up to data')
parser.add_argument("-s", "--scale", action='store_true', default=False, help='scale gjets up to data')
parser.add_argument("--nolumiweight", action='store_true', default=False, help='')
args = parser.parse_args()

# init
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)
HADD_DIR_NAME = "hadd"
FULLSUM_PREFIX = 'fullsum'
main_pdf = '_main.pdf'
cutflow_pdf = '_cutflow.pdf'
signal_pdf = '_signal.pdf'
leg_x1, leg_y1, leg_x2, leg_y2 = 0.7, 0.60, 0.89, 0.9
data_legend = 'Data'
data_color = ROOT.kBlack
gjets_legend = 'GJets'
gjets_color = ROOT.kGreen
qcd_legend = 'QCD'
qcd_color = ROOT.kOrange
mc_legend = args.mcleg if args.mcleg else ['MC']*9
mc_color = [ROOT.kViolet, ROOT.kViolet+2] + [ROOT.kPink]*9
signal_color = [ROOT.kRed, ROOT.kBlue, ROOT.kYellow+1] + [ROOT.kTeal]*9
signal_legend = ['signal']*9
signal_legend = args.signalleg if args.signalleg else ['MC']*9
cutflow_pdf = args.out + cutflow_pdf
signal_pdf = args.out + signal_pdf
main_pdf = args.out + main_pdf
if args.year == '18':
    lumi = XS.LUMI_UL18
    title = "UL18 {:,.0f} /pb".format(lumi)
elif args.year == '17':
    lumi = XS.LUMI_UL17
    title = "UL17 {:,.0f} /pb".format(lumi)
else:
    lumi = 1.0
    title = ""
if args.lumi: lumi = args.lumi

# build histogram collections
#data_hist_collections, _ = make_hist_collections(args.data)
data_hist_collections, _ = make_hist_collections_from_file("data.root")

print(type(data_hist_collections))
print(len(data_hist_collections))

data_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], data_hist_collections[1:], [hist.Clone() for hist in data_hist_collections[0]])

gjets_hist_collections, order1 = make_hist_collections(args.gjets)
if not args.nolumiweight:
    gjets_ngen, order2 = make_hist_collections(args.gjets, ngen=True)
    scale_collections(gjets_hist_collections, gjets_ngen, XS.GJETS, lumi, order1, order2)
gjets_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], gjets_hist_collections[1:], [hist.Clone() for hist in gjets_hist_collections[0]])

qcd_hist_collections, _ = make_hist_collections(args.qcd)
qcd_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], qcd_hist_collections, [hist.Clone() for hist in qcd_hist_collections[0]])

mc_hist_collections, _ = make_hist_collections(args.mc)
mc_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], mc_hist_collections, [hist.Clone() for hist in mc_hist_collections[0]])

signal_hist_collections, _ = make_hist_collections(args.signal)
signal_hist_collection = reduce(lambda a,b: [x.Add(x,y) and x for x,y in zip(a,b)], signal_hist_collections, [hist.Clone() for hist in signal_hist_collections[0]])



# compute scale factors
if args.scale_gjets:
    if not args.data or not args.gjets: raise SystemExit("Must use --data and --gjets with --scale_gjets !")
    data_count = data_hist_collection[0].Integral()
    gjets_count = gjets_hist_collection[0].Integral()
    mc_count = 0
    if args.qcd: mc_count += qcd_hist_collection[0].Integral()
    if args.mc:
        for k, hist_collection in enumerate(mc_hist_collections):
            mc_count+= hist_collection[0].Integral()
    gjets_k_factor = (data_count - mc_count) / gjets_count
    print("k_Factor:", gjets_k_factor)

if args.scale:
    mc_integral = 0
    if args.gjets: mc_integral += gjets_hist_collection[0].GetEntries()
    if args.qcd: mc_integral += qcd_hist_collection[0].GetEntries()
    if args.mc:
        for k, hist_collection in enumerate(mc_hist_collections):
            mc_integral += hist_collection[0].GetEntries()

# plot
c = ROOT.TCanvas()

# cutflow
if not args.hthat_only:
    c.Print(cutflow_pdf+'[')
    c.SetLogy(1)
    for i in range(len(data_hist_collection)):
        if not (data_hist_collection[i].GetName()).startswith('cutflow'): continue
        data_hist = data_hist_collection[i]
        data_hist.SetLineColor(data_color)
        data_hist.SetTitle(data_legend)
        data_hist.Draw()
        c.Print(cutflow_pdf)
    if args.gjets:
        gjets_sf = []
        for hists in zip(*(gjets_hist_collections)):
          if not (hists[0].GetName()).startswith('cutflow'): continue
          for j, hist in enumerate(hists):
            hist.SetLineColor(gjets_color+(j+1))
            hist.SetFillColor(gjets_color+(j+1))
            hist.SetTitle(gjets_legend)
            hist.Draw('hist')
            c.Print(cutflow_pdf)
    c.Print(cutflow_pdf+']')
    if args.cutflow_only: sys.exit()

# hthat
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
if args.hthat_only:
    c.Print(main_pdf+']')
    sys.exit()

# main
total_num_hist = max(len(data_hist_collection), len(gjets_hist_collection), len(qcd_hist_collection), len(mc_hist_collection), len(signal_hist_collections))
for i in range(total_num_hist):
    try:
        leg = ROOT.TLegend(leg_x1, leg_y1, leg_x2, leg_y2)

        if args.data:
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
        if args.data:
            first_hist = data_hist
            first_draw = data_hist
        elif args.gjets:
            first_hist = gjets_hist_collection[i]
            first_draw = mc_stack
            mc_stack.Draw()
        elif args.qcd: first_hist = qcd_hist_collection[i]
        elif args.mc: first_hist = mc_hist_collection[i]
        elif args.signal: first_hist = signal_hists[0]
        else: raise SystemExit()

        if (first_hist.GetName()).startswith('cutflow'): continue
        if (first_hist.GetName()).startswith('GJETS'): continue
        if (first_hist.GetName()).startswith('QCD'): continue
        if (first_hist.GetName()).startswith('SIGNAL'): continue

        print(first_hist.GetTitle(), first_hist.GetName())
        first_draw.GetXaxis().SetTitle(first_hist.GetTitle())
        first_draw.GetYaxis().SetTitle("Events" if not args.scale else "Scaled to Integral = 100")
        first_draw.SetTitle(title)

        c.SetLogy(0)
        first_draw.SetMinimum(0)
        first_draw.Draw()
        mc_stack.Draw('hist same NOCLEAR')
        for hist in signal_hists: hist.Draw("same")
        if args.data: data_hist.Draw('same')
        leg.Draw('same')
        c.Print(main_pdf)

        first_draw.SetMinimum(1e-1)
        c.SetLogy(1)
        first_draw.Draw()
        mc_stack.Draw('hist same NOCLEAR')
        for hist in signal_hists: hist.Draw("same")
        if args.data: data_hist.Draw('same')
        leg.Draw('same')
        c.Print(main_pdf)
    except RuntimeWarning:
        print('RuntimeWarning on ', gjets_hist_collection[i].GetName())
    except IndexError:
        print("!! Skipping plotting of histo", data_hist.GetName())
    if args.test and i>=1: break

c.Print(main_pdf+']')
