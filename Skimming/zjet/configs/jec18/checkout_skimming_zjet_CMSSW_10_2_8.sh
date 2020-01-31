#!/bin/sh
#
# Checkout script for Kappa (skimming)
######################################
#
# analysis:       JEC
# description:    derivation of L3Residual corrections with Z+Jets data
# CMSSW version:  CMSSW_10_2_8
# created:        2018-12-10


_CMSSW_VERSION="CMSSW_10_2_8"
_CMSSW_SCRAM_SUFFIX="skim2018"

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
git clone https://github.com/KIT-CMS/Kappa.git $CMSSW_BASE/src/Kappa

# Jet Toolbox
# FIXME/TODO: update to correct branch when it becomes available
#git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_101X
git clone https://github.com/cms-jet/JetToolbox.git $CMSSW_BASE/src/JMEAnalysis/JetToolbox --branch jetToolbox_94X


# -- compile using scram
scramv1 b -j20
