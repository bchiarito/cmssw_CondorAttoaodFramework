#! /bin/bash
echo "&&& Now Inside: payload_atto.sh &&&"
echo "&&& Here there are all the input arguments &&&"
echo $@

echo ""
echo "&&& Run &&&"

echo '&&& Begin Job Main Payload &&&'
python CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_atto/nano_postproc.py infiles_$3.dat . --drop ${11} --filter="$8" -n=-1 --$5 --dataset=${9} --proc=$3 --outfile=$2 --report=report_$3.txt --analyzer=${16}
if [ ${16} == "main" ]; then
  python CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_atto/metadata_create.py report_$3.txt $2 ${9} $3 --xs=${10}
fi
if [ ${16} == "trigger" ]; then
  python CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_atto/metadata_create.py report_$3.txt $2 ${9} $3 --xs=${10}
fi

echo "&&& Done: payload_atto.sh &&&"


