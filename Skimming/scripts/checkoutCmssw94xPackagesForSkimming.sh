#!/bin/bash
set -e # exit on errors

### Basic CMSSW setup ###

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_9_4_11_cand2
cd CMSSW_9_4_11_cand2/src
eval `scramv1 runtime -sh`

git cms-init

### Add-packages ###

# Get DeepFlavour b-tagger ---> optional
git cms-addpkg RecoBTag/TensorFlow
git cherry-pick 94ceae257f846998c357fcad408986cc8a039152

# Get working version of HTXSRivetProducer ---> mainly relevant for SM HTT
git cms-addpkg GeneratorInterface/RivetInterface
cd GeneratorInterface/RivetInterface/plugins
rm HTXSRivetProducer.cc
wget https://raw.githubusercontent.com/perrozzi/cmssw/HTXS_clean/GeneratorInterface/RivetInterface/plugins/HTXSRivetProducer.cc
cd -

### Merge-topics ###

# Get code for electron V2 ID's (trained on 94X MC's)
git cms-merge-topic guitargeek:EgammaID_949

# Get code for electron scale & smear corrections
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940

# Get recipes to re-correct MET (also for ECAL noise)
git cms-merge-topic cms-met:METFixEE2017_949_v2

# Get DPF based Tau ID (and Tau ID Embedder) ---> DPF is optional
git cms-merge-topic ocolegro:dpfisolation # consists updated version of runTauIdMVA.py (RecoTauTag/RecoTau/python/runTauIdMVA.py). Originally, this .py file comes from https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py

# Get latest anti-e discriminator MVA6v2 (2017 training) ---> optional
git cms-merge-topic cms-tau-pog:CMSSW_9_4_X_tau-pog_updateAntiEDisc

### Analysis group related software (ntuplizer, skimming, private MiniAOD, etc.) ###

# KIT related packages
git clone https://github.com/KIT-CMS/Kappa.git -b dictchanges
git clone https://github.com/janekbechtel/grid-control.git

CORES=`grep -c ^processor /proc/cpuinfo`
scram b -j $CORES
