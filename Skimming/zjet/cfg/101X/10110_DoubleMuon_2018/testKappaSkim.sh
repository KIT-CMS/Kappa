#!/bin/sh

_FILE="root://cms-xrd-global.cern.ch//store/data/Run2018A/DoubleMuon/MINIAOD/PromptReco-v3/000/316/995/00000/CE5942A3-D866-E811-8A80-02163E01800D.root"
_GT="101X_dataRun2_Prompt_v10"

cmsRun kappaSkim_DoubleMuon_Run2018A-PromptReco-v3_cfg.py inputFiles=file://${_FILE} \
                        globalTag=${_GT} \
                        isData=1 \
                        outputFile=testKappaSkim_out_$_GT.root \
                        maxEvents=100 \
                        dumpPythonAndExit=0 2>&1 | tee cout_$_GT.log
