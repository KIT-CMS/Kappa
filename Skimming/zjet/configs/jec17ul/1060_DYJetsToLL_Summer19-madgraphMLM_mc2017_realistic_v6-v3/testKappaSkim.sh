#!/bin/sh

_GT="106X_mc2017_realistic_v6"
_NEVT=100
_IS_DATA=0
_GRID_PATH_PREFIX="root://xrootd-cms.infn.it/"
_FILE="/store/mc/RunIISummer19UL17MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/106X_mc2017_realistic_v6-v2/70000/FBC4E43E-2C35-974A-84C9-29AD0430BD39.root"
_DIR="test/${_GT}"

mkdir -p $_dir

cmsRun ../kappaSkim_default_cfg.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=_IS_DATA \
                        outputFile=testKappaSkim_out_${_GT}.root \
                        maxEvents=${_NEVT} \
                        dumpPython=1 2>&1 | tee cout_${_GT}.log
mv cout_$_GT.log $_DIR/
mv infos.log $_DIR/
mv debugs.log $_DIR/
mv testKappaSkim_out_${_GT}_numEvent${_NEVT}.root $_DIR/
