#!/bin/sh

_GT="106X_dataRun2_v32"
_NEVT=100
_IS_DATA=true
_GRID_PATH_PREFIX="file:"
_FILE="/work/jec/pickevents_MINI_Run2016B_DoubleMuon.root"
_DIR="test/${_GT}"

mkdir -p $_DIR

echo "##############################################################################"
echo "STARTING cmsRun !!!!"
echo "##############################################################################"

cmsRun ../kappaSkim_default_cfg_preVFP.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=${_IS_DATA} \
                        outputFile=pickKappaSkim_out_${_GT}.root \
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

if [ -f pickKappaSkim_out_${_GT}_numEvent${_NEVT}.root ]; then
    mv pickKappaSkim_out_${_GT}_numEvent${_NEVT}.root $_DIR/
fi
