#!/bin/sh

_GT="102X_upgrade2018_realistic_v12"
_NEVT=1000
_GRID_PATH_PREFIX="root://xrootd-cms.infn.it/"

# _FILE="/store/mc/RunIIAutumn18MiniAOD/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15-v2/120000/F5C1F472-7B01-3247-9004-CF5D34307413.root"
_FILE="/store/mc/RunIIFall17MiniAOD/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/94X_mc2017_realistic_v10-v1/20000/FECF3F74-6CD7-E711-8B51-A4BF0112BC02.root"


_dir="test_DY2/${_GT}"
mkdir -p $_dir
cmsRun ../kappaSkim_1208_mc_default_cfg.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=0 \
                        outputFile=testKappaSkim_out_${_GT}.root \
                        maxEvents=${_NEVT} \
                        dumpPythonAndExit=0 2>&1 | tee cout_${_GT}.log
mv cout_$_GT.log $_dir/
mv infos.log $_dir/
mv debugs.log $_dir/
mv testKappaSkim_out_${_GT}_numEvent${_NEVT}.root $_dir/
