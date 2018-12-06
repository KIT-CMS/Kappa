#!/bin/sh

_GT="94X_dataRun2_ReReco17_forValidation"

_FILE="root://xrootd-cms.infn.it//store/data/Run2017B/SingleMuon/MINIAOD/17Nov2017-v1/70000/04D5F12D-37D7-E711-9B97-02163E019BF0.root"
_dir="test_DM/${_GT}"
mkdir -p $_dir
cmsRun kappaSkim_cfg.py inputFiles=file://${_FILE} \
                        globalTag=${_GT} \
                        isData=1 \
                        outputFile=testKappaSkim_out_$_GT.root \
                        maxEvents=100 \
                        dumpPythonAndExit=0 2>&1 | tee cout_$_GT.log
mv cout_$_GT.log $_dir/
mv infos.log $_dir/
mv debugs.log $_dir/
mv testKappaSkim_out_${_GT}_numEvent100.root $_dir/

