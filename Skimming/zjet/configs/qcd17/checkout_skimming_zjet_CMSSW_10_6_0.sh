#!/bin/sh
#
# Checkout script for Kappa (skimming)
######################################
#
# analysis:       JEC
# description:    derivation of L3Residual corrections with Z+Jets data
# CMSSW version:  CMSSW_10_2_8
# created:        2018-12-10


_CMSSW_VERSION="CMSSW_10_6_0"
_CMSSW_SCRAM_SUFFIX="skimUL2017"

_CMSSW_DIR="${_CMSSW_VERSION}"
if [ "${_CMSSW_SCRAM_SUFFIX}" != "" ]; then
    _CMSSW_DIR="${_CMSSW_DIR}_${_CMSSW_SCRAM_SUFFIX}"
fi

# checkout workflow
# =================


# -- checks

# check for CMSSW
if [ -z "${CMS_PATH}" ]; then
    echo "[ERROR] Cannot find CMSSW: environment variable \$CMS_PATH is not set!"
    echo "[INFO] Have you done `source /cvmfs/cms.cern.ch/cmsset_default.sh`?"
fi

# -- initialization

# create a CMSSW working directory
echo "[INFO] Can create working area '${_CMSSW_DIR}'?"
if [ -d "${_CMSSW_DIR}" ]; then
    echo "[ERROR] Cannot create working area '${_CMSSW_DIR}': directory already exists!"
fi
scramv1 project -n "${_CMSSW_DIR}" CMSSW "${_CMSSW_VERSION}"

cd "${_CMSSW_DIR}/src"
eval `scramv1 runtime -sh`

# initialize git repository from CMSSW
git cms-init

# -- apply CMSSW modifications, backports, etc. (user code)

# -- get some modules directly from github

# Kappa
git clone git@github.com:KIT-CMS/Kappa.git $CMSSW_BASE/src/Kappa

# Electron-Gamma Smearing according to recipe from https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaPostRecoRecipes
#git cms-merge-topic cms-egamma:EgammaPostRecoTools #just adds in an extra file to have a setup function to make things easier 
#git cms-merge-topic cms-egamma:PhotonIDValueMapSpeedup1029 #optional but speeds up the photon ID value module so things fun faster
#git cms-merge-topic cms-egamma:slava77-btvDictFix_10210 #fixes the Run2018D dictionary issue, see https://github.com/cms-sw/cmssw/issues/26182, may not be necessary for later releases, try it first and see if it works
#now to add the scale and smearing for 2018 (eventually this will not be necessary in later releases but is harmless to do regardless)
#git cms-addpkg EgammaAnalysis/ElectronTools
#rm EgammaAnalysis/ElectronTools/data -rf
#git clone https://github.com/cms-data/EgammaAnalysis-ElectronTools.git EgammaAnalysis/ElectronTools/data

# Jet Toolbox
git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_102X_v2
#git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_101X
# git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_94X

# -- compile using scram
scramv1 b -j20
