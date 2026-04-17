from collections import OrderedDict
# all pb

GJETS = OrderedDict([
('40to100',  18650,),
('100to200', 8639,),
('200to400', 2173,),
('400to600', 260.7,),
('600toInf', 86.55)
])

LUMI_UL18 = 59830
LUMI_UL17 = 41480
LUMI_UL16 = 36310
# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2

'''
options:
  - [--datasetname=gjets40to100, --xs=18650]
  - [--datasetname=gjets100to200, --xs=8639]
  - [--datasetname=gjets200to400, --xs=2173]
  - [--datasetname=gjets400to600, --xs=260.7]
  - [--datasetname=gjets600toInf, --xs=86.55]


options:
  - [--datasetname=qcd50to100, --xs=187700000]
  - [--datasetname=qcd100to200, --xs=23500000]
  - [--datasetname=qcd200to300, --xs=1552000]
  - [--datasetname=qcd300to500, --xs=321100]
  - [--datasetname=qcd500to700, --xs=30250]
  - [--datasetname=qcd700to1000, --xs=6398]
  - [--datasetname=qcd1000to1500, --xs=1122]
  - [--datasetname=qcd1500to2000, --xs=109.4]
  - [--datasetname=qcd2000toInf, --xs=21.74]

options:
  - [--datasetname=dy50, --xs=6077]
  - [--datasetname=wjets, --xs=61526.7]
  - [--datasetname=ttbar_semilep, --xs=888]

options:
  - [--datasetname=signalM125m0p55, --xs=202.315]
  - [--datasetname=signalM690m1p225, --xs=80.292484]
  - [--datasetname=signalM1280m2p2, --xs=2.3405524]


options:
  - [--datasetname=gjets40to100, --xs=18650]
  - [--datasetname=gjets100to200, --xs=8639]
  - [--datasetname=gjets200to400, --xs=2173]
  - [--datasetname=gjets400to600, --xs=260.7]
  - [--datasetname=gjets600toInf, --xs=86.55]

options:
  - [--datasetname=gjets40to100, --xs=18650]
  - [--datasetname=gjets100to200, --xs=8639]
  - [--datasetname=gjets200to400, --xs=2173]
  - [--datasetname=gjets400to600, --xs=260.7]
  - [--datasetname=gjets600toInf, --xs=86.55]
'''
