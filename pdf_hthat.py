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
mc_dirs_list = []
mc_color = []
mc_legend = []
mc_hat_tag = []

# command line options
parser = argparse.ArgumentParser(description="Makes pdf from atto+nano job directories")
parser.add_argument("prefix", help='prefix of job directories, include "Job_" part')
parser.add_argument("--out", default='plots', help='prefix for the output pdf files')
args = parser.parse_args()

# other config
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kRed, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)
leg_x1, leg_x2, leg_y1, leg_y2 = 0.7, 0.60, 0.9, 0.9
main = args.out+'.pdf'
cutflow = args.out+'_cutflow.pdf'

# mc config
mc_legend.append('GJets')
mc_hat_tag.append('GJETS_')
mc_color.append(ROOT.kGreen)
mc_dirs_list.append([
  args.prefix+'gjets40to100/'+plotting_jobs,
  args.prefix+'gjets100to200/'+plotting_jobs,
  args.prefix+'gjets200to400/'+plotting_jobs,
  args.prefix+'gjets400to600/'+plotting_jobs,
  args.prefix+'gjets600toInf/'+plotting_jobs,
])

############################
c = ROOT.TCanvas()

mc_hist_collections = [util.get_flat_histo_collection(mc_dirs) for mc_dirs in mc_dirs_list]
mc_hists_collections = [util.get_histo_collection(mc_dirs) for mc_dirs in mc_dirs_list]

c.Print(main+'[')
# mc hat plots
c.SetLogy()
for i in range(len(mc_hat_tag)):
  if mc_hat_tag[i] == False: continue
  for hists in zip(*(mc_hists_collections[i])):
    if not (hists[0].GetName()).startswith(mc_hat_tag[i]): continue
    hists[0].SetLineColor(mc_color[i])
    hists[0].SetFillColor(mc_color[i])
    hists[0].SetMinimum(1.0)
    #hists[0].GetYaxis().SetRangeUser(1e3, 1e9)
    hists[0].Draw('hist')
    for j, hist in enumerate(hists[1:]):
      hist.SetLineColor(mc_color[i]+(j+1))
      hist.SetFillColor(mc_color[i]+(j+1))
      hist.Draw('hist same')
    c.Print(main)
c.Print(main+']')
