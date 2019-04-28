#!/bin/bash
### Main script to test current setup of Kappa for Run II legacy datsets. Please setup first the aproppriate CMSSW & Kappa environments and a valid VOMS proxy.

# Step 1: produce MiniAOD outputs with applied post-MiniAOD sequences one defined MiniAOD test-files
bash $CMSSW_BASE/src/Kappa/Skimming/test/testpostminiaod.sh

# Step 2: run Kappa on these MiniAOD outputs
bash $CMSSW_BASE/src/Kappa/Skimming/test/testkappa.sh

# Step 3: compare resulting Kappa outputs with available NanoAOD campaigns run with the same global tag.

# (i) Download matching NanoAOD files (currently only 2016 & 2017 VBF sample available in recent NanoAOD campaigns):
xrdcp root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAODv4/VBFHToTauTau_M125_13TeV_powheg_pythia8/NANOAODSIM/PUMoriond17_Nano14Dec2018_102X_mcRun2_asymptotic_v6-v1/250000/59970AAE-5645-6943-9E01-110254CF26F9.root VBFHToTauTau_M125_13TeV_powheg_pythia8_RunIISummer16NanoAODv4.root # 2016 MC NanoAOD
xrdcp root://xrootd-cms.infn.it//store/mc/RunIIFall17NanoAODv4/VBFHToTauTau_M125_13TeV_powheg_pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/280000/BE095941-90FD-B84F-9610-D5FD2E54ADC9.root VBFHToTauTau_M125_13TeV_powheg_pythia8_RunIIFall17NanoAODv4.root # 2017 MC NanoAOD

# (ii) Run comparison script for NanoAOD vs. Kappa
python $CMSSW_BASE/src/Kappa/Skimming/scripts/compare_nano_vs_kappa.py --nanofile VBFHToTauTau_M125_13TeV_powheg_pythia8_RunIISummer16NanoAODv4.root --kappafile kappaTuple_2016_MC.root --events `cat Kappa/Skimming/test/2016_MC_events.txt` --object Tau --year 2016 > comparison_2016_MC.txt # 2016 MC comparison
python $CMSSW_BASE/src/Kappa/Skimming/scripts/compare_nano_vs_kappa.py --nanofile VBFHToTauTau_M125_13TeV_powheg_pythia8_RunIIFall17NanoAODv4.root --kappafile kappaTuple_2017_MC.root --events `cat Kappa/Skimming/test/2017_MC_events.txt` --object Tau --year 2017 > comparison_2017_MC.txt # 2017 MC comparison
