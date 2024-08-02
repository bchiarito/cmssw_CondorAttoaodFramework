runs in a conda environment created to these specs:
$ conda create -n pyroot -c conda-forge root "python<3"
which will provide python3 at <3.11 and python at 2.7

Region 1: tight
Region 2: loose
Region 0: neither

### running
use condor_submit.py

### to work on backend
1. get a copy
```
backend_plotting_get.sh
```
2. change code and run interactively, under CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_plotting directory
```
```
3. git push
4. copy tarball to cmslpc for use with next job
```
backend_plotting_xrdcp.sh 
```
