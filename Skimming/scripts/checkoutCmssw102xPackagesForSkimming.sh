#!/bin/bash
set -e # exit on errors

### Basic CMSSW setup ###
export SCRAM_ARCH=slc6_amd64_gcc700
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_10_2_13
cd CMSSW_10_2_13/src
eval `scramv1 runtime -sh`

git cms-init

### Add-packages ###

### Merge-topics ###
git cms-merge-topic ArturAkh:stxs_1p1 # adapted HTXS code for stage 1.1; used reference: https://gitlab.cern.ch/LHCHIGGSXS/LHCHXSWG2/STXS

# EGamma-POG
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2, https://twiki.cern.ch/twiki/bin/view/CMS/EgammaPostRecoRecipes
# The 2018 MiniAOD includes the Fall17V2 IDs for electrons but not for photons.
git cms-merge-topic cms-egamma:EgammaPostRecoTools # just adds in an extra file to have a setup function to make things easier

### Analysis group related software (ntuplizer, skimming, private MiniAOD, etc.) ###

# KIT related packages
git clone git@github.com:KIT-CMS/Kappa.git -b dictchanges_10_2
git clone git@github.com:janekbechtel/grid-control.git

CORES=`grep -c ^processor /proc/cpuinfo`
scram b -j $CORES
