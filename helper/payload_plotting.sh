#! /bin/bash
echo "&&& Now Inside: payload_plotter.sh &&&"
echo "&&& Here there are all the input arguments &&&"
echo $@

echo ""
echo "&&& Run &&&"
python CMSSW_10_6_20/src/PhysicsTools/NanoAODTools/python/fmk_plotting/nanoaodtools_looper.py local --$5 --out $2 --lumi=$7
echo "&&& Done: payload_plotter.sh &&&"
