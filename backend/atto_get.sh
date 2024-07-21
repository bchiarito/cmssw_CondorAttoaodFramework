#! /bin/sh

#if [[ "hexcms" == "hexcms" ]]; then

export PATH="/cvmfs/oasis.opensciencegrid.org/mis/apptainer/1.2.5/bin:$PATH"
cmssw-el7 "--bind /condor --bind /osg --bind /cms --bind /home --bind /users" -- backend/aux_atto_get.sh

#elif [[ "hexcms" == "cmslpc" ]]; then
#cmssw-el7 "--bind /uscms_data/d1/$USER/" -- backend/aux_atto_get.sh

#fi
