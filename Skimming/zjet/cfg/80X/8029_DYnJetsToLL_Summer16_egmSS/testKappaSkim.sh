#!/bin/sh

_GT="80X_mcRun2_asymptotic_2016_TrancheIV_v6"

#_FILE="/storage/c/tberger/testfiles/skimming_input/data/Run2016D_DoubleEG_MINIAOD_07Aug17-v1_testfile.root"
_FILE="/storage/c/tberger/testfiles/skimming_input/mc/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_MINIAODSIM_PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1_testfile.root"
_dir="test_DYNJ/${_GT}"
mkdir -p $_dir
cmsRun kappaSkim_cfg.py inputFiles=file://${_FILE} \
                        globalTag=${_GT} \
                        isData=0 \
                        outputFile=testKappaSkim_out_$_GT.root \
                        maxEvents=100 \
                        dumpPythonAndExit=0 2>&1 | tee cout_$_GT.log
mv cout_$_GT.log $_dir/
mv infos.log $_dir/
mv debugs.log $_dir/
mv testKappaSkim_out_${_GT}_numEvent100.root $_dir/
