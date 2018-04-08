#!/bin/bash
set -e # exit on errors

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_9_4_6
cd CMSSW_9_4_6/src
eval `scramv1 runtime -sh`

git cms-init

# KIT related packages
git clone https://github.com/KIT-CMS/Kappa.git -b dictchanges
git clone https://github.com/janekbechtel/grid-control.git

scram b -j 4
