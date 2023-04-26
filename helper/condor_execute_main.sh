#! /bin/bash
echo ">>> Starting job on" `date`
echo ">>> Running on: `uname -a`"
echo ">>> System software: `cat /etc/redhat-release`"
echo ""
echo "&&& Here there are all the input arguments &&&"
echo $@
export INITIAL_DIR=$(pwd)
echo ''
echo '&&& Current directiory and Contents: &&&'
pwd
ls -ldh *
echo ''

if [ -f /osg/current/setup.sh ]; then
  echo "&&& Sourcing grid environment for hexcms &&&"
  source /osg/current/setup.sh
  echo ''
fi

echo '&&& Running input unpacker script with command: &&&'
python unpacker.py $3
echo ''
echo '&&& New contents: &&&'
ls -ldh *
echo ''

echo '&&& Setup CMSSW area &&&'
export HOME=$INITIAL_DIR
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
export SCRAM_ARCH=slc7_amd64_gcc820
echo '&&& About to copying over tarball &&&'
if [ ${15} == "hexcms" ]; then
  cp /cms/$4/tarballs/$1/CMSSW_10_6_20.tgz .
elif [ ${15} == "cmslpc" ]; then
  xrdcp -s root://cmseos.fnal.gov//store/user/$4/tarballs/$1/CMSSW_10_6_20.tgz .
else
  echo '&&& ERROR! Could not determine site, did not copy over tarball !!! &&&'
  echo $1
  echo ${13}
  echo ${14}
  echo ${15}
fi
echo '&&& Finished copying over tarball &&&'
source $VO_CMS_SW_DIR/cmsset_default.sh
tar -xf CMSSW_10_6_20.tgz
rm CMSSW_10_6_20.tgz
cd CMSSW_10_6_20/src
echo '&&& ReBuilding (scram b ProjectRename) &&&'
scramv1 b ProjectRename
eval `scramv1 runtime -sh`
echo '&&& Setup finished &&&'
echo ''
echo '&&& Current Directory and Contents: &&&'
pwd
ls -ldh *
echo ''
echo '&&& CMSSW_BASE: &&&'
echo $CMSSW_BASE
echo '&&& HOME: &&&'
echo $HOME
echo '&&& ROOTSYS: &&&'
echo $ROOTSYS
echo '&&& python version &&&'
python --version
echo '&&& ROOT version &&&'
export DISPLAY=localhost:0.0
root -l -q -e "gROOT->GetVersion()"
unset DISPLAY
echo ''

echo '&&& Moving to initial dir &&&'
cd $INITIAL_DIR
pwd
ls -ldh *
echo ''
echo '&&& Begin Main Payload, Call Subscript &&&'

. ./payload_$1.sh

echo ''
echo '&&& Finished Main Payload, Current Directory and Contents: &&&'
pwd
ls -ldh *
echo ''
FINALFILE=$2
if [ -f "$FINALFILE" ]; then
    :
else 
    echo 'ERROR: No final file!'
    exit 2
fi

echo '&&& Finished Main Job Payload &&&'
echo ''
echo '&&& Running Stageout Script &&&'
python stageout.py $3 $1
exitcode=$?
if [[ exitcode -eq 0 ]] ; then
    :
else
    echo 'ERROR: stageout exited with non-zero exit code!'
    exit 1
fi
echo ''
echo '&&& Finished &&&'
