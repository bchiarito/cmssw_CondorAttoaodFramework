import ROOT
import sys

def fitfunc(x, p):
  norm = p[0]
  mpv = p[1]
  sigma = p[2]
  C1 = p[3]
  C2 = p[4]
  bound1 = p[5]
  bound2 = p[6]

  land = norm*ROOT.TMath.Landau(x[0], mpv, sigma)

  y11=norm*ROOT.TMath.Landau(bound1, mpv, sigma);
  y12=ROOT.TMath.Exp(C1*bound1);
  exp1 = ROOT.TMath.Exp(C1*x[0])*y11/y12

  y21=ROOT.TMath.Exp(C1*bound2)*y11/y12
  y22=ROOT.TMath.Exp(C2*bound2)
  exp2=ROOT.TMath.Exp(C2*x[0])*y21/y22

  if x[0] < bound1: return land
  elif x[0] < bound2: return exp1
  else: return exp2

fi = ROOT.TFile(sys.argv[1])

for i in range(10):
  h = fi.Get('plots/twoprong_masspi0_noniso_sym_barrel_140_160_tight')

  f2 = ROOT.TF1('f2', fitfunc, 0, 50, 7)
  f2.SetParameters(h.GetEntries(), h.GetMean(), 0.5, -3, -1, h.GetMean()+0.5, h.GetMean()*3)
  f2.SetParNames("Constant","MPV","Sigma","C1","C2","Boundary1","Boundary2")

  h.Fit(f2, 'L', "", 0, 15)
  h.Draw()
