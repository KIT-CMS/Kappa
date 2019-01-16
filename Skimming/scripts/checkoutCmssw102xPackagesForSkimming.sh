#!/bin/bash
set -e # exit on errors

### Basic CMSSW setup ###
export SCRAM_ARCH=slc6_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_10_2_9
cd CMSSW_10_2_9/src
eval `scramv1 runtime -sh`

git cms-init

### Add-packages ###

# TODO: conflict; check if cherry-pick needed at all
# Get DeepFlavour b-tagger ---> optional
git cms-addpkg RecoBTag/TensorFlow
#git cherry-pick 94ceae257f846998c357fcad408986cc8a039152

### Merge-topics ###

# TODO: check the recipe
# Get code for electron V2 ID's (trained on 94X MC's)
# git cms-merge-topic cms-egamma:EgammaID_1023

# TODO: confirm that not needed
# Get code for electron scale & smear corrections
#git cms-merge-topic cms-egamma:EgammaPostRecoTools_940

# TODO: with switch to next release should be backported
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Running_of_the_DNN_based_tau_ID
# Get new DNN based Tau ID's and new Anti-Electron Disc training MVA6v3
#git cms-merge-topic ArturAkh:DNNTauIDs_andAntiEDiscv3
git cms-merge-topic cms-tau-pog:CMSSW_10_2_X_tau_pog_DNNTauIDs
git clone https://github.com/cms-tau-pog/RecoTauTag-TrainingFiles -b master RecoTauTag/TrainingFiles/data

# Ge the prefiring map
# from private communication, valid till Moriond at least
git cms-merge-topic lathomas:L1Prefiring_10_2_6
mkdir L1Prefiring/EventWeightProducer/data
mv L1Prefiring/EventWeightProducer/files/L1PrefiringMaps_new.root L1Prefiring/EventWeightProducer/data/L1PrefiringMaps_new.root

### Analysis group related software (ntuplizer, skimming, private MiniAOD, etc.) ###

# KIT related packages
git clone git@github.com:KIT-CMS/Kappa.git -b dictchanges
git clone git@github.com:KIT-CMS/grid-control.git

CORES=`grep -c ^processor /proc/cpuinfo`
scram b -j $CORES
