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
options.parseArguments()

def getBaseConfig(
	nickname,
	testfile=False, # false if not given, string otherwise
	maxevents=-1,
	outputfilename = 'kappaTuple.root'):

	from Kappa.Skimming.KSkimming_template_cfg import process
	## ------------------------------------------------------------------------

	# count number of events before doing anything else
	process.p *= process.nEventsTotal
	process.p *= process.nNegEventsTotal

	muons = "slimmedMuons"
	electrons = "slimmedElectrons"

	# new tau id only available for 8_0_20 (I believe) and above
	if tools.is_above_cmssw_version([8,0,20]):
		taus = "NewTauIDsEmbedded"
	else:
		taus = "slimmedTaus"
	isSignal = datasetsHelper.isSignal(nickname)

	# produce selected collections and filter events with not even one Lepton
	if options.preselect and not isSignal:
		from Kappa.Skimming.KSkimming_preselection import do_preselection

		do_preselection(process)
		process.p *= process.goodEventFilter

		process.selectedKappaTaus.cut = cms.string('pt > 15 && abs(eta) < 2.5')
		process.selectedKappaMuons.cut = cms.string('pt > 8 && abs(eta) < 2.6')
		process.selectedKappaElectrons.cut = cms.string('pt > 8 && abs(eta) < 2.7')
		muons = "selectedKappaMuons"
		electrons = "selectedKappaElectrons"
		taus = "selectedKappaTaus"
		process.goodEventFilter.minNumber = cms.uint32(2)

	## ------------------------------------------------------------------------

	# possibility to write out edmDump. Be careful when using unsceduled mode
	process.load("Kappa.Skimming.edmOut")
	process.ep = cms.EndPath()
	#process.ep *= process.edmOut

	## ------------------------------------------------------------------------

	# Configure Kappa
	if testfile:
		process.source.fileNames      = cms.untracked.vstring("%s"%testfile)
	else:
		process.source 			  = cms.Source('PoolSource', fileNames=cms.untracked.vstring())
	process.maxEvents.input	      = maxevents
	process.kappaTuple.verbose    = cms.int32(0)
	# uncomment the following option to select only running on certain luminosity blocks. Use only for debugging
	# process.source.lumisToProcess  = cms.untracked.VLuminosityBlockRange("1:500-1:1000")
        # process.source.eventsToProcess  = cms.untracked.VEventRange("299368:56418140-299368:56418140")
	process.kappaTuple.profile    = cms.bool(True)


	globaltag = datasetsHelper.getGlobalTag(nickname)
	print "Global Tag:", globaltag
	process.GlobalTag.globaltag = globaltag

	## ------------------------------------------------------------------------

	# Configure Metadata describing the file
	# Important to be evaluated correctly for the following steps
	# data, isEmbedded, miniaod, process.kappaTuple.TreeInfo.parameters = datasetsHelper.getTreeInfo(nickname, globaltag, kappaTag)
	process.kappaTuple.active = cms.vstring('TreeInfo')

	data = datasetsHelper.isData(nickname)
	isEmbedded = datasetsHelper.isEmbedded(nickname)
	print "nickname:", nickname

	#####miniaod = datasetsHelper.isMiniaod(nickname) not used anymore, since everything is MiniAOD now
	process.kappaTuple.TreeInfo.parameters= datasetsHelper.getTreeInfo(nickname)

	## ------------------------------------------------------------------------

	# General configuration
	if tools.is_above_cmssw_version([7,4]) and not data and not isEmbedded:
		process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo","","PAT")
	if not tools.is_above_cmssw_version([9]):
            if isSignal:
		process.kappaTuple.Info.lheSource = cms.InputTag("source")
	if tools.is_above_cmssw_version([8]) and (not data or isEmbedded):
		process.kappaTuple.Info.htxsInfo = cms.InputTag("rivetProducerHTXS", "HiggsClassification")
		process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
		process.mergedGenParticles = cms.EDProducer("MergedGenParticleProducer",
			inputPruned = cms.InputTag("prunedGenParticles"),
			inputPacked = cms.InputTag("packedGenParticles"),
		)
		process.myGenerator = cms.EDProducer("GenParticles2HepMCConverter",
			genParticles = cms.InputTag("mergedGenParticles"),
			genEventInfo = cms.InputTag("generator"),
			signalParticlePdgIds = cms.vint32(25),
		)
		process.rivetProducerHTXS = cms.EDProducer('HTXSRivetProducer',
			HepMCCollection = cms.InputTag('myGenerator','unsmeared'),
			LHERunInfo = cms.InputTag('externalLHEProducer'),
			ProductionMode = cms.string('AUTO'),
		)
		process.p *= cms.Sequence(process.mergedGenParticles*process.myGenerator*process.rivetProducerHTXS)

	# save primary vertex
	process.kappaTuple.active += cms.vstring('VertexSummary') # save VertexSummary

	process.kappaTuple.VertexSummary.whitelist = cms.vstring('offlineSlimmedPrimaryVertices')  # save VertexSummary
	process.kappaTuple.VertexSummary.rename = cms.vstring('offlineSlimmedPrimaryVertices => goodOfflinePrimaryVerticesSummary')

	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(src=cms.InputTag("offlineSlimmedPrimaryVertices"))

	#process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')
	process.kappaTuple.active += cms.vstring('ReducedTriggerObject')
	if not isEmbedded:
		process.kappaTuple.ReducedTriggerObject.metfilterbits = cms.InputTag("TriggerResults", "", "PAT")
	else:
		process.kappaTuple.ReducedTriggerObject.bits = cms.InputTag("TriggerResults", "", "SIMembedding")
		process.kappaTuple.ReducedTriggerObject.metfilterbits = cms.InputTag("TriggerResults", "", "MERGE")

	# setup BadPFMuonFilter and BadChargedCandidateFilter
	if tools.is_above_cmssw_version([8]) and not tools.is_above_cmssw_version([9]):
		process.load('RecoMET.METFilters.BadPFMuonFilter_cfi')
		process.BadPFMuonFilter.muons = cms.InputTag("slimmedMuons")
		process.BadPFMuonFilter.PFCandidates = cms.InputTag("packedPFCandidates")
		process.BadPFMuonFilter.taggingMode = cms.bool(True)

		process.load('RecoMET.METFilters.BadChargedCandidateFilter_cfi')
		process.BadChargedCandidateFilter.muons = cms.InputTag("slimmedMuons")
		process.BadChargedCandidateFilter.PFCandidates = cms.InputTag("packedPFCandidates")
		process.BadChargedCandidateFilter.taggingMode = cms.bool(True)

		# in reMiniAOD data these filters are already present; only need to run the dedicated module for MC and older data
		if not "03Feb2017" in str(process.kappaTuple.TreeInfo.parameters.scenario):
			process.load('RecoMET.METFilters.badGlobalMuonTaggersMiniAOD_cff')
			#switch on tagging mode:
			process.badGlobalMuonTaggerMAOD.taggingMode = cms.bool(True)
			process.cloneGlobalMuonTaggerMAOD.taggingMode = cms.bool(True)
			process.kappaTuple.TriggerObjectStandalone.metfilterbitslist = cms.vstring("BadChargedCandidateFilter", "BadPFMuonFilter", "badGlobalMuonTaggerMAOD", "cloneGlobalMuonTaggerMAOD")
		else:
			process.kappaTuple.TriggerObjectStandalone.metfilterbitslist = cms.vstring("BadChargedCandidateFilter","BadPFMuonFilter")

	process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
	if isEmbedded:
		process.kappaTuple.TriggerObjectStandalone.bits = cms.InputTag("TriggerResults", "", "SIMembedding")
		process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "MERGE")
		process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "SIMembedding")
	elif data:
		if tools.is_above_cmssw_version([9]):
			process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")
                        process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO") # take last process used in production for data
		elif "03Feb2017" in str(process.kappaTuple.TreeInfo.parameters.scenario):
			process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "PAT")
		else:
			process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO")
			process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "RECO")
        else:
                process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "PAT") # take last process used in production for mc

	if not isEmbedded and "Spring16" in str(process.kappaTuple.TreeInfo.parameters.campaign):
		# adds for each HLT Trigger wich contains "Tau" or "tau" in the name a Filter object named "l1extratauccolltection"
		process.kappaTuple.TriggerObjectStandalone.l1extratauJetSource = cms.untracked.InputTag("l1extraParticles","IsoTau","RECO")

	if not tools.is_above_cmssw_version([9]):
		process.kappaTuple.TriggerObjectStandalone.triggerObjects = cms.PSet( src = cms.InputTag("selectedPatTrigger"))
		process.kappaTuple.TriggerObjectStandalone.bits = cms.InputTag("TriggerResults", "", "HLT")

	process.kappaTuple.active += cms.vstring('BeamSpot')
	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(src = cms.InputTag("offlineBeamSpot"))

	if not isEmbedded and data:
		process.kappaTuple.active+= cms.vstring('DataInfo')          # produce Metadata for data,

	if not isEmbedded and not data:
		process.kappaTuple.active+= cms.vstring('GenInfo')           # produce Metadata for MC,
		process.kappaTuple.active+= cms.vstring('GenParticles')      # save GenParticles,
		process.kappaTuple.active+= cms.vstring('GenTaus')           # save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
		process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")


	# write out for all processes where available
	process.kappaTuple.Info.lheWeightNames = cms.vstring(".*")

	# save Flag
	process.kappaTuple.Info.isEmbedded = cms.bool(isEmbedded)

	if isEmbedded:
		#process.load('RecoBTag/Configuration/RecoBTag_cff')
		#process.load('RecoJets/JetAssociationProducers/ak5JTA_cff')
		#process.ak5PFJetNewTracksAssociatorAtVertex.tracks = "tmfTracks"
		#process.ak5PFCHSNewJetTracksAssociatorAtVertex.tracks = "tmfTracks"
		#process.p *= process.btagging
		# disable overrideHLTCheck for embedded samples, since it triggers an Kappa error
		process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)
		process.kappaTuple.active += cms.vstring('GenInfo')
		process.kappaTuple.active += cms.vstring('GenParticles') # save GenParticles,
		process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")
		process.kappaTuple.active += cms.vstring('GenTaus')
		process.kappaTuple.GenTaus.genTaus.src = cms.InputTag("prunedGenParticles")

		#process.kappaTuple.active += cms.vstring('GenTaus') # save GenParticles,
		#process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("genParticles","","EmbeddedRECO")

	## ------------------------------------------------------------------------

	# Trigger
	from Kappa.Skimming.hlt_run2 import hltBlacklist, hltWhitelist
	process.kappaTuple.Info.hltWhitelist = hltWhitelist
	process.kappaTuple.Info.hltBlacklist = hltBlacklist

	## ------------------------------------------------------------------------

	# should not be the default, it blows up the skim a lot
	#process.kappaTuple.active += cms.vstring('packedPFCandidates')
	#process.kappaTuple.packedPFCandidates.packedPFCandidates = cms.PSet(src = cms.InputTag("packedPFCandidates"))

	jetCollectionPuppi = "slimmedJetsPuppi"
	if tools.is_above_cmssw_version([9]):
                from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
                updateJetCollection(
                       process,
                       jetSource = cms.InputTag('slimmedJets'),
                       labelName = 'UpdatedJEC',
                       jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute', 'L2L3Residual']), 'None'),
                       btagDiscriminators = [
                            "pfDeepFlavourJetTags:probb",
                            "pfDeepFlavourJetTags:probbb",
                            "pfDeepFlavourJetTags:problepb",
                       ],
                )
		jetCollection = "updatedPatJetsUpdatedJEC"
	elif tools.is_above_cmssw_version([8]):
		from RecoMET.METPUSubtraction.jet_recorrections import recorrectJets
		#from RecoMET.METPUSubtraction.jet_recorrections import loadLocalSqlite
		#loadLocalSqlite(process, sqliteFilename = "Spring16_25nsV6_DATA.db" if data else "Spring16_25nsV6_MC.db",
		#                         tag = 'JetCorrectorParametersCollection_Spring16_25nsV6_DATA_AK4PF' if data else 'JetCorrectorParametersCollection_Spring16_25nsV6_MC_AK4PF')
		recorrectJets(process, isData=data)
		jetCollection = "patJetsReapplyJEC"
	else:
		from RecoMET.METPUSubtraction.localSqlite import recorrectJets
		recorrectJets(process, isData=data)
		jetCollection = "patJetsReapplyJEC"

	## ------------------------------------------------------------------------

	# Configure Muons
	process.load("Kappa.Skimming.KMuons_miniAOD_cff")
	process.kappaTuple.Muons.muons.src = cms.InputTag(muons)
	process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Muons.use03ConeForPfIso = cms.bool(True)
	process.kappaTuple.Muons.doPfIsolation = cms.bool(False)
	for src in [ "muPFIsoDepositCharged", "muPFIsoDepositChargedAll", "muPFIsoDepositNeutral", "muPFIsoDepositGamma", "muPFIsoDepositPU"]:
		setattr(getattr(process, src), "src", cms.InputTag(muons))

	process.kappaTuple.active += cms.vstring('Muons')
	process.kappaTuple.Muons.noPropagation = cms.bool(True)
	process.p *= ( process.makeKappaMuons )

	## ------------------------------------------------------------------------

	# Configure Electrons

        # Apply scale & smear corrections of electrons & store them as user floats (default) and recompute the VID's (including V2)
        if tools.is_above_cmssw_version([9,4]):
            from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
            setupEgammaPostRecoSeq(
                    process,
                    runVID=True,
                    eleIDModules=[
                            'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff',

                            'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff',
                            'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff',
                            'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff',

                            'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
                            'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff',
                            'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
                    ],
                    era='2017-Nov17ReReco'
            )
            process.p *= process.egammaPostRecoSeq

	process.kappaTuple.active += cms.vstring('Electrons')
	process.load("Kappa.Skimming.KElectrons_miniAOD_cff")
	process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
	process.kappaTuple.Electrons.electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
	process.kappaTuple.Electrons.electrons.rhoIsoInputTag = cms.InputTag(jetCollection, "rho")
	process.kappaTuple.Electrons.electrons.allConversions = cms.InputTag("reducedEgamma", "reducedConversions")

        if tools.is_above_cmssw_version([9,4]):
                process.kappaTuple.Electrons.srcIds = cms.string("pat")
        else:
                process.kappaTuple.Electrons.srcIds = cms.string("standalone")

	if tools.is_above_cmssw_version([9,4]):
		process.kappaTuple.Electrons.ids = cms.VInputTag(
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-veto"),
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-loose"),
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-medium"),
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-tight"),

			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-veto"),
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-loose"),
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-medium"),
			cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-tight"),

			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wp90"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wp80"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V1-wpLoose"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wp90"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wp80"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V1-wpLoose"),

			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp90"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp80"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wpLoose"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp90"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp80"),
			cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wpLoose"),
			)
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

			cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV1Values"),
			cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17IsoV1Values"),
			cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV2Values"),
			cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17IsoV2Values"),
                        )
	elif tools.is_above_cmssw_version([8]):
		process.kappaTuple.Electrons.ids = cms.VInputTag(
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-veto",
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-loose",
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-medium",
			"egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-tight",
			"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring16GeneralPurposeV1Values"
			)
                process.kappaTuple.Electrons.userFloats = cms.VInputTag(
                        )
	else:
		process.kappaTuple.Electrons.ids = cms.VInputTag(
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-veto",
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-loose",
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-medium",
			"egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight",
			"electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring15NonTrig25nsV1Values"
			)
                process.kappaTuple.Electrons.userFloats = cms.VInputTag(
                        )

	if not tools.is_above_cmssw_version([9,4]):
                from Kappa.Skimming.KElectrons_miniAOD_cff import setupElectrons
                setupElectrons(process, electrons)
                process.p *= (process.makeKappaElectrons)

	## ------------------------------------------------------------------------

	# new tau id only available for 8_0_20 (I believe) and above
        from RecoTauTag.RecoTau.runTauIdMVA import TauIDEmbedder
	if tools.is_above_cmssw_version([9,4,2]):
                na = TauIDEmbedder(process, cms,
                    debug=True,
                    toKeep = ["2017v2","DPFTau_2016_v0","DPFTau_2016_v1","deepTau2017v1"]
                )
	elif tools.is_above_cmssw_version([8,0,20]):
                na = TauIDEmbedder(process, cms,
                    debug=True,
                    toKeep = ["2016v1"]
                )
        na.runTauID(taus)
        process.p *= ( process.rerunMvaIsolationSequence)
        process.p *= getattr(process, taus)

	process.kappaTuple.active += cms.vstring('PatTaus')
	process.kappaTuple.PatTaus.taus.binaryDiscrBlacklist = cms.vstring()
	process.kappaTuple.PatTaus.taus.src = cms.InputTag(taus)
	process.kappaTuple.PatTaus.taus.floatDiscrBlacklist = cms.vstring()

	# just took everything from https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendation13TeV with old DM's and deltaR = 0.5
	process.kappaTuple.PatTaus.taus.preselectOnDiscriminators = cms.vstring ()
	process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist = cms.vstring(
		"decayModeFinding",
		"decayModeFindingNewDMs",
		"byLooseCombinedIsolationDeltaBetaCorr3Hits",
		"byMediumCombinedIsolationDeltaBetaCorr3Hits",
		"byTightCombinedIsolationDeltaBetaCorr3Hits",
		"byCombinedIsolationDeltaBetaCorrRaw3Hits",
		"chargedIsoPtSum",
		"neutralIsoPtSum",
		"neutralIsoPtSumWeight",
		"puCorrPtSum",
		"footprintCorrection",
		"photonPtSumOutsideSignalCone",
		"byIsolationMVArun2v1DBoldDMwLTraw",
		"byVLooseIsolationMVArun2v1DBoldDMwLT",
		"byLooseIsolationMVArun2v1DBoldDMwLT",
		"byMediumIsolationMVArun2v1DBoldDMwLT",
		"byTightIsolationMVArun2v1DBoldDMwLT",
		"byVTightIsolationMVArun2v1DBoldDMwLT",
		"byVVTightIsolationMVArun2v1DBoldDMwLT",
		"againstMuonLoose3",
		"againstMuonTight3",
		"againstElectronMVA6category",
		"againstElectronMVA6raw",
		"againstElectronVLooseMVA6",
		"againstElectronLooseMVA6",
		"againstElectronMediumMVA6",
		"againstElectronTightMVA6",
		"againstElectronVTightMVA6",
		)

	process.kappaTuple.active += cms.vstring('L1Taus')
        if isEmbedded:
                process.kappaTuple.L1Taus.l1taus.src = cms.InputTag("caloStage2Digis","Tau","SIMembedding")

	if tools.is_above_cmssw_version([9,4,2]):
		process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist += cms.vstring(
                        # 2017v2
                        "byIsolationMVArun2017v2DBoldDMwLTraw2017",
                        "byVVLooseIsolationMVArun2017v2DBoldDMwLT2017",
                        "byVLooseIsolationMVArun2017v2DBoldDMwLT2017",
                        "byLooseIsolationMVArun2017v2DBoldDMwLT2017",
                        "byMediumIsolationMVArun2017v2DBoldDMwLT2017",
                        "byTightIsolationMVArun2017v2DBoldDMwLT2017",
                        "byVTightIsolationMVArun2017v2DBoldDMwLT2017",
                        "byVVTightIsolationMVArun2017v2DBoldDMwLT2017",
                        "deepTau2017v1tauVSall", # deep Tau based on same inputs as MVAIso (BDT-based)
                        "DPFTau_2016_v0tauVSall", # Deep PF Tau based also on low-level inputs (v0)
                        "DPFTau_2016_v1tauVSall", # Deep PF Tau based also on low-level inputs (v1)
			)
	elif tools.is_above_cmssw_version([8,0,20]):
		process.kappaTuple.PatTaus.taus.binaryDiscrWhitelist += cms.vstring(
                        # 2016v1
                        "byIsolationMVArun2016v1DBoldDMwLTraw2016",
                        "byVLooseIsolationMVArun2016v1DBoldDMwLT2016",
                        "byLooseIsolationMVArun2016v1DBoldDMwLT2016",
                        "byMediumIsolationMVArun2016v1DBoldDMwLT2016",
                        "byTightIsolationMVArun2016v1DBoldDMwLT2016",
                        "byVTightIsolationMVArun2016v1DBoldDMwLT2016",
                        "byVVTightIsolationMVArun2016v1DBoldDMwLT2016",
			)

	## now also possible to save all MVA isolation inputs for taus # turn of per default
	process.kappaTuple.PatTaus.taus.extrafloatDiscrlist = cms.untracked.vstring(
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
	process.kappaTuple.PatTaus.verbose = cms.int32(1)

	## ------------------------------------------------------------------------

	## Configure Jets
	process.kappaTuple.active += cms.vstring('PileupDensity')
	process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
	process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")
	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(src=cms.InputTag("fixedGridRhoFastjetAll"))
	process.kappaTuple.active += cms.vstring('PatJets')
	if tools.is_above_cmssw_version([7,6]):
		process.kappaTuple.PatJets.ak4PF = cms.PSet(src=cms.InputTag(jetCollection))
		process.kappaTuple.PatJets.puppiJets = cms.PSet(src=cms.InputTag(jetCollectionPuppi))
	if tools.is_above_cmssw_version([9]):
                process.jecSequence = cms.Sequence(process.patJetCorrFactorsUpdatedJEC * process.updatedPatJetsUpdatedJEC)
                process.p *= process.jecSequence

	## Standard MET and GenMet from pat::MET
	process.kappaTuple.active += cms.vstring('PatMET')
	process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETsModifiedMET"))
	if tools.is_above_cmssw_version([9]):
		from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
		runMetCorAndUncFromMiniAOD(
			process,
			isData=data,
			fixEE2017 = True,
			fixEE2017Params = {'userawPt': True, 'ptThreshold':50.0, 'minEtaThreshold':2.65, 'maxEtaThreshold': 3.139},
			postfix = "ModifiedMET"
		)
		process.p *= process.fullPatMetSequenceModifiedMET
	elif tools.is_above_cmssw_version([8,0,14]):
		from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
		runMetCorAndUncFromMiniAOD(process, isData=data  )
		process.kappaTuple.PatMET.met = cms.PSet(src=cms.InputTag("slimmedMETs", "", "KAPPA"))

#	if tools.is_above_cmssw_version([9]):
#                from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
#                makePuppiesFromMiniAOD(process, True)
#                runMetCorAndUncFromMiniAOD(
#                        process,
#                        isData=data,
#                        metType="Puppi",
#                        postfix="Puppi",
#                        jetFlavor="AK4PFPuppi",
#                )
#
#                process.puppiNoLep.useExistingWeights = False
#                process.puppi.useExistingWeights = False
#
#                #process.p *= process.egmPhotonIDSequence*process.puppiMETSequence*process.fullPatMetSequencePuppi
#                process.p *= process.fullPatMetSequencePuppi

	#process.kappaTuple.PatMET.pfmetT1 = cms.PSet(src=cms.InputTag("patpfMETT1"))
	process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"))

	if not tools.is_above_cmssw_version([9]):
		## Write MVA MET to KMETs
		process.kappaTuple.active += cms.vstring('PatMETs')
		# new MVA MET
		from RecoMET.METPUSubtraction.MVAMETConfiguration_cff import runMVAMET
		runMVAMET( process, jetCollectionPF = jetCollection)
		process.kappaTuple.PatMETs.MVAMET = cms.PSet(src=cms.InputTag("MVAMET", "MVAMET"))
		process.MVAMET.srcLeptons  = cms.VInputTag(muons, electrons, taus) # to produce all possible combinations
		process.MVAMET.requireOS = cms.bool(False)
		if tools.is_above_cmssw_version([8,0]) and isEmbedded:
			process.MVAMET.srcMETs = cms.VInputTag(
				cms.InputTag("slimmedMETs", "", "MERGE"),
				cms.InputTag("patpfTrackMET"),
				cms.InputTag("patpfNoPUMET"),
				cms.InputTag("patpfPUCorrectedMET"),
				cms.InputTag("patpfPUMET"),
				cms.InputTag("slimmedMETsPuppi", "", "MERGE")
				)

	## ------------------------------------------------------------------------

	## GenJets
	if not data or isEmbedded:
		process.load('PhysicsTools/JetMCAlgos/TauGenJets_cfi')
		process.load('PhysicsTools/JetMCAlgos/TauGenJetsDecayModeSelectorAllHadrons_cfi')
		process.tauGenJets.GenParticles = cms.InputTag("prunedGenParticles")
		process.p *= (
			process.tauGenJets +
			process.tauGenJetsSelectorAllHadrons
			)
		if isSignal:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets", "slimmedGenJets")
		else:
			process.kappaTuple.GenJets.whitelist = cms.vstring("tauGenJets")
		process.kappaTuple.active += cms.vstring('GenJets')
		if tools.is_above_cmssw_version([7,6]):
			if isSignal:
				process.kappaTuple.GenJets.genJets = cms.PSet(src=cms.InputTag("slimmedGenJets"))
			process.kappaTuple.GenJets.tauGenJets = cms.PSet(src=cms.InputTag("tauGenJets"))
			process.kappaTuple.GenJets.tauGenJetsSelectorAllHadrons = cms.PSet(src=cms.InputTag("tauGenJetsSelectorAllHadrons"))

	# add repository revisions to TreeInfo
	for repo, rev in tools.get_repository_revisions().iteritems():
		setattr(process.kappaTuple.TreeInfo.parameters, repo, cms.string(rev))

	## ------------------------------------------------------------------------

	## Count Events after running all filters
	if not data:
		process.nEventsTotal.isMC = cms.bool(True)
		process.nNegEventsTotal.isMC = cms.bool(True)
		process.nEventsFiltered.isMC = cms.bool(True)
		process.nNegEventsFiltered.isMC = cms.bool(True)

	process.p *= process.nEventsFiltered
	process.p *= process.nNegEventsFiltered
	process.kappaTuple.active += cms.vstring('FilterSummary')

	## ------------------------------------------------------------------------

	## if needed adapt output filename
	process.ep *= process.kappaOut
	if outputfilename != '':
		process.kappaTuple.outputFile = cms.string('%s'%outputfilename)

	## ------------------------------------------------------------------------

	## Further information saved to Kappa output
	if options.dumpPython:
		f = open("dumpPython.py", "w")
		f.write(process.dumpPython())
		f.close()

	# add python config to TreeInfo
	process.kappaTuple.TreeInfo.parameters.config = cms.string(process.dumpPython())

	return process

if __name__ == "__main__" or __name__ == "kSkimming_run2_cfg":

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

	# GC job-submission?
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
