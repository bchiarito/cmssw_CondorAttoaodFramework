#! /bin/bash
echo ">>> Starting job on" `date`
echo ">>> Running on: `uname -a`"
echo ">>> System software: `cat /etc/redhat-release`"
echo ""
echo "&&& Here there are all the input arguments &&&"
echo "&&& unpacker stageout proc mc/data year lumi twoprongSB photonSB selection &&&"
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
echo 'python' $1 $3
python $1 $3
echo ''
echo '&&& New contents: &&&'
ls -ldh *
echo ''

echo '&&& Setup CMSSW area &&&'
export HOME=$INITIAL_DIR
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
export SCRAM_ARCH=slc7_amd64_gcc820
#source $VO_CMS_SW_DIR/cmsset_default.sh
# bring in the tarball you created before with caches and large files excluded:
echo '&&& About to copying over tarball &&&'
xrdcp -s root://cmseos.fnal.gov//store/user/bchiari1/tarballs/CMSSW_10_6_20.tgz .
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
echo '&&& Begin Job Main Payload &&&'
python nano_postproc.py infiles_$3.dat . --drop my_ana_drop.txt --filter="$9" --add_recophi HPID -n=-1 --$4 > report.txt
#ls $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/
#python $CMSSW_BASE/src/PhysicsTools/NanoAODTools/scripts/haddnano.py out.root *_Skim.root
echo ''
echo '&&& Current Directory and Contents: &&&'
pwd
ls -ldh *
echo ''
FINALFILE=out.root
if [ -f "$FINALFILE" ]; then
    :
else 
    echo 'ERROR: No final file!'
    exit 2
fi

echo ''
echo '&&& Finished Main Job Payload &&&'
echo ''
echo '&&& Running Stageout Script with command: &&&'
echo 'python' $2 $3
python $2 $3
exitcode=$?
if [[ exitcode -eq 0 ]] ; then
    :
else
    echo 'ERROR: stageout exited with non-zero exit code!'
    exit 1
fi
echo ''
echo '&&& Finished &&&'
