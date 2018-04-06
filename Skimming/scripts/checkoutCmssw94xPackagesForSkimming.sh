#!/bin/bash
set -e # exit on errors

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_9_4_4
cd CMSSW_9_4_4/src
eval `scramv1 runtime -sh`

git cms-init

# 2017 electron ID's
git cms-merge-topic lsoffi:CMSSW_9_4_0_pre3_TnP
git cms-merge-topic guitargeek:ElectronID_MVA2017_940pre3
scram b -j 4 # needed to have 'external' folder

cd $CMSSW_BASE/external
cd $SCRAM_ARCH
git clone https://github.com/lsoffi/RecoEgamma-ElectronIdentification.git data/RecoEgamma/ElectronIdentification/data
cd data/RecoEgamma/ElectronIdentification/data
git checkout CMSSW_9_4_0_pre3_TnP
cd $CMSSW_BASE/src

# 2017 tau ID's
git cms-merge-topic -u cms-tau-pog:CMSSW_9_4_X_tau-pog_newTauID-MCv1

# KIT related packages
git clone https://github.com/KIT-CMS/Kappa.git
git clone https://github.com/janekbechtel/grid-control.git

scram b -j 4
