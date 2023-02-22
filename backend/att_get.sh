#! /bin/sh
rm -rf backend_atto_cmssw
mkdir backend_atto_cmssw
cd backend_atto_cmssw
cmsrel CMSSW_10_6_20
cd CMSSW_10_6_20/src
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools/python
if [[ -z "$1" ]] ; then
  echo ""
  echo "Got no argument, using default (https://github.com/bchiarito/cmssw_CondorAttoaodBackend.git) github repo for backend"
  echo ""
  git clone https://github.com/bchiarito/cmssw_CondorAttoaodBackend.git fmk_atto
else
  echo ""
  echo "Using argument as github repo"
  echo "git clone" $1 "test"
  echo ""
  git clone $1 fmk_atto
  exitcode=$?
  if [[ exitcode -eq 0 ]] ; then
      :
  else
      echo 'ERROR: git clone exited with non-zero exit code!'
      exit 1
  fi
fi
cd ../../..
scram b
