#!/usr/bin/env python3
from __future__ import print_function
import sys
import os
import subprocess

in_key =  "===#===#==="
out_key = "---#---#---"

def parse(filename):
  fi = open(filename)
  collection = []
  i = False
  for line in fi:
    line = line.strip()
    #print(line)
    if line == in_key:
      d = {}
      i = True
    if line == out_key:
      collection.append(d)
      i = False
    if i:
      line = line.split()
      #print(line)
      if len(line) == 1: d['name'] = line[0]
      if len(line) == 2:
        num = line[1]
        try: num = int(num)
        except ValueError:
          num = 0
          print("got a ValueError! on line", line)
        d[line[0]] = num
  return collection

loc = sys.argv[1]
files = []
all_colls = []
if loc.startswith('/store/'):
  list_of_files = (subprocess.getoutput("xrdfs root://cmseos.fnal.gov ls "+loc)).split('\n')
  #print(list_of_files, '\n')
  for fi in list_of_files:
    if not fi.endswith(".txt"): continue
    print(fi)
    os.system('xrdcp --nopbar root://cmseos.fnal.gov/'+fi+' .')
    temp = os.path.basename(fi)
    #print(temp)
    collection = parse(temp)
    all_colls.append(collection)
    os.system('rm '+temp)
else:
  for fi in os.listdir(loc):
    if fi.endswith(".txt"):
      print("on", fi)
      collection = parse(os.path.join(sys.argv[1], fi))
      #for d in collection:
      #  for key in d:
      #    print(key, d[key])
      all_colls.append(collection)

summed_coll = []
for i in range(len(all_colls[0])):
  d = {}
  summed_coll.append(d)
for coll in all_colls:
  for i, d in enumerate(coll):
    summed_dir = summed_coll[i]
    for key in d:
      if key in summed_dir:
        if key == 'name': continue
        summed_dir[key] += d[key]
      else:
        summed_dir[key] = d[key]

print("this many reports:", len(summed_coll))
for i, d in enumerate(summed_coll):
  print("  report", i+1)
  for key in d:
    print(key, d[key])
