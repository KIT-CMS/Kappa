#!/bin/sh

_GT="94X_dataRun2_ReReco_EOY17_v2"

_FILE="/storage/c/dsavoiu/miniaod-test/data/Run2017B/DoubleMuon/ReReco-17Nov2017-v1/0E73FD13-49D6-E711-A914-7845C4FC3B48.root"
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

_FILE="/storage/c/tberger/testfiles/skimming_input/data/Run2017B_DoubleEG_MINIAOD_17Nov2017-v1_testfile.root"
_dir="test_DE/${_GT}"
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
