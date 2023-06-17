import ROOT
import sys
import math

RANGE_LOW = 0 
RANGE_HIGH = 20
BINS = 20

NAME_COUNT = 0
def getname():
  '''
  helper to return unique names for ROOT objects
  '''
  global NAME_COUNT
  NAME_COUNT += 1
  return 'obj'+str(NAME_COUNT)

def TemplateToHistogram(func, bins, low, high, integral=False, debug=False):
  '''
  Takes ROOT TF1 function template, and a binning

  Returns a ROOT TH1D histogram vesion
  '''
  name = getname()  
  hist = ROOT.TH1D(name, name, bins, low, high)
  for i in range(hist.GetNbinsX()):
    if not integral:
      val = func.Eval(hist.GetBinCenter(i+1))
      hist.SetBinContent(i+1, val) if not math.isnan(val) else hist.SetBinContent(i+1, 0)
    else:
      val = (func.Integral(hist.GetBinLowEdge(i+1), hist.GetBinLowEdge(i+1) + hist.GetBinWidth(i+1))) / hist.GetBinWidth(i+1)
      hist.SetBinContent(i+1, val) if not math.isnan(val) else hist.SetBinContent(i+1, 0)
  return hist

def HistogramToFunction(hist):
  '''
  Takes a ROOT TH1 histogram

  Returns a linearized version as a ROOT TF1
  '''
  def histfunc(x):
    return hist.GetBinContent(hist.FindBin(x[0])) 
  return histfunc

def MultiplyWithPolyToTF1(func, degree, range_low=0, range_high=10, cheb=0, parameters=None):
  '''
  Takes a python function

  Returns a TF1 object representing the input function times a polynomial, and the returns resulting function as well

  when cheb=0 (default) use regular polynomials (1, x^2, x^3, etc)
  when cheb=1 use Chebyshev polynomials of the first kind
  when cheb=2 use Chebyshev polynomials of the second kind
  '''
  if degree == 0 and cheb==0:
    def func_after_mult(x, p):
      return func(x) * (p[0])
  if degree == 1 and cheb==0:
    def func_after_mult(x, p):
      return func(x) * (p[0] + p[1]*x[0])
  if degree == 2 and cheb==0:
    def func_after_mult(x, p):
      return func(x) * (p[0] + p[1]*x[0] + p[2]*(x[0]**2))
  if degree == 3 and cheb==0:
    def func_after_mult(x, p):
      return func(x) * (p[0] + p[1]*x[0] + p[2]*(x[0]**2) + p[3]*(x[0]**3))
  if degree == 4 and cheb==0:
    def func_after_mult(x, p):
      return func(x) * (p[0] + p[1]*x[0] + p[2]*(x[0]**2) + p[3]*(x[0]**3) + p[4]*(x[0]**4))

  if degree == 0 and cheb == 1:
    def func_after_mult(x, p):
      return func(x) * (p[0])
  if degree == 1 and cheb == 1:
    def func_after_mult(x, p):
      return func(x) * (p[0] + p[1]*(x[0]))
  if degree == 2 and cheb == 1:
    def func_after_mult(x, p):
      X = x[0]
      return func(x) * (p[0] + p[1]*(X) + p[2]*(2*X**2 - 1))
  if degree == 3 and cheb == 1:
    def func_after_mult(x, p):
      X = x[0]
      return func(x) * (p[0] + p[1]*(X) + p[2]*(2*X**2 - 1) + p[3]*(4*X**3 - 3*X))
  if degree == 4 and cheb == 1:
    def func_after_mult(x, p):
      X = x[0]
      return func(x) * (p[0] + p[1]*(X) + p[2]*(2*X**2 - 1) + p[3]*(4*X**3 - 3*X) + p[4]*(8*X**4 - 8*X**2 + 1))

  if degree == 0 and cheb == 2:
    def func_after_mult(x, p):
      return func(x) * (p[0])
  if degree == 1 and cheb == 2:
    def func_after_mult(x, p):
      return func(x) * (p[0] + p[1]*(2*x[0]))
  if degree == 2 and cheb == 2:
    def func_after_mult(x, p):
      X = x[0]
      return func(x) * (p[0] + p[1]*(2*X) + p[2]*(4*X**2 - 1))
  if degree == 3 and cheb == 2:
    def func_after_mult(x, p):
      X = x[0]
      return func(x) * (p[0] + p[1]*(2*X) + p[2]*(4*X**2 - 1) + p[3]*(8*X**3 - 4*X))
  if degree == 4 and cheb == 3:
    def func_after_mult(x, p):
      X = x[0]
      return func(x) * (p[0] + p[1]*(2*X) + p[2]*(4*X**2 - 1) + p[3]*(8*X**3 - 4*X) + p[4]*(16*X**4 - 12*X**2 + 1))

  tf1 = ROOT.TF1(getname(), func_after_mult, range_low, range_high, degree+1)
  if degree>=0: tf1.SetParNames('Constant') if cheb==0 else tf1.SetParNames('Zero')
  if degree>=1: tf1.SetParNames('Linear') if cheb==0 else tf1.SetParNames('One')
  if degree>=2: tf1.SetParNames('Quadratic') if cheb==0 else tf1.SetParNames('Two')
  if degree>=3: tf1.SetParNames('Cubic') if cheb==0 else tf1.SetParNames('Three')
  if degree>=4: tf1.SetParNames('Quartic') if cheb==0 else tf1.SetParNames('Four')
  if not parameters:
    for i in range(degree+1): tf1.SetParameter(i, 1.0)
  else:
    tf1.SetParameters(*parameters)
  return tf1, func_after_mult


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
