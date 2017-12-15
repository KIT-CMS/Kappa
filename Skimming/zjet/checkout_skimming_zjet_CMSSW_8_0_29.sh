#!/bin/sh
#
# Checkout script for Kappa (skimming)
######################################
#
# analysis:       JEC
# description:    derivation of L3Residual corrections with Z+Jets data
# CMSSW version:  CMSSW_8_0_29
# created:        2017-12-15


_CMSSW_VERSION="CMSSW_8_0_29"

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

# https://github.com/cms-sw/cmssw/pull/16174#pullrequestreview-5167487
# Fix for Puppi MET and MET significance compatibility between AOD and miniAOD (80X)
git cms-merge-topic cms-met:METRecipe_8020 -u

# https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription#Instructions_for_8_0_X_X_26_patc
# Fix for the re-clustering of the CHS jets on the fly
git cms-merge-topic cms-met:METRecipe_80X_part2 -u

# Tau POG backport of tauID
# NOTE: Cannot use cms-merge-topic, since backport is intended for "CMSSW_8_0_26_patch1"

_foreign_repo="cms-tau-pog"
_foreign_ref="CMSSW_8_0_X_tau-pog_tauIDOnMiniAOD-legacy-backport-81X"

git fetch -n "https://github.com/${_foreign_repo}/cmssw.git" +${_foreign_ref}:${_foreign_repo}/${_foreign_ref}
git rebase --onto "${_CMSSW_VERSION}" CMSSW_8_0_26_patch1 "${_foreign_repo}/${_foreign_ref}"
git cms-sparse-checkout "${_CMSSW_VERSION}" "${_foreign_repo}/${_foreign_ref}"
git read-tree -mu HEAD
git checkout "from-${_CMSSW_VERSION}"
git merge "${_foreign_repo}/${_foreign_ref}" --no-ff -m "Merged ${_foreign_ref} from repository ${_foreign_repo} (done by Kappa checkout script)"

# -- get some modules directly from github

# Kappa
git clone https://github.com/KIT-CMS/Kappa.git

# Jet Toolbox
git clone https://github.com/cms-jet/JetToolbox.git JMEAnalysis/JetToolbox --branch jetToolbox_80X


# -- compile using scram
scramv1 b -j10
