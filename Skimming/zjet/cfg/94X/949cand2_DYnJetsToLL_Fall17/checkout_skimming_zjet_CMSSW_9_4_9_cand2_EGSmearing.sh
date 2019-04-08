#!/bin/sh
#
# Checkout script for Kappa (skimming)
######################################
#
# analysis:       JEC
# description:    derivation of L3Residual corrections with Z+Jets data
# CMSSW version:  CMSSW_9_4_9
# created:        2018-07-23

# set CMSSW-version
# _CMSSW_VERSION="CMSSW_9_4_9_cand2"
_CMSSW_VERSION="CMSSW_9_4_10"


# checkout workflow
# =================


# -- initialization

# get CMS environment
source /cvmfs/cms.cern.ch/cmsset_default.sh

# create a CMSSW working directory
cmsrel $_CMSSW_VERSION

# go to src directory for checkout
cd "${_CMSSW_DIR}/src"

# set up CMSSW
cmsenv

# initialize git repository from CMSSW
git cms-init --upstream-only
# --upstream-only avoids having github access to the cmssw project to clone the code!


# -- apply CMSSW modifications, backports, etc. (user code)

# https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaPostRecoRecipes
# E/Gamma post-reco tools (scale/smearing correction, VIDs)
git cms-merge-topic cms-egamma:EgammaID_949 #if you want the V2 IDs, otherwise skip
git cms-merge-topic cms-egamma:EgammaPostRecoTools_940 #just adds in an extra file to have a setup function to make things easier
# -- get some modules directly from github

# Kappa
git clone https://github.com/KIT-CMS/Kappa.git $CMSSW_BASE/src/Kappa

# Jet Toolbox
git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_94X


# -- compile using scram
scram b -j20
