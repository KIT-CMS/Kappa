#!/bin/sh

_GT="106X_dataRun2_v20"
_NEVT=100
_IS_DATA=1
_GRID_PATH_PREFIX="root://xrootd-cms.infn.it/"
_FILE="/store/data/Run2017B/DoubleMuon/MINIAOD/09Aug2019_UL2017-v1/260000/015A2805-A748-B147-8E81-9A3D7247F4D1.root"
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
