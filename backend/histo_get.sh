#! /bin/sh

if [[ $1 == "hexcms" ]]; then

export PATH="/cvmfs/oasis.opensciencegrid.org/mis/apptainer/1.2.5/bin:$PATH"
cmssw-el7 "--bind /condor --bind /osg --bind /cms --bind /home --bind /users" -- backend/aux_histo_get.sh

elif [[ $1 == "cmslpc" ]]; then
cmssw-el7 "--bind /uscms_data/d1/$USER/" -- backend/aux_histo_get.sh

else
echo "Please supply [hexcms] or [cmslpc] as positional argument!"

fi
