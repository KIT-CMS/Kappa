#!/bin/sh

_FILE="root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAOD/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/94X_mc2017_realistic_v10-v1/20000/FECF3F74-6CD7-E711-8B51-A4BF0112BC02.root"
# _FILE="root://cms-xrd-global.cern.ch//store/mc/RunIIFall17MiniAODv2/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/70000/FC35C315-6E42-E811-A2AD-AC162DACB208.root"
# _FILE="/storage/c/dsavoiu/miniaod-test/mc/RunIIFall17/DY1JetsToLL/madgraphMLM_94X_mc2017_realistic_v10-v1/001FAA2D-AEDA-E711-ACB4-0CC47A4D7632.root"
_GT="94X_mc2017_realistic_v10"

cmsRun kappaSkim_cfg.py inputFiles=file://${_FILE} \
                        globalTag=${_GT} \
                        isData=0 \
                        outputFile=testKappaSkim_out_$_GT.root \
                        maxEvents=10 \
			# edmOut=test.root \
                        dumpPythonAndExit=0 2>&1 | tee cout_$_GT.log
