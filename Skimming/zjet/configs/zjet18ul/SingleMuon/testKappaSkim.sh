#!/bin/sh

_GT="106X_dataRun2_v35"
_NEVT=1000
_IS_DATA=1
_GRID_PATH_PREFIX="root://xrootd-cms.infn.it/"
_FILE="/store/data/Run2018A/SingleMuon/MINIAOD/UL2018_MiniAODv2-v2/120000/0481F84F-6CC0-1846-93BC-B6065B9BDD7E.root"
_DIR="test_with_bool/${_GT}"

mkdir -p $_DIR

echo "##############################################################################"
echo "STARTING cmsRun !!!!"
echo "##############################################################################"

cmsRun ../kappaSkim_default_cfg.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=${_IS_DATA} \
                        outputFile=testKappaSkim_out_${_GT}_numEvents${_NEVT}.root \
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

if [ -f testKappaSkim_out_${_GT}_numEvents${_NEVT}.root ]; then
    mv testKappaSkim_out_${_GT}_numEvents${_NEVT}.root $_DIR/
fi
