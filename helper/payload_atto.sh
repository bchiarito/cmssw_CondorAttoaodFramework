#! /bin/bash
echo "&&& Now Inside: payload_atto.sh &&&"
echo "&&& Here there are all the input arguments &&&"
echo $@

echo ""
echo "&&& Run &&&"

echo '&&& Begin Job Main Payload &&&'
python CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_atto/nano_postproc.py infiles_$3.dat . --drop atto_branch_selection.txt --filter="$8" -n=-1 --$5 --dataset=${9} --proc=$3 --outfile=$2 --report=report_$3.txt --add_recophi=${11}
python CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_atto/metadata_create.py report_$3.txt $2 ${9} $3 --xs=${10}

echo "&&& Done: payload_atto.sh &&&"


