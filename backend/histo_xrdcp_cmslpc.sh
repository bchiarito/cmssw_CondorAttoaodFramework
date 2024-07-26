#! /bin/sh
if [[ -z "$1" ]] ; then
  echo "Please supply grid id as argument."
  exit 1
fi
rm backend_histo_cmssw/CMSSW_10_6_20.tgz
tar -C backend_histo_cmssw --exclude="*.root" -zcf CMSSW_10_6_20.tgz CMSSW_10_6_20
xrdfs root://cmseos.fnal.gov/ rm /store/user/$1/tarballs/histo/CMSSW_10_6_20.tgz
xrdcp CMSSW_10_6_20.tgz root://cmseos.fnal.gov//store/user/$1/tarballs/histo/CMSSW_10_6_20.tgz
mv CMSSW_10_6_20.tgz backend_histo_cmssw
