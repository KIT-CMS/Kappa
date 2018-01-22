#!/bin/bash

_CMSSW_VERSION="CMSSW_9_4_2"


# checkout workflow
# =================


# -- checks

# check for CMSSW
if [[ -z "${CMS_PATH}" ]]; then
    echo "[ERROR] Cannot find CMSSW: environment variable \$CMS_PATH is not set!"
    echo "[INFO] Have you done `source /cvmfs/cms.cern.ch/cmsset_default.sh`?"
fi


# -- initialization

# create a CMSSW working directory
echo "[INFO] Can create working area '${_CMSSW_VERSION}'?"
if [ -d "${_CMSSW_VERSION}" ]; then
    echo "[ERROR] Cannot create working area '${_CMSSW_VERSION}': directory already exists!"
fi
scramv1 project CMSSW "${_CMSSW_VERSION}"

cd "${_CMSSW_VERSION}/src"
eval `scramv1 runtime -sh`

# initialize git repository from CMSSW
git cms-init

# -- apply CMSSW modifications, backports, etc. (user code)

# (none yet)

# -- get some modules directly from github

# Kappa
git clone https://github.com/KIT-CMS/Kappa.git

# Jet Toolbox
# FIXME/TODO: update to correct branch when it becomes available
#git clone https://github.com/cms-jet/JetToolbox.git JMEAnalysis/JetToolbox --branch jetToolbox_94X
git clone https://github.com/cms-jet/JetToolbox.git JMEAnalysis/JetToolbox --branch jetToolbox_91X


# -- compile using scram
scramv1 b -j12
