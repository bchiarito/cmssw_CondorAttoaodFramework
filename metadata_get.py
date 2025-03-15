#!/usr/bin/env python
from __future__ import print_function
import sys
import os
from functools import reduce
print("checkpoint 1")
import ROOT

# process all attoaod in directory and dump full cutflow

print("checkpoint 2")

path = sys.argv[1]
print("checkpoint 3")
metadata = ROOT.TChain('Metadata')
print("checkpoint 4")


for fi in os.listdir(path):
    if fi.endswith('.root') and fi.startswith('ATTOAOD'): metadata.Add(path+'/'+fi)


#metadata.Scan("*")

cutflow = {}
for col, entry in enumerate(metadata):
    for row, b in enumerate(entry.GetListOfBranches()):
        #print(b.GetName(), entry.__getattr__(b.GetName()))
        
        if not 'zttAna' in b.GetName(): continue
        name = b.GetName()

        if col == 0: cutflow[name] = []
        cutflow[name].append(entry.__getattr__(name))

print(cutflow)

c = {}
for name in cutflow:
    c[name] = reduce(lambda a,b: a+b, cutflow[name])

print()
for name in c:
    if 'AnaTau' in name: print(name, c[name])
print()
for name in c:
    if 'AnaTp' in name and not 'AnaTpm' in name: print(name, c[name])
print()
for name in c:
    if 'AnaTpm' in name: print(name, c[name])

