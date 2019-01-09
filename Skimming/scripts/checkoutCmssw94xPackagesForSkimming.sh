#!/bin/bash
set -e # exit on errors

### Basic CMSSW setup ###

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_9_4_12
cd CMSSW_9_4_12/src
eval `scramv1 runtime -sh`

git cms-init

### Add-packages ###

# Get DeepFlavour b-tagger ---> optional
#git cms-addpkg RecoBTag/TensorFlow
#git cherry-pick 94ceae257f846998c357fcad408986cc8a039152

### Merge-topics ###

# Get code for electron V2 ID's (trained on 94X MC's)
git cms-merge-topic cms-egamma:EgammaID_949

# Get code for electron scale & smear corrections
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940

# Get DPF based Tau ID (and Tau ID Embedder) ---> DPF is optional; remove databases for the time-being
git cms-merge-topic cms-tau-pog:CMSSW_9_4_X_tau_pog_DNNTauIDs #merge experimental code for 94X
git clone https://github.com/cms-tau-pog/RecoTauTag-TrainingFiles -b master RecoTauTag/TrainingFiles/data
wget https://raw.githubusercontent.com/greyxray/TauAnalysisTools/CMSSW_9_4_X_tau-pog_RunIIFall17/TauAnalysisTools/python/runTauIdMVA.py -P RecoTauTag/RecoTau/python/

# Get latest anti-e discriminator MVA6v2 (2017 training) ---> optional
#git cms-merge-topic cms-tau-pog:CMSSW_9_4_X_tau-pog_updateAntiEDisc

# Ge the prefiring map
git cms-merge-topic lathomas:L1Prefiring_9_4_9
mkdir L1Prefiring/EventWeightProducer/data
mv L1Prefiring/EventWeightProducer/files/L1PrefiringMaps_new.root L1Prefiring/EventWeightProducer/data/L1PrefiringMaps_new.root

### Analysis group related software (ntuplizer, skimming, private MiniAOD, etc.) ###

# KIT related packages
git clone git@github.com:KIT-CMS/Kappa.git -b dictchanges
git clone git@github.com:janekbechtel/grid-control.git

CORES=`grep -c ^processor /proc/cpuinfo`
scram b -j $CORES
