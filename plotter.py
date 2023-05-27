import math
import ROOT
import sys
import os
import argparse
import array
import fitting_utils as util


# Function for fitting specific pt-bin histogram
def fitfunc(x, p):
    norm = p[0]
    mpv = p[1]
    sigma = p[2]
    C1 = p[3]
    C2 = p[4]
    bound1 = p[5]
    bound2 = p[6]
   
    land = norm * ROOT.TMath.Landau(x[0], mpv, sigma)
  
    y11=norm*ROOT.TMath.Landau(bound1, mpv, sigma);
    y12=ROOT.TMath.Exp(C1*bound1)
    if y12 == 0: exp1 = 1000000000000
    else: exp1 = ROOT.TMath.Exp(C1*x[0])*y11/y12
     
    if y12 == 0: y21 = 1000000000000
    else: y21=ROOT.TMath.Exp(C1*bound2)*y11/y12
    y22=ROOT.TMath.Exp(C2*bound2)
    if y22 == 0: exp2 = 1000000000000
    else: exp2=ROOT.TMath.Exp(C2*x[0])*y21/y22
     
    if x[0] < bound1: return land
    elif x[0] < bound2: return exp1
    else: return exp2


# command line options
parser = argparse.ArgumentParser(description="")
parser.add_argument("input", metavar="INPUT", help="input root file")

# plot specification
parser.add_argument("--sanity", "-s", default=False, action="store_true", help="create sanity plots")
parser.add_argument("--test", default=False, action="store_true", help="create test plots")

# parse args
args = parser.parse_args()

infile1 = ROOT.TFile(sys.argv[1])

# other config
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetLegendFillColor(ROOT.TColor.GetColorTransparent(ROOT.kWhite, 0.01));
ROOT.gStyle.SetLegendBorderSize(0)
leg_x1, leg_x2, leg_y1, leg_y2 = 0.7, 0.60, 0.89, 0.89

c1 = ROOT.TCanvas("c1", "c1", 800, 600)
#if not args.sanity: ROOT.TPad.Divide(c1, 1, 2)
c1.Print("plots.pdf[")

# pi0: masspi0 plots for all eta regions, barrel, and endcap; pi0_bins: pt-binned masspi0 plots in barrel and endcap; overlay; pt-binned plots with overlayed ratios for each twoprong region
sanity_plots = ["sieie", "pfRelIso03_chg", "hadTow"]  
main_plots = ["pi0_bins"]
test_plots = ["pi0_bins"]
if args.sanity: plots = sanity_plots
elif args.test: plots = test_plots
else: plots = main_plots

eta_regions = ["all", "barrel", "endcap"]
regions = ["iso_asym", "noniso_sym", "noniso_asym"]
test_regions = ["noniso_sym"]
if args.test: regions = test_regions
photon_regions = ["tight", "loose"]
bins = [20,40,60,70,80,100,120,140,160,180,200,240,300,380,460]


for item in plots:
    if item == "pfRelIso03_chg" or item == "sieie" or item == "hoe" or item == "hadTow":  # sanity plots
        for region in photon_regions:
            iso_sym = "photon_" + region + "_" + item + "_iso_sym"
            iso_asym = "photon_" + region + "_" + item + "_iso_asym"
            noniso_sym = "photon_" + region + "_" + item + "_noniso_sym"
            noniso_asym = "photon_" + region + "_" + item + "_noniso_asym"

            h_iso_sym = infile1.Get("plots/" + iso_sym)
            h_iso_asym = infile1.Get("plots/" + iso_asym)
            h_noniso_sym = infile1.Get("plots/" + noniso_sym)
            h_noniso_asym = infile1.Get("plots/" + noniso_asym)

            h_iso_sym.SetLineColor(ROOT.kRed)
            h_iso_asym.SetLineColor(ROOT.kBlack)
            h_noniso_sym.SetLineColor(ROOT.kGreen+2)
            h_noniso_asym.SetLineColor(ROOT.kBlue)

            if not h_iso_sym.Integral() == 0: h_iso_sym.Scale(1.0/h_iso_sym.Integral())
            if not h_noniso_sym.Integral() == 0: h_noniso_sym.Scale(1.0/h_noniso_sym.Integral())
            if not h_iso_asym.Integral() == 0: h_iso_asym.Scale(1.0/h_iso_asym.Integral())
            if not h_noniso_asym.Integral() == 0: h_noniso_asym.Scale(1.0/h_noniso_asym.Integral())
            
            # Legend creation
            legend = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2) 
            legend.AddEntry(h_noniso_asym, "NonIso_Asym TwoProng", "l")
            legend.AddEntry(h_iso_sym, "Iso_Sym TwoProng", "l")
            legend.AddEntry(h_iso_asym, "Iso_Asym TwoProng", "l")
            legend.AddEntry(h_noniso_sym, "NonIso_Sym TwoProng", "l")

            title = region + " Photon"
            h_iso_sym.SetTitle(title)

            # Draw plots
            c1.cd(1)
            h_iso_sym.Draw("e")
            h_noniso_asym.Draw("samee")
            h_iso_asym.Draw("samee")
            h_noniso_sym.Draw("samee")
            ROOT.gPad.SetLogy()
            if item == "eta": ROOT.gPad.SetGridx(1)
            legend.Draw("same")

            if item == "sieie": h_iso_sym.GetXaxis().SetRangeUser(0, 0.1)
            elif item == "hoe" and region == "tight": h_iso_sym.GetXaxis().SetRangeUser(0, 0.4)
            elif item == "hoe" and region == "loose": h_iso_sym.GetXaxis().SetRangeUser(0, 2)
            elif item == "pfRelIso03_chg" and region == "tight": h_iso_sym.GetXaxis().SetRangeUser(0, 0.1)
            elif item == "pfRelIso03_chg" and region == "loose": h_iso_sym.GetXaxis().SetRangeUser(0, 0.2)
            elif item == "hadTow" and region == "tight": h_iso_sym.GetXaxis().SetRangeUser(0, 0.1) 
            elif item == "hadTow" and region == "loose": h_iso_sym.GetXaxis().SetRangeUser(0, 0.2) 
            c1.Print("plots.pdf")
    elif item == "pi0":  # un-pt-binned massPi0 plots
        ROOT.TPad.Divide(c1, 1, 2)
        for region in regions:  # loop through twoprong regions
            for eta_reg in eta_regions:  # loop through eta regions for a fixed twoprong sideband
                if not eta_reg == "barrel" and not eta_reg == "endcap":
                    h_egamma_tight = infile1.Get("plots/twoprong_masspi0_" + region + "_tight")
                    h_egamma_loose = infile1.Get("plots/twoprong_masspi0_" + region + "_loose")
                else:
                    h_egamma_tight = infile1.Get("plots/twoprong_masspi0_" + region + "_" + eta_reg + "_tight")
                    h_egamma_loose = infile1.Get("plots/twoprong_masspi0_" + region + "_" + eta_reg + "_loose")
                
                h_egamma_tight.SetLineColor(ROOT.kBlack)
                h_egamma_loose.SetLineColor(ROOT.kGreen+2)
                h_egamma_loose.SetFillColor(ROOT.kGreen+2)
                 
                if not h_egamma_tight.Integral() == 0: h_egamma_tight.Scale(1.0/h_egamma_tight.Integral())
                if not h_egamma_loose.Integral() == 0: h_egamma_loose.Scale(1.0/h_egamma_loose.Integral())
                
                h_ratio = h_egamma_tight.Clone()
                h_ratio.Reset()
                h_ratio.SetLineColor(ROOT.kBlack)
                h_ratio.Divide(h_egamma_tight, h_egamma_loose)
               
                # Create title for plot 
                title = region + " Twoprong"
                if eta_reg == "barrel": title += ", Barrel"
                elif eta_reg == "endcap": title += ", Endcap"
               
                # Legend creation
                legend = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2)
                legend.AddEntry(h_egamma_tight, "Tight Photon, " + str(h_egamma_tight.GetEntries()), "l")
                legend.AddEntry(h_egamma_loose, "Loose Photon, " + str(h_egamma_loose.GetEntries()), "f")

                h_egamma_tight.SetTitle(title)
                h_ratio.SetTitle("Tight / Loose Photon")  
                
                # Draw plots
                c1.cd(1)
                h_egamma_tight.Draw("")
                mc_stack = ROOT.THStack('hs', 'hs')
                mc_stack.Add(h_egamma_loose)
                mc_stack.Draw("hist same")
                h_egamma_tight.Draw("samee")
                ROOT.gPad.SetLogy()
                h_egamma_tight.GetXaxis().SetRangeUser(0, 26)
                legend.Draw("same")
                
                c1.cd(2)
                h_ratio.Draw("e")
                h_ratio.GetXaxis().SetRangeUser(0, 26)
                h_ratio.GetYaxis().SetRangeUser(-2, 4)
                h_ratio.SetStats(0)
                ROOT.gPad.SetGridy(1)
                ROOT.gPad.Update()
                c1.Print("plots.pdf")    
    elif item == "pi0_bins":
        for region in regions:  # loop through twoprong sideband regions
            for i in range(len(bins)):  # loop through pt bins for a fixed twoprong sideband
                for eta_reg in eta_regions:  # loop through eta regions for fixed pt-bin and fixed twoprong sideband
                    if not eta_reg == "barrel" and not eta_reg == "endcap": continue  # no pt-bin plots for barrel and endcap combined, so skip this case

                    # Generate correct plots names to access from summed histogram files
                    egamma_tight_plots = "plots/twoprong_masspi0_" + region + "_" + eta_reg
                    egamma_loose_plots = "plots/twoprong_masspi0_" + region + "_" + eta_reg
                
                    if i == len(bins) - 1:
                        egamma_tight_plots += "_" + str(bins[i]) + "+"
                        egamma_loose_plots += "_" + str(bins[i]) + "+"
                    else:
                        egamma_tight_plots += "_" + str(bins[i]) + "_" + str(bins[i+1])
                        egamma_loose_plots += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    
                    # Reference name of the histogram created in the backend 
                    egamma_tight_plots += "_tight"
                    egamma_loose_plots += "_loose"
                    
                    # Get the histograms from the input file
                    h_egamma_tight = infile1.Get(egamma_tight_plots)
                    h_egamma_loose = infile1.Get(egamma_loose_plots)
                    
                    # Configure display options
                    h_egamma_tight.SetLineColor(ROOT.kBlack)
                    h_egamma_loose.SetLineColor(ROOT.kBlue+1)
                    
                    print("BEGINNING OF PT BIN: " + str(bins[i]))
                    # Fit loose histogram to a curve
                    f2 = ROOT.TF1('f2', fitfunc, 0, 50, 7)
                    f2.SetParNames("Constant","MPV","Sigma","C1","C2","Boundary1","Boundary2")
                    f2.SetParameters(h_egamma_loose.GetEntries(), h_egamma_loose.GetMean(), 0.5, -3, -1, h_egamma_loose.GetMean()+0.5, h_egamma_loose.GetMean()*3)
                    h_egamma_loose.Fit(f2, 'L', "", 0, 15)

                    h_fitted_egamma_loose = util.TemplateToHistogram(f2, 300, 0, 50)
                    h_egamma_tight.Reset()
                    h_egamma_tight = h_fitted_egamma_loose.Clone()

                    # Create title for plot 
                    title = region + " Twoprong"
                    if eta_reg == "barrel": title += ", Barrel"
                    elif eta_reg == "endcap": title += ", Endcap"
                    if i == len(bins) - 1: title += ", pt > " + str(bins[i])
                    else: title += ", " + str(bins[i]) + " < pt < " + str(bins[i+1])
                   
                    # Legend creation
                    legend = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2)
                    #legend.AddEntry(h_egamma_tight, "Tight Photon, " + str(h_egamma_tight.GetEntries()), "l")
                    legend.AddEntry(h_egamma_tight, "Fitted Loose Photon, " + str(h_egamma_tight.GetEntries()), "l")
                    legend.AddEntry(h_egamma_loose, "Loose Photon, " + str(h_egamma_loose.GetEntries()), "l")

                    h_egamma_loose.SetTitle(title)
                    h_egamma_loose.SetMaximum()
                    
                    # Draw plots
                    c1.cd(1)
                    h_egamma_loose.Draw()  # draw data first so that it appears over the mc
                    h_egamma_tight.Draw("hist same")
                    h_egamma_loose.Draw("hist same")  # this is where the data is actually drawn to the canvas
                    ROOT.gPad.SetLogy()
                    h_egamma_loose.GetXaxis().SetRangeUser(0, 26)
                    legend.Draw("same")
                    ROOT.gPad.Update()
                    c1.Print("plots.pdf")    
    elif item == "overlay":
        for i in range(len(bins)):
            for eta_reg in eta_regions:
                if not eta_reg == "barrel" and not eta_reg == "endcap": continue
                else:
                    egamma_iso_sym_tight = "plots/twoprong_masspi0_iso_sym_" + eta_reg
                    egamma_iso_asym_tight = "plots/twoprong_masspi0_iso_asym_" + eta_reg
                    egamma_noniso_sym_tight = "plots/twoprong_masspi0_noniso_sym_" + eta_reg
                    egamma_noniso_asym_tight = "plots/twoprong_masspi0_noniso_asym_" + eta_reg
                    egamma_iso_sym_loose = "plots/twoprong_masspi0_iso_sym_" + eta_reg
                    egamma_iso_asym_loose = "plots/twoprong_masspi0_iso_asym_" + eta_reg
                    egamma_noniso_sym_loose = "plots/twoprong_masspi0_noniso_sym_" + eta_reg
                    egamma_noniso_asym_loose = "plots/twoprong_masspi0_noniso_asym_" + eta_reg
            
                if i == len(bins) - 1:
                    egamma_iso_sym_tight += "_" + str(bins[i]) + "+"
                    egamma_iso_asym_tight += "_" + str(bins[i]) + "+"
                    egamma_noniso_sym_tight += "_" + str(bins[i]) + "+" 
                    egamma_noniso_asym_tight += "_" + str(bins[i]) + "+"  
                    egamma_iso_sym_loose += "_" + str(bins[i]) + "+"
                    egamma_iso_asym_loose += "_" + str(bins[i]) + "+"
                    egamma_noniso_sym_loose += "_" + str(bins[i]) + "+" 
                    egamma_noniso_asym_loose += "_" + str(bins[i]) + "+"  
                else:
                    egamma_iso_sym_tight += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_iso_asym_tight += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_noniso_sym_tight += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_noniso_asym_tight += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_iso_sym_loose += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_iso_asym_loose += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_noniso_sym_loose += "_" + str(bins[i]) + "_" + str(bins[i+1])
                    egamma_noniso_asym_loose += "_" + str(bins[i]) + "_" + str(bins[i+1])
              
                h_egamma_iso_sym_tight = infile1.Get(egamma_iso_sym_tight + "_tight")
                h_egamma_iso_asym_tight = infile1.Get(egamma_iso_asym_tight + "_tight")
                h_egamma_noniso_sym_tight = infile1.Get(egamma_noniso_sym_tight + "_tight")
                h_egamma_noniso_asym_tight = infile1.Get(egamma_noniso_asym_tight + "_tight")
                h_egamma_iso_sym_loose = infile1.Get(egamma_iso_sym_loose + "_loose")
                h_egamma_iso_asym_loose = infile1.Get(egamma_iso_asym_loose + "_loose")
                h_egamma_noniso_sym_loose = infile1.Get(egamma_noniso_sym_loose + "_loose")
                h_egamma_noniso_asym_loose = infile1.Get(egamma_noniso_asym_loose + "_loose")

                h_egamma_tight = h_egamma_iso_sym_tight.Clone()
                h_egamma_tight.Add(h_egamma_iso_asym_tight)
                h_egamma_tight.Add(h_egamma_noniso_sym_tight)
                h_egamma_tight.Add(h_egamma_noniso_asym_tight)
                h_egamma_tight.SetLineColor(ROOT.kBlack)
                h_egamma_loose = h_egamma_iso_sym_loose.Clone()
                h_egamma_loose.Add(h_egamma_iso_asym_loose)
                h_egamma_loose.Add(h_egamma_noniso_sym_loose)
                h_egamma_loose.Add(h_egamma_noniso_asym_loose)
                h_egamma_loose.SetLineColor(ROOT.kGreen+2)
                h_egamma_loose.SetFillColor(ROOT.kGreen+2)
                
                if not h_egamma_iso_sym_tight.Integral() == 0: h_egamma_iso_sym_tight.Scale(1.0/h_egamma_iso_sym_tight.Integral())
                if not h_egamma_iso_asym_tight.Integral() == 0: h_egamma_iso_asym_tight.Scale(1.0/h_egamma_iso_asym_tight.Integral())
                if not h_egamma_noniso_sym_tight.Integral() == 0: h_egamma_noniso_sym_tight.Scale(1.0/h_egamma_noniso_sym_tight.Integral())
                if not h_egamma_noniso_asym_tight.Integral() == 0: h_egamma_noniso_asym_tight.Scale(1.0/h_egamma_noniso_asym_tight.Integral())
                if not h_egamma_tight.Integral() == 0: h_egamma_tight.Scale(1.0/h_egamma_tight.Integral())

                if not h_egamma_iso_sym_loose.Integral() == 0: h_egamma_iso_sym_loose.Scale(1.0/h_egamma_iso_sym_loose.Integral())
                if not h_egamma_iso_asym_loose.Integral() == 0: h_egamma_iso_asym_loose.Scale(1.0/h_egamma_iso_asym_loose.Integral())
                if not h_egamma_noniso_sym_loose.Integral() == 0: h_egamma_noniso_sym_loose.Scale(1.0/h_egamma_noniso_sym_loose.Integral())
                if not h_egamma_noniso_asym_loose.Integral() == 0: h_egamma_noniso_asym_loose.Scale(1.0/h_egamma_noniso_asym_loose.Integral())
                if not h_egamma_loose.Integral() == 0: h_egamma_loose.Scale(1.0/h_egamma_loose.Integral())
                
                h_ratio_iso_sym = h_egamma_tight.Clone()
                h_ratio_iso_sym.Reset()
                h_ratio_iso_sym.SetLineColor(ROOT.kBlack)
                h_ratio_iso_sym.Divide(h_egamma_iso_sym_tight, h_egamma_iso_sym_loose)
                h_ratio_iso_asym = h_egamma_tight.Clone()
                h_ratio_iso_asym.Reset()
                h_ratio_iso_asym.SetLineColor(ROOT.kGreen+1)
                h_ratio_iso_asym.Divide(h_egamma_iso_asym_tight, h_egamma_iso_asym_loose)
                h_ratio_noniso_sym = h_egamma_tight.Clone()
                h_ratio_noniso_sym.Reset()
                h_ratio_noniso_sym.SetLineColor(ROOT.kBlue)
                h_ratio_noniso_sym.Divide(h_egamma_noniso_sym_tight, h_egamma_noniso_sym_loose)
                h_ratio_noniso_asym = h_egamma_tight.Clone()
                h_ratio_noniso_asym.Reset()
                h_ratio_noniso_asym.SetLineColor(ROOT.kRed)
                h_ratio_noniso_asym.Divide(h_egamma_noniso_asym_tight, h_egamma_noniso_asym_loose)
               
                # Create title for plot 
                title = ""
                if eta_reg == "barrel": title += "Barrel"
                elif eta_reg == "endcap": title += "Endcap"
                if i == len(bins) - 1: title += ", pt > " + str(bins[i])
                else: title += ", " + str(bins[i]) + " < pt < " + str(bins[i+1])
               
                # Legend creation
                legend1 = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2)
                legend1.AddEntry(h_egamma_tight, "Tight Photon, " + str(h_egamma_tight.GetEntries()), "l")
                legend1.AddEntry(h_egamma_loose, "Loose Photon, " + str(h_egamma_loose.GetEntries()), "f")
                
                legend2 = ROOT.TLegend(leg_x1, leg_x2, leg_y1, leg_y2)
                legend2.AddEntry(h_ratio_iso_sym, "Iso_Sym TwoProng", "l")
                legend2.AddEntry(h_ratio_iso_asym, "Iso_Asym TwoProng", "l")
                legend2.AddEntry(h_ratio_noniso_sym, "NonIso_Sym TwoProng", "l")
                legend2.AddEntry(h_ratio_noniso_asym, "NonIso_Asym TwoProng", "l")

                h_egamma_tight.SetTitle(title)
                h_ratio_iso_sym.SetTitle("Tight / Loose Photon")  
                
                # Draw plots
                c1.cd(1)
                h_egamma_tight.Draw()
                stack = ROOT.THStack('hs', 'hs')
                stack.Add(h_egamma_loose)
                stack.Draw("hist same")
                h_egamma_tight.Draw("samee")
                ROOT.gPad.SetLogy()
                h_egamma_tight.GetXaxis().SetRangeUser(0, 26)
                legend1.Draw("same")
                c1.cd(2) # draw ratio plots
                h_ratio_iso_sym.Draw("e")
                h_ratio_iso_asym.Draw("samee")
                h_ratio_noniso_sym.Draw("samee")
                h_ratio_noniso_asym.Draw("same")
                h_ratio_iso_sym.GetXaxis().SetRangeUser(0, 26)
                h_ratio_iso_sym.GetYaxis().SetRangeUser(-2, 4)
                legend2.Draw("same")
                ROOT.gPad.SetGridy(1)
                ROOT.gPad.Update()
                c1.Print("plots.pdf")    

c1.Print("plots.pdf]")
infile1.Close()
