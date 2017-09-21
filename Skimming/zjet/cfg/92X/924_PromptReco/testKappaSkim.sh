#!/bin/sh

cmsRun kappaSkim_cfg.py inputFiles=file:///storage/9/dsavoiu/zjet/miniaod-test/data/Run2017C/DoubleMuon/PromptReco-v1/22A34E8E-896D-E711-8520-02163E01A6AF.root \
                        globalTag=92X_dataRun2_v4 \
                        isData=1 \
                        outputFile=testKappaSkim_out.root \
                        maxEvents=100
