import ROOT
import sys
import argparse
import array


def computeBinErrors(lowErr, upErr):
    return (lowErr + upErr) / 2 

def compute_mc_bin(bin_vals):
    bin_sum = 0
    for i in range(len(bin_vals)):
        bin_sum += bin_vals[i]
    return bin_sum

def compute_mc_errors(bin_vals, weights):
    bin_err = 0
    for i in range(len(weights)):
        bin_err += bin_vals[i]*weights[i]**2  # each bin weight is sqrt(bin_content) * mc_weight
    return bin_err**0.5


infiles = 0
for i in range(len(sys.argv)):
    if ".root" in sys.argv[i]: infiles += 1

parser = argparse.ArgumentParser(description="")

# args
parser.add_argument("input", metavar="INPUT", help="input root file (data)")
if infiles >= 2: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 3: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 4: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 5: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 6: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 7: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 8: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 9: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 10: parser.add_argument("input", metavar="INPUT", help="input root file")
if infiles >= 11: parser.add_argument("input", metavar="INPUT", help="input root file")

parser.add_argument("--name", default="plots", help="specify pdf name")
parser.add_argument("--gjets", default=False, action="store_true", help="compute gjets error bars")
parser.add_argument("--scalefactor", "--sf", default="", choices=["1D","2D"], help="compute 1D scalefactor hists")
parser.add_argument("--visualize", "-v", default=False, action="store_true", help="display histogram after its made")
parser.add_argument("--dataset", "-d", default="muon", choices=["muon","met"], help="specify dataset used")
args = parser.parse_args()

c1 = ROOT.TCanvas("c1", "c1", 800, 600)
c1.Print(args.name + ".pdf[")
c1.cd()

effs = ["pt", "eta", "phi"]

if args.scalefactor == "":  # display photon pt, eta, phi efficiencies for data or mc 
    if args.gjets:
        weights = [36.5075189661, 16.2932699488, 2.07826966876, 0.924808517231, 0.311118100188] #0: 40-100, 1:100-200, etc

        infile0 = ROOT.TFile(sys.argv[1], 'UPDATE')
        infile1 = ROOT.TFile(sys.argv[2], 'UPDATE')
        infile2 = ROOT.TFile(sys.argv[3], 'UPDATE')
        infile3 = ROOT.TFile(sys.argv[4], 'UPDATE')
        infile4 = ROOT.TFile(sys.argv[5], 'UPDATE')

        for j in range(len(effs)):
            if effs[j] == "pt":
                h_num = ROOT.TH1F('photon_pt_num', '; Photon p_{T}', 160, 0, 1600)
                h_denom = ROOT.TH1F('photon_pt_num', '; Photon p_{T}', 160, 0, 1600)
            elif effs[j] == "eta":
                h_num = ROOT.TH1F('photon_eta_num', '; Photon_Eta', 35, -1.5, 1.5)
                h_denom = ROOT.TH1F('photon_eta_num', '; Photon_Eta', 35, -1.5, 1.5)
            else:
                h_num = ROOT.TH1F('photon_phi_num', '; Photon_phi', 35, -3.5, 3.5)
                h_denom = ROOT.TH1F('photon_phi_num', '; Photon_phi', 35, -3.5, 3.5)
            
            h_num0 = infile0.Get("plots/" + "photon_" + effs[j] + "_num")
            h_denom0 = infile0.Get("plots/" + "photon_" + effs[j] + "_denom")
            h_num1 = infile1.Get("plots/" + "photon_" + effs[j] + "_num")
            h_denom1 = infile1.Get("plots/" + "photon_" + effs[j] + "_denom")
            h_num2 = infile2.Get("plots/" + "photon_" + effs[j] + "_num")
            h_denom2 = infile2.Get("plots/" + "photon_" + effs[j] + "_denom")
            h_num3 = infile3.Get("plots/" + "photon_" + effs[j] + "_num")
            h_denom3 = infile3.Get("plots/" + "photon_" + effs[j] + "_denom")
            h_num4 = infile4.Get("plots/" + "photon_" + effs[j] + "_num")
            h_denom4 = infile4.Get("plots/" + "photon_" + effs[j] + "_denom")

            for k in range(h_num0.GetNbinsX()):
                num_bin_vals = [h_num0.GetBinContent(k), h_num1.GetBinContent(k), h_num2.GetBinContent(k), h_num3.GetBinContent(k), h_num4.GetBinContent(k)]
                denom_bin_vals = [h_denom0.GetBinContent(k), h_denom1.GetBinContent(k), h_denom2.GetBinContent(k), h_denom3.GetBinContent(k), h_denom4.GetBinContent(k)]

                h_num.SetBinContent(k, h_num0.GetBinContent(k) + h_num1.GetBinContent(k) + h_num2.GetBinContent(k) + h_num3.GetBinContent(k) + h_num4.GetBinContent(k))
                h_num.SetBinError(k, compute_mc_errors(num_bin_vals, weights))
                h_denom.SetBinContent(k, h_denom0.GetBinContent(k) + h_denom1.GetBinContent(k) + h_denom2.GetBinContent(k) + h_denom3.GetBinContent(k) + h_denom4.GetBinContent(k))
                h_denom.SetBinError(k, compute_mc_errors(denom_bin_vals, weights))

            h_teff = ROOT.TEfficiency(h_num, h_denom)
            h_teff.SetTitle("GJets 2018, HLT_Photon200, Barrel")
            h_teff.Draw("")

            #l = ROOT.TLegend(0.35, 0.78, 0.65, 0.9)
            #l.AddEntry(h_teff, "HLT_Photon200, Barrel + Endcap", "l")
            #l.Draw("same")

            ROOT.gPad.SetGridx()
            if effs[j] == "pt": 
                line = ROOT.TLine(0, 1, 1740, 1)
                line.Draw("same")
            c1.Print(args.name + ".pdf")
    else:
        for i in range(infiles):
            for j in range(len(effs)):
                infile = ROOT.TFile(sys.argv[i+1], 'UPDATE')
                h_num = infile.Get("plots/" + "photon_" + effs[j] + "_num")
                h_denom = infile.Get("plots/" + "photon_" + effs[j] + "_denom")
                h_teff = ROOT.TEfficiency(h_num, h_denom)

                h_teff.SetTitle("GJets 2018, HLT_Photon200, Barrel")
                h_teff.Draw("")

                #l = ROOT.TLegend(0.35, 0.78, 0.65, 0.9)
                #l.AddEntry(h_teff, "HLT_Photon200, Barrel + Endcap", "l")
                #l.Draw("same")

                ROOT.gPad.SetGridx()
                if effs[j] == "pt": 
                    line = ROOT.TLine(0, 1, 1740, 1)
                    line.Draw("same")
                c1.Print(args.name + ".pdf")

elif args.scalefactor.lower() == "1d":  # create the 1D scalefactor plots for data/mc in photon pt, eta, phi
    for j in range(len(effs)): 
        infile0 = ROOT.TFile(sys.argv[1], 'UPDATE')  # data first
        infile1 = ROOT.TFile(sys.argv[2], 'UPDATE')  # rest is for gjets ht bins
        infile2 = ROOT.TFile(sys.argv[3], 'UPDATE')
        infile3 = ROOT.TFile(sys.argv[4], 'UPDATE')
        infile4 = ROOT.TFile(sys.argv[5], 'UPDATE')
        infile5 = ROOT.TFile(sys.argv[6], 'UPDATE')

        h_num_dat = infile0.Get("plots/" + "photon_" + effs[j] + "_num")
        h_denom_dat = infile0.Get("plots/" + "photon_" + effs[j] + "_denom")
        h_teff_dat = ROOT.TEfficiency(h_num_dat, h_denom_dat)  # numerator for scalefactor

        if effs[j] == "pt":
            h_num_mc = ROOT.TH1F('photon_pt_num', '; Photon p_{T}', 160, 0, 1600)
            h_denom_mc = ROOT.TH1F('photon_pt_denom', '; Photon p_{T}', 160, 0, 1600)
            h_scale_dat = ROOT.TH1F('photon_pt_scale_dat', '; Photon p_{T}', 160, 0, 1600)
            h_scale_mc = ROOT.TH1F('photon_pt_scale_mc', '; Photon p_{T}', 160, 0, 1600)
            h_Eff_data_to_mc = ROOT.TH1F('photon_pt_scalefactor', '; Photon p_{T}', 160, 0, 1600)
        elif effs[j] == "eta":
            h_num_mc = ROOT.TH1F('photon_eta_num', '; Photon_Eta', 35, -1.5, 1.5)
            h_denom_mc = ROOT.TH1F('photon_eta_denom', '; Photon_Eta', 35, -1.5, 1.5)
            h_scale_dat = ROOT.TH1F('photon_eta_scale_dat', '; Photon_Eta', 35, -1.5, 1.5)
            h_scale_mc = ROOT.TH1F('photon_eta_scale_mc', '; Photon_Eta', 35, -1.5, 1.5)
            h_Eff_data_to_mc = ROOT.TH1F('photon_eta_scalefactor', '; Photon_Eta', 35, -1.5, 1.5)
        else:
            h_num_mc = ROOT.TH1F('photon_phi_num', '; Photon_phi', 35, -3.5, 3.5)
            h_denom_mc = ROOT.TH1F('photon_phi_denom', '; Photon_phi', 35, -3.5, 3.5)
            h_scale_dat = ROOT.TH1F('photon_phi_scale_dat', '; Photon_phi', 35, -3.5, 3.5)
            h_scale_mc = ROOT.TH1F('photon_phi_scale_mc', '; Photon_phi', 35, -3.5, 3.5)
            h_Eff_data_to_mc = ROOT.TH1F('photon_phi_scalefactor', '; Photon_phi', 35, -3.5, 3.5)
        
        h_num1 = infile1.Get("plots/" + "photon_" + effs[j] + "_num")
        h_denom1 = infile1.Get("plots/" + "photon_" + effs[j] + "_denom")
        h_num2 = infile2.Get("plots/" + "photon_" + effs[j] + "_num")
        h_denom2 = infile2.Get("plots/" + "photon_" + effs[j] + "_denom")
        h_num3 = infile3.Get("plots/" + "photon_" + effs[j] + "_num")
        h_denom3 = infile3.Get("plots/" + "photon_" + effs[j] + "_denom")
        h_num4 = infile4.Get("plots/" + "photon_" + effs[j] + "_num")
        h_denom4 = infile4.Get("plots/" + "photon_" + effs[j] + "_denom")
        h_num5 = infile5.Get("plots/" + "photon_" + effs[j] + "_num")
        h_denom5 = infile5.Get("plots/" + "photon_" + effs[j] + "_denom")
        weights = [36.5075189661, 16.2932699488, 2.07826966876, 0.924808517231, 0.311118100188] #0: 40-100, 1:100-200, etc

        for k in range(h_num1.GetNbinsX()):
            num_bin_vals = [h_num1.GetBinContent(k), h_num2.GetBinContent(k), h_num3.GetBinContent(k), h_num4.GetBinContent(k), h_num5.GetBinContent(k)]
            denom_bin_vals = [h_denom1.GetBinContent(k), h_denom2.GetBinContent(k), h_denom3.GetBinContent(k), h_denom4.GetBinContent(k), h_denom5.GetBinContent(k)]

            h_num_mc.SetBinContent(k, h_num1.GetBinContent(k) + h_num2.GetBinContent(k) + h_num3.GetBinContent(k) + h_num4.GetBinContent(k) + h_num5.GetBinContent(k))
            h_num_mc.SetBinError(k, compute_mc_errors(num_bin_vals, weights))
            h_denom_mc.SetBinContent(k, h_denom1.GetBinContent(k) + h_denom2.GetBinContent(k) + h_denom3.GetBinContent(k) + h_denom4.GetBinContent(k) + h_denom5.GetBinContent(k))
            h_denom_mc.SetBinError(k, compute_mc_errors(denom_bin_vals, weights))

        h_teff_mc = ROOT.TEfficiency(h_num_mc, h_denom_mc)

        # create scalefactor hist
        for i in range(h_num_mc.GetNbinsX()):
            tBin = h_teff_dat.GetGlobalBin(i+1)
            h_scale_dat.SetBinContent(i+1,h_teff_dat.GetEfficiency(tBin))
            h_scale_mc.SetBinContent(i+1,h_teff_mc.GetEfficiency(tBin))
            binErr_dat = computeBinErrors(h_teff_dat.GetEfficiencyErrorUp(tBin), h_teff_dat.GetEfficiencyErrorLow(tBin))
            h_scale_dat.SetBinError(i+1,binErr_dat)
            binErr_mc = computeBinErrors(h_teff_mc.GetEfficiencyErrorUp(tBin), h_teff_mc.GetEfficiencyErrorLow(tBin))
            h_scale_mc.SetBinError(i+1,binErr_mc)
            
            # Uncorrelated num/denom, so add the RELATIVE errors in quadrature
            if h_scale_dat.GetBinContent(i+1) == 0 and h_scale_mc.GetBinContent(i+1) != 0:
                totErr = binErr_mc / h_scale_mc.GetBinContent(i+1)
            elif h_scale_mc.GetBinContent(i+1) == 0 and h_scale_dat.GetBinContent(i+1) != 0:
                totErr = binErr_dat / h_scale_dat.GetBinContent(i+1)
            elif h_scale_dat.GetBinContent(i+1) == 0 and h_scale_mc.GetBinContent(i+1) == 0:
                totErr = 0
            else:
                relErr_dat = h_scale_dat.GetBinError(i+1) / h_scale_dat.GetBinContent(i+1)
                relErr_mc = binErr_mc / h_scale_mc.GetBinContent(i+1)
                totErr = (relErr_dat**2 + relErr_mc**2) ** 0.5 
            
            # Fill histograms
            if h_scale_mc.GetBinContent(i+1) == 0:
                h_Eff_data_to_mc.SetBinContent(i+1,0)
            else:
                h_Eff_data_to_mc.SetBinContent(i+1, h_scale_dat.GetBinContent(i+1) / h_scale_mc.GetBinContent(i+1))
                h_Eff_data_to_mc.SetBinError(i+1,totErr)

        h_Eff_data_to_mc.SetTitle("SingleMuon / Gjets, 2018, Barrel")
        h_Eff_data_to_mc.Draw("")
        
        if effs[j] == "pt":
            h_Eff_data_to_mc.GetXaxis().SetRangeUser(200, 1600)
            h_Eff_data_to_mc.GetYaxis().SetRangeUser(0.5, 1.5)
            line = ROOT.TLine(200, 1, 1600, 1)
            line.Draw("same")
        elif effs[j] == "eta":
            h_Eff_data_to_mc.GetYaxis().SetRangeUser(0.8, 1.2)
            line = ROOT.TLine(-1.5, 1, 1.5, 1)
            line.Draw("same")
        elif effs[j] == "phi":
            h_Eff_data_to_mc.GetXaxis().SetRangeUser(-3, 3)
            h_Eff_data_to_mc.GetYaxis().SetRangeUser(0.9, 1.1)
            line = ROOT.TLine(-3, 1, 3, 1)
            line.Draw("same")

        if args.visualize: raw_input()
        c1.Print(args.name + ".pdf")

else:  # 2D scalefactor
    for j in range(len(effs)): 
        infile0 = ROOT.TFile(sys.argv[1], 'UPDATE')  # data first
        infile1 = ROOT.TFile(sys.argv[2], 'UPDATE')  # rest is for gjets ht bins
        infile2 = ROOT.TFile(sys.argv[3], 'UPDATE')
        infile3 = ROOT.TFile(sys.argv[4], 'UPDATE')
        infile4 = ROOT.TFile(sys.argv[5], 'UPDATE')
        infile5 = ROOT.TFile(sys.argv[6], 'UPDATE')

        h_num_dat = infile0.Get("plots/" + "photon_pt_eta_2d_num")
        h_denom_dat = infile0.Get("plots/" + "photon_pt_eta_2d_denom")
        h_teff_dat = ROOT.TEfficiency(h_num_dat, h_denom_dat)  # numerator for scalefactor
        
        # Scalefactor hists
        pt_bin = array.array('f', [220, 260, 300, 350, 400, 450, 500, 600, 800, 2000])
        eta_bin = array.array('f', [0, 0.8, 1.44442])
        h_num_mc = ROOT.TH2F('photon_pt_eta_2d_num', '; Photon p_{T}; Photon Eta', len(pt_bin)-1, pt_bin, len(eta_bin)-1, eta_bin)
        h_denom_mc = ROOT.TH2F('photon_pt_eta_2d_denom', '; Photon p_{T}; Photon Eta', len(pt_bin)-1, pt_bin, len(eta_bin)-1, eta_bin)
        h_scale_dat = ROOT.TH2F('photon_pt_eta_2d_scale_dat', '; Photon p_{T}; Photon Eta', len(pt_bin)-1, pt_bin, len(eta_bin)-1, eta_bin)
        h_scale_mc = ROOT.TH2F('photon_pt_eta_2d_scale_mc', '; Photon p_{T}; Photon Eta', len(pt_bin)-1, pt_bin, len(eta_bin)-1, eta_bin)
        h_Eff_data_to_mc = ROOT.TH2F('photon_pt_eta_scalefactor', '; Photon p_{T}; Photon Eta', len(pt_bin)-1, pt_bin, len(eta_bin)-1, eta_bin)
        
        h_num1 = infile1.Get("plots/" + "photon_pt_eta_2d_num")
        h_denom1 = infile1.Get("plots/" + "photon_pt_eta_2d_denom")
        h_num2 = infile2.Get("plots/" + "photon_pt_eta_2d_num")
        h_denom2 = infile2.Get("plots/" + "photon_pt_eta_2d_denom")
        h_num3 = infile3.Get("plots/" + "photon_pt_eta_2d_num")
        h_denom3 = infile3.Get("plots/" + "photon_pt_eta_2d_denom")
        h_num4 = infile4.Get("plots/" + "photon_pt_eta_2d_num")
        h_denom4 = infile4.Get("plots/" + "photon_pt_eta_2d_denom")
        h_num5 = infile5.Get("plots/" + "photon_pt_eta_2d_num")
        h_denom5 = infile5.Get("plots/" + "photon_pt_eta_2d_denom")
        weights = [36.5075189661, 16.2932699488, 2.07826966876, 0.924808517231, 0.311118100188] #0: 40-100, 1:100-200, etc
        
        # properly combine mc ht bins
        for k in range(len(pt_bin)-1):
            for l in range(len(eta_bin)-1):
                num_bin_vals = [h_num1.GetBinContent(k+1,l+1), h_num2.GetBinContent(k+1,l+1), h_num3.GetBinContent(k+1,l+1), h_num4.GetBinContent(k+1,l+1), h_num5.GetBinContent(k+1,l+1)]
                denom_bin_vals = [h_denom1.GetBinContent(k+1,l+1), h_denom2.GetBinContent(k+1,l+1), h_denom3.GetBinContent(k+1,l+1), h_denom4.GetBinContent(k+1,l+1), h_denom5.GetBinContent(k+1,l+1)]

                h_num_mc.SetBinContent(k+1,l+1, compute_mc_bin(num_bin_vals)) 
                h_num_mc.SetBinError(k+1,l+1, compute_mc_errors(num_bin_vals, weights))
                h_denom_mc.SetBinContent(k+1,l+1, compute_mc_bin(denom_bin_vals)) 
                h_denom_mc.SetBinError(k+1,l+1, compute_mc_errors(denom_bin_vals, weights))

        h_teff_mc = ROOT.TEfficiency(h_num_mc, h_denom_mc)

        # create scalefactor hist
        for i in range(len(pt_bin)-1):
            for k in range(len(eta_bins)-1):
                tBin = h_teff_dat.GetGlobalBin(i+1,k+1)
                h_scale_dat.SetBinContent(i+1,k+1,h_teff_dat.GetEfficiency(tBin))
                h_scale_mc.SetBinContent(i+1,k+1,h_teff_mc.GetEfficiency(tBin))
                binErr_dat = computeBinErrors(h_teff_dat.GetEfficiencyErrorUp(tBin), h_teff_dat.GetEfficiencyErrorLow(tBin))
                h_scale_dat.SetBinError(i+1,k+1,binErr_dat)
                binErr_mc = computeBinErrors(h_teff_mc.GetEfficiencyErrorUp(tBin), h_teff_mc.GetEfficiencyErrorLow(tBin))
                h_scale_mc.SetBinError(i+1,k+1,binErr_mc)
                
                # Uncorrelated num/denom, so add the RELATIVE errors in quadrature
                if h_scale_dat.GetBinContent(i+1,k+1) == 0 and h_scale_mc.GetBinContent(i+1,k+1) != 0:
                    totErr = binErr_mc / h_scale_mc.GetBinContent(i+1,k+1,k+1)
                elif h_scale_mc.GetBinContent(i+1,k+1) == 0 and h_scale_dat.GetBinContent(i+1,k+1) != 0:
                    totErr = binErr_dat / h_scale_dat.GetBinContent(i+1,k+1)
                elif h_scale_dat.GetBinContent(i+1,k+1) == 0 and h_scale_mc.GetBinContent(i+1,k+1) == 0:
                    totErr = 0
                else:
                    relErr_dat = h_scale_dat.GetBinError(i+1,k+1) / h_scale_dat.GetBinContent(i+1,k+1)
                    relErr_mc = binErr_mc / h_scale_mc.GetBinContent(i+1,k+1)
                    totErr = (relErr_dat**2 + relErr_mc**2) ** 0.5 
                
                # Fill histograms
                if h_scale_mc.GetBinContent(i+1,k+1) == 0:
                    h_Eff_data_to_mc.SetBinContent(i+1,k+1,0)
                else:
                    h_Eff_data_to_mc.SetBinContent(i+1,k+1, h_scale_dat.GetBinContent(i+1,k+1) / h_scale_mc.GetBinContent(i+1,k+1))
                    h_Eff_data_to_mc.SetBinError(i+1,k+1,totErr)
        
        if args.dataset == "muon": h_Eff_data_to_mc.SetTitle("SingleMuon / Gjets, 2018, Barrel")
        elif args.dataset == "met": h_Eff_data_to_mc.SetTitle("MET / Gjets, 2018, Barrel")
        h_Eff_data_to_mc.Draw("")

        if args.visualize: raw_input()
        c1.Print(args.name + ".pdf")


c1.Print(args.name + ".pdf]")





