#!/bin/sh

_GT="102X_dataRun2_Sep2018Rereco_v1"
_NEVT=1000
_GRID_PATH_PREFIX="root://xrootd-cms.infn.it/"

_FILE="/store/data/Run2018A/DoubleMuon/MINIAOD/17Sep2018-v2/00000/0491D3FD-85FD-1A4E-A4E9-EC8BB47BF373.root"
_dir="test_DM/${_GT}"
mkdir -p $_dir
cmsRun kappaSkim_cfg.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=1 \
                        outputFile=testKappaSkim_out_${_GT}.root \
                        maxEvents=${_NEVT} \
                        dumpPythonAndExit=0 2>&1 | tee cout_${_GT}.log
mv cout_$_GT.log $_dir/
mv infos.log $_dir/
mv debugs.log $_dir/
mv testKappaSkim_out_${_GT}_numEvent${_NEVT}.root $_dir/


_FILE="/store/data/Run2018A/EGamma/MINIAOD/17Sep2018-v2/100000/00A356F9-0B7B-B943-A3F4-57B5106F9AFF.root"
_dir="test_EG/${_GT}"
mkdir -p $_dir
cmsRun kappaSkim_cfg.py inputFiles=${_GRID_PATH_PREFIX}${_FILE} \
                        globalTag=${_GT} \
                        isData=1 \
                        outputFile=testKappaSkim_out_${_GT}.root \
                        maxEvents=${_NEVT} \
                        dumpPythonAndExit=0 2>&1 | tee cout_${_GT}.log
mv cout_$_GT.log $_dir/
mv infos.log $_dir/
mv debugs.log $_dir/
mv testKappaSkim_out_${_GT}_numEvent${_NEVT}.root $_dir/
