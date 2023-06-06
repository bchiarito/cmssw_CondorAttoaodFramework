import ROOT
import sys

RANGE_LOW = 0 
RANGE_HIGH = 10
BINS = 20

NAME_COUNT = 0
def getname():
  '''
  helper to return unique names for ROOT objects
  '''
  global NAME_COUNT
  NAME_COUNT += 1
  return 'obj'+str(NAME_COUNT)

def TemplateToHistogram(func, bins, low, high, integral=False):
  '''
  Takes ROOT TF1 function template, and a binning

  Returns a ROOT TH1D histogram vesion, by using the function midpoint in each bin
  '''
  name = getname()  
  hist = ROOT.TH1D(name, name, bins, low, high)
  for i in range(hist.GetNbinsX()):
    if not integral: hist.SetBinContent(i+1, func.Eval(hist.GetBinCenter(i+1)))
    else: hist.SetBinContent(i+1, func.Integral(hist.GetBinLowEdge(i+1), hist.GetBinLowEdge(i+1) + hist.GetBinWidth(i+1) ) )
  return hist

def HistogramToFunction(hist):
  '''
  Takes a ROOT TH1 histogram

  Returns a linearized version as a ROOT TF1
  '''
  def histfunc(x):
    return hist.GetBinContent(hist.FindBin(x[0])) 
  return histfunc

def MultiplyWithPolyToTF1(func, degree):
  '''
  Takes a python function

  Returns a TF1 object representing the input function times a polynomial
  '''
  if degree == 0:
    def multPol1(x, p):
      return func(x) * (p[0])
    f = ROOT.TF1(getname(), multPol1, RANGE_LOW, RANGE_HIGH, 1)
    f.SetParNames('Constant')
    f.SetParameter(0, 1.0)
  if degree == 1:
    def multPol1(x, p):
      return func(x) * (p[0] + p[1]*x[0])
    f = ROOT.TF1(getname(), multPol1, RANGE_LOW, RANGE_HIGH, 2)
    f.SetParNames('Constant', 'Linear')
    f.SetParameters(1.0, 1.0)
  if degree == 2:
    def multPol2(x, p):
      return func(x) * (p[0] + p[1]*x[0] + p[2]*x[0])
    f = ROOT.TF1(getname(), multPol2, RANGE_LOW, RANGE_HIGH, 3)
    f.SetParNames('Constant', 'Linear', 'Quadratic')
    f.SetParameters(1.0, 1.0, 1.0)
  if degree == 3:
    def multPol3(x, p):
      return func(x) * (p[0] + p[1]*x[0] + p[2]*x[0] + p[3]*x[0])
    f = ROOT.TF1(getname(), multPol2, RANGE_LOW, RANGE_HIGH, 4)
    f.SetParNames('Constant', 'Linear', 'Quadratic', 'Cubic')
    f.SetParameters(1.0, 1.0, 1.0, 1.0)
  
  return f

if __name__ == '__main__':
  print('define a function')
  f1 = ROOT.TF1('f1', 'gaus(0)', RANGE_LOW, RANGE_HIGH)
  f1.SetParNames('first', 'second', 'third')
  f1.SetParameters(1.0, 1.0, 1.0)

  print('turn into histogram')
  bins, low, high = BINS, RANGE_LOW, RANGE_HIGH
  hist = TemplateToHistogram(f1, bins, low, high, integral=True)
  hist.Draw()
  raw_input()

  print('turn histo into python function')
  func = HistogramToFunction(hist)

  print('multiply with polynomial')
  func_with_poly = MultiplyWithPolyToTF1(func, 2)
  func_with_poly.Draw()
  raw_input()

  print('make second histogram')
  hist_target = ROOT.TH1D(getname(), 'target', bins, low, high)
  hist_target.FillRandom('f1', 100000)
  hist_target.Draw()
  raw_input() 

  print('fit second histogram with function')
  hist_target.Fit(func_with_poly, "L")
  hist_target.Draw()
  raw_input() 

  print('extract parameters of poly from fit')
  f = func_with_poly
  n = f.GetNpar()
  for i in range(n):
    print(f.GetParName(i), f.GetParameter(i))
