#-# Copyright (c) 2014 - All Rights Reserved
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Fabio Colombo <fabio.colombo@cern.ch>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Raphael Friese <Raphael.Friese@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>
#-#   Stefan Wayand <stefan.wayand@gmail.com>
#-#   Thomas Mueller <tmuller@cern.ch>
#-#   Yasmin Anstruther <yasmin.anstruther@kit.edu>

## ------------------------------------------------------------------------
# Central cmsRun config file to be used with grid-control
# Settings are stored ordered on physics objects
# Object-related settings should be done in designated python configs
# if possible, run2 configs import the run1 configs and add some extra information
## ------------------------------------------------------------------------

# Kappa test: CMSSW 7.6.3, 8.0.20
# Kappa test: scram arch slc6_amd64_gcc493, slc6_amd64_gcc530
# Kappa test: checkout script scripts/checkoutCmssw76xPackagesForSkimming.py, scripts/checkoutCmssw80xPackagesForSkimming.py
# Kappa test: output kappaTuple.root
import sys
if not hasattr(sys, 'argv'):
	sys.argv = ["cmsRun", "runFrameworkMC.py"]

import os
import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
datasetsHelper = datasetsHelperTwopz(os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets.json"))
import Kappa.Skimming.tools as tools

from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('python')
options.register('nickname', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Dataset Nickname')
options.register('testfile', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Path for a testfile. If no test file is given, nickname is used to get a test file with xrootd.')
options.register('maxevents', -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'maxevents. -1 for all events. Default: -1')
options.register('outputfilename', 'kappaTuple.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Filename for the Outputfile')
options.register('mode', 'testsuite', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Mode to run. Options: ["testuite" (Default), "local", "crab"]. Grid-Control is automatically determined.')
options.register('preselect', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'apply preselection at CMSSW level on leptons. Never preselect on SM Higgs samples')
options.register('dumpPython', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'write cmsRun config to dumpPython.py')
options.register('inspectprocess', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'print the content of proces')
options.register('verbose', 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'varbosity of kappaTuple. Default: 0')
options.register('reportEvery', -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'MessageLogger report rate. Default: -1')
options.register('usePostMiniAODSequences', False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, 'use sequences to be rerun on MiniAOD')
options.parseArguments()

def getBaseConfig(
	nickname,
	testfile=False, # false if not given, string otherwise
	maxevents=-1,
	outputfilename = 'kappaTuple.root'):

        metfilterbits_process_data = {
            2016 : "DQM",
            2017 : "PAT",
            2018 : "RECO",
        }

        pfmet = {
            2016 : "slimmedMETs",
            2017 : "slimmedMETsModifiedMET",
            2018 : "slimmedMETs",
        }

        
        # CMSSW version
        cmssw_version_number = tools.get_cmssw_version_number()

        # Nickname specific options
	print "nickname:", nickname
	isSignal = datasetsHelper.isSignal(nickname)
	isEmbedded = datasetsHelper.isEmbedded(nickname)
	isData = datasetsHelper.isData(nickname) and not isEmbedded
        isMC = not isData and not isEmbedded
        year = datasetsHelper.base_dict[nickname]["year"]
        dtype = ""
        if isData:
            dtype = "data"
        elif isEmbedded:
            dtype = "embedding"
        elif isMC:
            dtype = "MC"
        postMiniAODProcess = "SKIM"

        from Kappa.Skimming.postMiniAODSequences import create_postMiniAODSequences
        process = create_postMiniAODSequences(year, dtype)
        process.ep = cms.EndPath()
        if not options.usePostMiniAODSequences:
            process.p = cms.Path()
            process._Process__name = "KAPPA"

        ## Global Tag
	globaltag = datasetsHelper.getGlobalTag(nickname)
	process.GlobalTag.globaltag = globaltag
	print "Global Tag:", globaltag

        ## MessageLogger
        process.MessageLogger.default = cms.untracked.PSet(
                ERROR = cms.untracked.PSet(limit = cms.untracked.int32(5))
        )

	if options.reportEvery >= 0 :
		process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery

        ## Options and Output Report
        process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) ,
                allowUnscheduled = cms.untracked.bool(False) )

        ## Kappa
        from Kappa.Producers.KTuple_cff import kappaTupleDefaultsBlock
        process.kappaTuple = cms.EDAnalyzer('KTuple',
            kappaTupleDefaultsBlock,
            outputFile = cms.string("kappaTuple.root"),
        )
        process.kappaTuple.active = cms.vstring()
        process.kappaOut = cms.Sequence(process.kappaTuple)
	process.ep *= process.kappaOut
	#process.load("Kappa.Skimming.edmOut") # possibility to write out edmDump. Be careful when using unscheduled mode
	#process.ep *= process.edmOut

	## ------------------------------------------------------------------------

	# Configure Kappa
	if testfile:
		process.source.fileNames      = cms.untracked.vstring("%s"%testfile)
	else:
		process.source 			  = cms.Source('PoolSource', fileNames=cms.untracked.vstring())

	process.maxEvents.input	      = maxevents
	process.kappaTuple.verbose    = cms.int32(options.verbose)
	process.kappaTuple.profile    = cms.bool(True)

	# uncomment the following option to select only running on certain luminosity blocks. Use only for debugging
	# process.source.lumisToProcess  = cms.untracked.VLuminosityBlockRange("1:500-1:1000")
        # process.source.eventsToProcess  = cms.untracked.VEventRange("299368:56418140-299368:56418140")

	## ------------------------------------------------------------------------

	# Configure metadata describing the file
	process.kappaTuple.active = cms.vstring('TreeInfo')
	process.kappaTuple.TreeInfo.parameters= datasetsHelper.getTreeInfo(nickname)
	for repo, rev in tools.get_repository_revisions().iteritems(): # add repository revisions to TreeInfo
		setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))

	## ------------------------------------------------------------------------

        # General info (All: HLT paths, MC: PU Source, HTXS, LHE weights)
	if isData:
		process.kappaTuple.active+= cms.vstring('DataInfo')
                process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
	elif isMC:
		process.kappaTuple.active+= cms.vstring('GenInfo')           # produce Metadata for MC
		process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")
		process.kappaTuple.Info.htxsInfo = cms.InputTag("rivetProducerHTXS", "HiggsClassification",  postMiniAODProcess)
                process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
        elif isEmbedded:
		process.kappaTuple.active += cms.vstring('GenInfo')          # produce Metatada for embedding
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.Info.htxsInfo = cms.InputTag("rivetProducerHTXS", "HiggsClassification",  postMiniAODProcess)
		process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "SIMembedding")

	process.kappaTuple.Info.lheWeightNames = cms.vstring(".*") # write out for all processes where available
	process.kappaTuple.Info.isEmbedded = cms.bool(isEmbedded) # save Flag
	from Kappa.Skimming.hlt_run2 import hltBlacklist, hltWhitelist # Trigger
	process.kappaTuple.Info.hltWhitelist = hltWhitelist 
	process.kappaTuple.Info.hltBlacklist = hltBlacklist

	# Primary vertex
	process.kappaTuple.active += cms.vstring('VertexSummary') # save VertexSummary
	process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary
	process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')
        process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlineSlimmedPrimaryVertices"))

	## ------------------------------------------------------------------------

        # Trigger object information
	process.kappaTuple.active += cms.vstring('ReducedTriggerObject')
	if isData or isMC:
		process.kappaTuple.ReducedTriggerObject.bits = cms.InputTag("TriggerResults", "", "HLT")
        elif isEmbedded:
		process.kappaTuple.ReducedTriggerObject.bits = cms.InputTag("TriggerResults", "", "SIMembedding")
		process.kappaTuple.ReducedTriggerObject.triggerObjects = cms.PSet(src=cms.InputTag("slimmedPatTrigger"))

	## ------------------------------------------------------------------------

        # MET filters
        if isData:
		process.kappaTuple.ReducedTriggerObject.metfilterbits = cms.InputTag("TriggerResults", "", metfilterbits_process_data[year])
        elif isMC:
		process.kappaTuple.ReducedTriggerObject.metfilterbits = cms.InputTag("TriggerResults", "", "PAT")
	elif isEmbedded:
		process.kappaTuple.ReducedTriggerObject.metfilterbits = cms.InputTag("TriggerResults", "", "MERGE")
        process.kappaTuple.ReducedTriggerObject.rerunecalBadCalibFilter = cms.InputTag("ecalBadCalibReducedMINIAODFilter")

	## ------------------------------------------------------------------------

        # Beamspot
	process.kappaTuple.active += cms.vstring('BeamSpot')
        process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(src = cms.InputTag("offlineBeamSpot"))

	## ------------------------------------------------------------------------

        # Generated particles
        if isMC or isEmbedded:
		process.kappaTuple.active+= cms.vstring('GenParticles')
		process.kappaTuple.active+= cms.vstring('GenTaus')
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
		process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")

	## ------------------------------------------------------------------------

	# Muons
	process.kappaTuple.active += cms.vstring('Muons')
	process.kappaTuple.Muons.muons.src = cms.InputTag("slimmedMuons")
	process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Muons.use03ConeForPfIso = cms.bool(True)
	process.kappaTuple.Muons.doPfIsolation = cms.bool(False)
	process.kappaTuple.Muons.noPropagation = cms.bool(True)

	## ------------------------------------------------------------------------

	# Electrons
	process.kappaTuple.active += cms.vstring('Electrons')
	process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
	process.kappaTuple.Electrons.electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Electrons.electrons.rhoIsoInputTag = cms.InputTag("selectedUpdatedPatJetsUpdatedJEC", "rho", postMiniAODProcess)
	process.kappaTuple.Electrons.allConversions = cms.InputTag("reducedEgamma","reducedConversions")
        process.kappaTuple.Electrons.srcIds = cms.string("pat")
        process.kappaTuple.Electrons.ids = cms.VInputTag(
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Spring16-GeneralPurpose-V1-wp80"),
		cms.InputTag("egmGsfElectronIDs:mvaEleID-Spring16-GeneralPurpose-V1-wp90"),

                cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-veto"),
                cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-loose"),
                cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-medium"),
                cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-tight"),

                cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp90"),
                cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp80"),
                cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wpLoose"),
                cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp90"),
                cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp80"),
                cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wpLoose"),
                )
        # According to this: https://twiki.cern.ch/twiki/bin/view/CMS/EgammaPostRecoRecipes#A_note_on_ValueMaps
        process.kappaTuple.Electrons.userFloats = cms.VInputTag(
        # scale & smear corrected energy (applied on Data AND MC)
        cms.InputTag("electronCorrection:ecalTrkEnergyPreCorr"),
        cms.InputTag("electronCorrection:ecalTrkEnergyPostCorr"),
        cms.InputTag("electronCorrection:ecalTrkEnergyErrPreCorr"),
        cms.InputTag("electronCorrection:ecalTrkEnergyErrPostCorr"),

        # systematic variations for scale & smear corrections (to be used on MC)
        cms.InputTag("electronCorrection:energyScaleUp"),
        cms.InputTag("electronCorrection:energyScaleDown"),
        cms.InputTag("electronCorrection:energyScaleStatUp"),
        cms.InputTag("electronCorrection:energyScaleStatDown"),
        cms.InputTag("electronCorrection:energyScaleSystUp"),
        cms.InputTag("electronCorrection:energyScaleSystDown"),
        cms.InputTag("electronCorrection:energyScaleGainUp"),
        cms.InputTag("electronCorrection:energyScaleGainDown"),
        cms.InputTag("electronCorrection:energySigmaUp"),
        cms.InputTag("electronCorrection:energySigmaDown"),
        cms.InputTag("electronCorrection:energySigmaPhiUp"),
        cms.InputTag("electronCorrection:energySigmaPhiDown"),
        cms.InputTag("electronCorrection:energySigmaRhoUp"),
        cms.InputTag("electronCorrection:energySigmaRhoDown"),

        cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV2Values"),
        cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17IsoV2Values"),
        )

	## ------------------------------------------------------------------------

        # Taus
	process.kappaTuple.active += cms.vstring('PatTaus')
	process.kappaTuple.PatTaus.taus.binaryDiscrBlacklist = cms.vstring()
	process.kappaTuple.PatTaus.taus.src = cms.InputTag("slimmedTausNewID")
	process.kappaTuple.PatTaus.taus.floatDiscrBlacklist = cms.vstring()
	process.kappaTuple.PatTaus.taus.preselectOnDiscriminators = cms.vstring ()
	process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist = cms.vstring(
                # DM finding
		"decayModeFinding",
		"decayModeFindingNewDMs",

                # cut-based iso
		"byLooseCombinedIsolationDeltaBetaCorr3Hits",
		"byMediumCombinedIsolationDeltaBetaCorr3Hits",
		"byTightCombinedIsolationDeltaBetaCorr3Hits",
		"byCombinedIsolationDeltaBetaCorrRaw3Hits",

                # Tau MVA ID inputs
		"chargedIsoPtSum",
		"neutralIsoPtSum",
		"neutralIsoPtSumWeight",
		"puCorrPtSum",
		"footprintCorrection",
		"photonPtSumOutsideSignalCone",

                # standard anti-mu
		"againstMuonLoose3",
		"againstMuonTight3",

                # standard anti-e
		"againstElectronMVA6category",
		"againstElectronMVA6Raw",
		"againstElectronVLooseMVA6",
		"againstElectronLooseMVA6",
		"againstElectronMediumMVA6",
		"againstElectronTightMVA6",
		"againstElectronVTightMVA6",
		
		# old 2015
		"byIsolationMVArun2v1DBoldDMwLTraw",
		"byVLooseIsolationMVArun2v1DBoldDMwLT",
		"byLooseIsolationMVArun2v1DBoldDMwLT",
		"byMediumIsolationMVArun2v1DBoldDMwLT",
		"byTightIsolationMVArun2v1DBoldDMwLT",
		"byVTightIsolationMVArun2v1DBoldDMwLT",
		"byVVTightIsolationMVArun2v1DBoldDMwLT", 

                # 2017v2
                "byIsolationMVArun2017v2DBoldDMwLTraw2017",
                "byVVLooseIsolationMVArun2017v2DBoldDMwLT2017",
                "byVLooseIsolationMVArun2017v2DBoldDMwLT2017",
                "byLooseIsolationMVArun2017v2DBoldDMwLT2017",
                "byMediumIsolationMVArun2017v2DBoldDMwLT2017",
                "byTightIsolationMVArun2017v2DBoldDMwLT2017",
                "byVTightIsolationMVArun2017v2DBoldDMwLT2017",
                "byVVTightIsolationMVArun2017v2DBoldDMwLT2017",

                # deepTau
                "byDeepTau2017v1VSjetraw",
                "byDeepTau2017v1VSeraw",
                "byDeepTau2017v1VSmuraw",

                "byVVTightDeepTau2017v1VSjet",
                "byVTightDeepTau2017v1VSjet",
                "byTightDeepTau2017v1VSjet",
                "byMediumDeepTau2017v1VSjet",
                "byLooseDeepTau2017v1VSjet",
                "byVLooseDeepTau2017v1VSjet",
                "byVVLooseDeepTau2017v1VSjet",

                "byVVTightDeepTau2017v1VSe",
                "byVTightDeepTau2017v1VSe",
                "byTightDeepTau2017v1VSe",
                "byMediumDeepTau2017v1VSe",
                "byLooseDeepTau2017v1VSe",
                "byVLooseDeepTau2017v1VSe",
                "byVVLooseDeepTau2017v1VSe",

                "byVVTightDeepTau2017v1VSmu",
                "byVTightDeepTau2017v1VSmu",
                "byTightDeepTau2017v1VSmu",
                "byMediumDeepTau2017v1VSmu",
                "byLooseDeepTau2017v1VSmu",
                "byVLooseDeepTau2017v1VSmu",
                "byVVLooseDeepTau2017v1VSmu",

                # DPFTau
                "byDpfTau2016v0VSallraw",
                "byTightDpfTau2016v0VSall",
                "byDpfTau2016v1VSallraw",
                "byTightDpfTau2016v1VSall",

                # new anti-e training
                "againstElectronMVA6category2018",
                "againstElectronMVA6Raw2018",
                "againstElectronVLooseMVA62018",
                "againstElectronLooseMVA62018",
                "againstElectronMediumMVA62018",
                "againstElectronTightMVA62018",
                "againstElectronVTightMVA62018",
                )
	process.kappaTuple.PatTaus.taus.extrafloatDiscrlist = cms.untracked.vstring( # now also possible to save all MVA isolation inputs for taus # turn of per default
		"decayDistX",
		"decayDistY",
		"decayDistZ",
		"decayDistM",
		"nPhoton",
		"ptWeightedDetaStrip",
		"ptWeightedDphiStrip",
		"ptWeightedDrSignal",
		"ptWeightedDrIsolation",
		"leadingTrackChi2",
		"eRatio"
		)
	process.kappaTuple.PatTaus.taus.floatDiscrWhitelist = process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist
	process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist = cms.vstring("DontUseBinary")
	process.kappaTuple.PatTaus.verbose = cms.int32(1)

	## ------------------------------------------------------------------------

        # L1 taus
	process.kappaTuple.active += cms.vstring('L1Taus')
        if isEmbedded:
                process.kappaTuple.L1Taus.l1taus.src = cms.InputTag("caloStage2Digis","Tau","SIMembedding")

	## ------------------------------------------------------------------------

	## MET
	from Kappa.Producers.prepareMETDefinitions_cff import prepareMETs # Preparations for MVA MET
	prepareMETs(process,"selectedUpdatedPatJetsUpdatedJEC")
        process.neutralInJets.jetPUDIWP = cms.string("medium")
        process.neutralInJets.jetPUIDMapLabel = cms.string("pileupJetIdUpdated:fullId")
	process.p *= cms.Sequence(process.pfNeutrals*process.pfChargedPV*process.neutralInJets*process.pfChargedPU)
	process.p *= cms.Sequence(process.pfTrackMETCands*process.pfTrackMET*process.patpfTrackMET*process.pfNoPUMETCands*process.pfNoPUMET*process.patpfNoPUMET*process.pfPUCorrectedMETCands*process.pfPUCorrectedMET*process.patpfPUCorrectedMET*process.pfPUMETCands*process.pfPUMET*process.patpfPUMET)

	process.kappaTuple.active += cms.vstring('PatMET')
	process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag(pfmet[year]))
	process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"))
	process.kappaTuple.PatMET.trackMet = cms.PSet(src=cms.InputTag("patpfTrackMET"))
	process.kappaTuple.PatMET.noPuMet = cms.PSet(src=cms.InputTag("patpfNoPUMET"))
	process.kappaTuple.PatMET.puCorMet = cms.PSet(src=cms.InputTag("patpfPUCorrectedMET"))
	process.kappaTuple.PatMET.puMet = cms.PSet(src=cms.InputTag("patpfPUMET"))

	## ------------------------------------------------------------------------

	## Pileup Density
	process.kappaTuple.active += cms.vstring('PileupDensity')
	process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
	process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")
        process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))

	## ------------------------------------------------------------------------

	## Jets
	process.kappaTuple.active += cms.vstring('PatJets')
        process.kappaTuple.PatJets.ak4PF = cms.PSet(src=cms.InputTag("selectedUpdatedPatJetsUpdatedJEC"))
        process.kappaTuple.PatJets.puppiJets = cms.PSet(src=cms.InputTag("slimmedJetsPuppi"))

	## ------------------------------------------------------------------------

	## GenJets
	if isMC or isEmbedded:
		process.kappaTuple.active += cms.vstring('GenJets')
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
		process.p *= (
			process.tauGenJets +
			process.tauGenJetsSelectorAllHadrons
			)
		if isSignal:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets", "slimmedGenJets")
                        process.kappaTuple.GenJets.genJets = cms.PSet(src=cms.InputTag("slimmedGenJets"))
		else:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
                process.kappaTuple.GenJets.tauGenJets = cms.PSet(src=cms.InputTag("tauGenJets"))
                process.kappaTuple.GenJets.tauGenJetsSelectorAllHadrons = cms.PSet(src=cms.InputTag("tauGenJetsSelectorAllHadrons"))


	## ------------------------------------------------------------------------

        # Event counting
	process.kappaTuple.active += cms.vstring('FilterSummary')
        process.load("Kappa.Producers.EventWeightCountProducer_cff")
	process.p.insert(0,process.nEventsTotal) # count number of events before doing anything else
	process.p.insert(1,process.nNegEventsTotal)

	if not isData and not isEmbedded:
		process.nEventsTotal.isMC = cms.bool(True)
		process.nNegEventsTotal.isMC = cms.bool(True)
		process.nEventsFiltered.isMC = cms.bool(True)
		process.nNegEventsFiltered.isMC = cms.bool(True)

	process.p.insert(-1,process.nEventsFiltered) # count Events after running all filters
	process.p.insert(-1,process.nNegEventsFiltered)

	## ------------------------------------------------------------------------

	# if needed adapt output filename
	if outputfilename != '':
		process.kappaTuple.outputFile = cms.string('%s'%outputfilename)

	## ------------------------------------------------------------------------

	# Further information saved to Kappa output
	if options.dumpPython:
		f = open("dumpPython.py", "w")
		f.write(process.dumpPython())
		f.close()

	if options.inspectprocess:
		import pprint
		pp = pprint.PrettyPrinter(indent=4)
		pp.pprint(process.__dict__)

	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2_cfg_KappaOnly":

	# local testing with user-defined input file
	if options.mode == "local":
		if options.testfile == '': # get testfile from DBS
			testfile = datasetsHelper.get_testfile_for_nick(options.nickname)
		else:
			testfile = options.testfile
		print 'read from testfile '+str(testfile)
		process = getBaseConfig(
			nickname=options.nickname,
			testfile=testfile,
			outputfilename=options.outputfilename,
			maxevents=options.maxevents
			)

	# CRAB job-submission
	elif options.mode == "crab":
		process = getBaseConfig(
			nickname=options.nickname,
			outputfilename=options.outputfilename
			)

	# GC job-submission
	elif str("@NICK@")[0] != '@':
			process = getBaseConfig(
				nickname="@NICK@",
				outputfilename="kappaTuple.root"
				)

	# Kappa test suite (cmsRun with NO extra options, i.e. testsuite mode)
	# to create new testfiles edit make_testfile.py and run it with cmsRun
	elif options.mode == "testsuite":
		cernbox_path = "https://cernbox.cern.ch/index.php/s/AqIrGNDGdygdvhU/download?path=%2Fnew&files=" # path to "new" folder within Olena's CernBox

		if tools.is_cmssw_version([9,2]):
			test_nick = "SingleElectron_Run2017B_23Jun2017v1_13TeV_MINIAOD"
		elif tools.is_cmssw_version([8,0]):
			test_nick='SUSYGluGluToHToTauTauM160_RunIISpring16MiniAODv1_PUSpring16_13TeV_MINIAOD_pythia8'
		elif tools.is_cmssw_version([7,6]):
			test_nick='SUSYGluGluToHToTauTauM160_RunIIFall15MiniAODv2_PU25nsData2015v1_13TeV_MINIAOD_pythia8'
		else:
			print "There is not yet a valid CMSSW test available for this CMSSW release. Please edit kSkimming_run2_cfg.py correspondingly."
			sys.exit(1)
		testfile=tools.download_rootfile(cernbox_path, test_nick)
		process = getBaseConfig(
			testfile=testfile,
			nickname=test_nick,
			maxevents=100
			)
	else:
		print "Invalid mode selected: " + options.mode
		sys.exit(1)
