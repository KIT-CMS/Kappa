source /cvmfs/cms.cern.ch/cmsset_default.sh

scramv1 project CMSSW_10_2_16_patch1
cd CMSSW_10_2_16_patch1/src/

eval `scramv1 runtime -sh`
git cms-merge-topic -u cms-tau-pog:CMSSW_10_2_X_tau-pog_DeepTau2017v2
git cms-merge-topic -u cms-tau-pog:CMSSW_10_2_X_tau-pog_deepTauVetoPCA

git clone --recursive git@github.com:KIT-CMS/Kappa.git -b nanoAOD
git clone git@github.com:KIT-CMS/grid-control
git clone git@github.com:janekbechtel/grid-control jb_grid-control


scram b -j 12
