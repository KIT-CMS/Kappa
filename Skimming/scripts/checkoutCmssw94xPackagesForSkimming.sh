#!/bin/bash
set -e # exit on errors

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_9_4_10
cd CMSSW_9_4_10/src
eval `scramv1 runtime -sh`

git cms-init

# Get code for electron scale & smear corrections
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940

# Get recipes to re-correct MET (also for ECAL prefiring)
git cms-merge-topic cms-met:METRecipe94xEEnoisePatch

# KIT related packages
git clone https://github.com/KIT-CMS/Kappa.git -b dictchanges
git clone https://github.com/janekbechtel/grid-control.git

# Get python code to rerun Tau ID's
cd Kappa/Skimming/python
wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py
cd -

# Get working version of HTXSRivetProducer
git cms-addpkg GeneratorInterface/RivetInterface
cd GeneratorInterface/RivetInterface/plugins
rm HTXSRivetProducer.cc
wget https://raw.githubusercontent.com/perrozzi/cmssw/HTXS_clean/GeneratorInterface/RivetInterface/plugins/HTXSRivetProducer.cc
cd -

scram b -j 4
