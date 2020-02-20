#!/bin/bash

if [ -z $CMSSW_BASE ]; then
    echo "CMSSW not sourced! Abort"
    return
fi

cd ${CMSSW_BASE}/src

git cms-addpkg PhysicsTools/PatAlgos
git cms-merge-topic -u TaiSakuma:53X-met-131120-01
git cms-merge-topic -u cms-analysis-tools:5_3_14-updateSelectorUtils
git cms-merge-topic -u cms-analysis-tools:5_3_13_patch2-testNewTau
git cms-merge-topic -u cms-met:53X-MVaNoPuMET-20131217-01

git cms-addpkg RecoMET/METFilters
git clone https://github.com/KappaAnalysis/Kappa.git && cd Kappa && git checkout newtagging && cd ..
git clone https://github.com/cms-analysis/RecoMET-METAnalyzers.git RecoMET/METAnalyzers

git clone https://github.com/violatingcp/Jets_Short.git
cp -r Jets_Short/* .
rm -rf Jets_Short

git clone https://github.com/amarini/QuarkGluonTagger.git && cd QuarkGluonTagger && git checkout v1-2-6 && cd ..

cd ${CMSSW_BASE}


