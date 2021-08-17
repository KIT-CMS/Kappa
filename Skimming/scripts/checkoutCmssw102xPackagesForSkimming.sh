#!/bin/bash
set -e # exit on errors

### Basic CMSSW setup ###
export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh

scramv1 project CMSSW_10_2_19
cd CMSSW_10_2_19/src
eval `scramv1 runtime -sh`

git cms-init

### Add-packages ###
git cms-addpkg EgammaAnalysis/ElectronTools
rm EgammaAnalysis/ElectronTools/data -rf
git clone git@github.com:cms-data/EgammaAnalysis-ElectronTools.git EgammaAnalysis/ElectronTools/data

### Merge-topics ###

# EGamma-POG
# https://twiki.cern.ch/twiki/bin/view/CMS/EgammaMiniAODV2, https://twiki.cern.ch/twiki/bin/view/CMS/EgammaPostRecoRecipes
# The 2018 MiniAOD includes the Fall17V2 IDs for electrons but not for photons.
git cms-merge-topic cms-egamma:slava77-btvDictFix_10210 # fixes the Run2018D dictionary issue, see https://github.com/cms-sw/cmssw/issues/26182, may not be necessary for later releases

scram b -j $CORES
git clone git@github.com:cms-egamma/EgammaPostRecoTools.git  EgammaUser/EgammaPostRecoTools
cd  EgammaUser/EgammaPostRecoTools
git checkout master
cd -
echo $CMSSW_BASE
cd $CMSSW_BASE/src

### Analysis group related software (ntuplizer, skimming, private MiniAOD, etc.) ###

# KIT related packages
git clone --recursive git@github.com:KIT-CMS/Kappa.git -b dictchanges
git clone git@github.com:KIT-CMS/grid-control.git

CORES=`grep -c ^processor /proc/cpuinfo`
scram b -j $CORES
