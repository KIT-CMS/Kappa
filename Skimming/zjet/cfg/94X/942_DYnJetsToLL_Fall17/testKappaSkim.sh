#!/bin/sh

_FILE="/storage/c/dsavoiu/miniaod-test/mc/RunIIFall17/DY1JetsToLL/madgraphMLM_94X_mc2017_realistic_v10-v1/001FAA2D-AEDA-E711-ACB4-0CC47A4D7632.root"
_GT="94X_mc2017_realistic_v10"

cmsRun kappaSkim_cfg.py inputFiles=file://${_FILE} \
                        globalTag=${_GT} \
                        isData=0 \
                        outputFile=testKappaSkim_out_$_GT.root \
                        maxEvents=100 \
                        dumpPythonAndExit=0 2>&1 | tee cout_$_GT.log
