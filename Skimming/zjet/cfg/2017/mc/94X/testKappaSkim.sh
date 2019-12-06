#!/bin/sh

_GT="94X_mc2017_realistic_v14"


_FILE="root://xrootd-cms.infn.it//store/mc/RunIIFall17MiniAODv2/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14_ext3-v1/30002/FE18C0A5-27E3-E911-8643-EC0D9A8221EE.root"
#_FILE="root://xrootd-cms.infn.it//store/data/Run2017B/SingleMuon/MINIAOD/09Aug2019_UL2017-v1/50000/F738CB6B-FEB4-AC4D-A549-F25912F0C896.root"

_dir="test_DM/${_GT}"
mkdir -p $_dir
#cmsRun test_cfg.py inputFiles=${_FILE} \

cmsRun kappaSkim_test_cfg.py inputFiles=${_FILE} \
                        globalTag=${_GT} \
                        isData=0\
                        outputFile=testKappaSkim_out_$_GT.root \
                        maxEvents=100 \
                        dumpPythonAndExit=0 2>&1 | tee cout_$_GT.log
mv cout_$_GT.log $_dir/
mv infos.log $_dir/
mv debugs.log $_dir/
mv testKappaSkim_out_${_GT}_numEvent100.root $_dir/

