#!/bin/bash

./condor_submit.py plotting /cms/chiarito/eos/twoprong/sanity_plots/atto/Fullrun6-Apr2023/egamma18a/2023-04-17-14-43-12/v1p0-34-123c/ /cms/jwf82/work/atto_framework/egamma2018a_output --data --filesPerJob 2 --lumi 59830 -p bkg -d egamma2018a

./condor_submit.py plotting /cms/chiarito/eos/twoprong/sanity_plots/atto/Fullrun6-Apr2023/egamma18b/2023-04-17-14-43-14/v1p0-34-123c/ /cms/jwf82/work/atto_framework/egamma2018b_output --data --filesPerJob 2 --lumi 59830 -p bkg -d egamma2018b
    
./condor_submit.py plotting /cms/chiarito/eos/twoprong/sanity_plots/atto/Fullrun6-Apr2023/egamma18c/2023-04-17-14-43-16/v1p0-34-123c/ /cms/jwf82/work/atto_framework/egamma2018c_output --data --filesPerJob 2 --lumi 59830 -p bkg -d egamma2018c
 
./condor_submit.py plotting /cms/chiarito/eos/twoprong/sanity_plots/atto/Fullrun6-Apr2023/egamma18d/2023-04-17-14-43-19/v1p0-34-123c/ /cms/jwf82/work/atto_framework/egamma2018d_output --data --filesPerJob 2 --lumi 59830 -p bkg -d egamma2018d
