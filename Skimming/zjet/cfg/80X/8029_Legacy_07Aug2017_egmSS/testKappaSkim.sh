#!/bin/sh

_GT="80X_dataRun2_2016LegacyRepro_v4"

_FILE="/storage/c/tberger/testfiles/skimming_input/data/Run2016D_DoubleEG_MINIAOD_07Aug17-v1_testfile.root"
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
