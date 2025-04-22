# 
import sys
import os

prefix = sys.argv[1]

for multijobdir in os.listdir("."):
    if not multijobdir.startswith("MultiJob_{}").format(tag): continue
    if not multijobdir.endswith("_HistoMode"): continue
    print(multijobdir)
