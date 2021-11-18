#!/bin/sh

_GT="106X_upgrade2018_realistic_v16_L1v1"
_NEVT=100
_IS_DATA=false
_GRID_PATH_PREFIX="root://xrootd-cms.infn.it/"
_FILE="/store/mc/RunIISummer20UL18MiniAODv2/ZZ_TuneCP5_13TeV-pythia8/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/120000/1FBDEBC9-8063-DD41-B96D-89C6706A8B88.root"
_DIR="test/${_GT}"

mkdir -p $_DIR

echo "##############################################################################"
echo "STARTING cmsRun !!!!"
echo "##############################################################################"

cmsRun ../kappaSkim_default_cfg.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=${_IS_DATA} \
                        outputFile=testKappaSkim_out_${_GT}.root \
                        maxEvents=${_NEVT} \
                        dumpPython=1 2>&1 | tee cout_${_GT}.log

echo "##############################################################################"
echo "cmsRun terminated !!!!"
echo "##############################################################################"

if [ -f cout_$_GT.log ]; then
    mv cout_$_GT.log $_DIR/
fi

if [ -f infos.log ]; then
    mv infos.log $_DIR/
fi

if [ -f debugs.log ]; then
    mv debugs.log $_DIR/
fi

if [ -f testKappaSkim_out_${_GT}_numEvent${_NEVT}.root ]; then
    mv testKappaSkim_out_${_GT}_numEvent${_NEVT}.root $_DIR/
fi
