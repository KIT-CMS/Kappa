#-# Copyright (c) 2014 - All Rights Reserved
#-#   Bastian Kargoll <bastian.kargoll@cern.ch>
#-#   Benjamin Treiber <benjamin.treiber@gmail.com>
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms

## ------------------------------------------------------------------------
##  rerun tau reconstruction sequence following POG recommendation:
##  https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#Rerunning_of_the_tau_ID_on_MiniA


## since we run in the unscheduled mode the normal import fails. Maybe a customizer would also be helpfull.

from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants
from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1raw as rerunDiscriminationByIsolationMVAOldDMrun2v1raw
from RecoTauTag.RecoTau.PATTauDiscriminationByMVAIsolationRun2_cff import patDiscriminationByIsolationMVArun2v1VLoose as rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose

# Summer 2016 training ids for oldDMs
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.PATTauProducer = cms.InputTag('slimmedTaus')
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.Prediscriminants = noPrediscriminants
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.loadMVAfromDB = cms.bool(True)
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1")
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.mvaOpt = cms.string("DBoldDMwLT")
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.requireDecayMode = cms.bool(True)
rerunDiscriminationByIsolationMVAOldDMrun2v1raw.verbosity = cms.int32(0)

rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.PATTauProducer = cms.InputTag('slimmedTaus')
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.Prediscriminants = noPrediscriminants
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw')
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.key = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw:category')
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.loadMVAfromDB = cms.bool(True)
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.mvaOutput_normalization = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_mvaOutput_normalization")
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.mapping = cms.VPSet(
		cms.PSet(
			category = cms.uint32(0),
			cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff90"),
			variable = cms.string("pt"),
		)
	)

rerunDiscriminationByIsolationMVAOldDMrun2v1Loose = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff80")
rerunDiscriminationByIsolationMVAOldDMrun2v1Medium = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff70")
rerunDiscriminationByIsolationMVAOldDMrun2v1Tight = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff60")
rerunDiscriminationByIsolationMVAOldDMrun2v1VTight = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff50")
rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2016v1_WPEff40")

# Summer 2016 training ids for newDMs
rerunDiscriminationByIsolationMVANewDMrun2v1raw = rerunDiscriminationByIsolationMVAOldDMrun2v1raw.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1raw.mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1")
rerunDiscriminationByIsolationMVANewDMrun2v1raw.mvaOpt = cms.string("DBnewDMwLT")

rerunDiscriminationByIsolationMVANewDMrun2v1VLoose = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1raw')
rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.key = cms.InputTag('rerunDiscriminationByIsolationMVANewDMrun2v1raw:category')
rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.mvaOutput_normalization = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_mvaOutput_normalization")
rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff90")

rerunDiscriminationByIsolationMVANewDMrun2v1Loose = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1Loose.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff80")
rerunDiscriminationByIsolationMVANewDMrun2v1Medium = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1Medium.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff70")
rerunDiscriminationByIsolationMVANewDMrun2v1Tight = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1Tight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff60")
rerunDiscriminationByIsolationMVANewDMrun2v1VTight = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1VTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff50")
rerunDiscriminationByIsolationMVANewDMrun2v1VVTight = rerunDiscriminationByIsolationMVANewDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVANewDMrun2v1VVTight.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBnewDMwLT2016v1_WPEff40")

# Summer 2017 training ids for oldDMs
rerunDiscriminationByIsolationMVAOldDMrun2v1raw2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1raw.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1raw2017.mvaName = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1")
rerunDiscriminationByIsolationMVAOldDMrun2v1raw2017.mvaOpt = cms.string("DBoldDMwLTwGJ")

rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.toMultiplex = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw2017')
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.key = cms.InputTag('rerunDiscriminationByIsolationMVAOldDMrun2v1raw2017:category')
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.mvaOutput_normalization = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_mvaOutput_normalization")
rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff90")

rerunDiscriminationByIsolationMVAOldDMrun2v1VVLoose2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1VVLoose2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff95")
rerunDiscriminationByIsolationMVAOldDMrun2v1Loose2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1Loose2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff80")
rerunDiscriminationByIsolationMVAOldDMrun2v1Medium2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1Medium2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff70")
rerunDiscriminationByIsolationMVAOldDMrun2v1Tight2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1Tight2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff60")
rerunDiscriminationByIsolationMVAOldDMrun2v1VTight2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1VTight2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff50")
rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight2017 = rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017.clone()
rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight2017.mapping[0].cut = cms.string("RecoTauTag_tauIdMVAIsoDBoldDMwLT2017v1_WPEff40")

## ------------------------------------------------------------------------
## Definition of sequences

## run this to get latest greatest HPS taus
makeKappaTaus = cms.Sequence(
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose +
	rerunDiscriminationByIsolationMVAOldDMrun2v1Loose +
	rerunDiscriminationByIsolationMVAOldDMrun2v1Medium +
	rerunDiscriminationByIsolationMVAOldDMrun2v1Tight +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VTight +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight +
	rerunDiscriminationByIsolationMVANewDMrun2v1raw +
	rerunDiscriminationByIsolationMVANewDMrun2v1VLoose +
	rerunDiscriminationByIsolationMVANewDMrun2v1Loose +
	rerunDiscriminationByIsolationMVANewDMrun2v1Medium +
	rerunDiscriminationByIsolationMVANewDMrun2v1Tight +
	rerunDiscriminationByIsolationMVANewDMrun2v1VTight +
	rerunDiscriminationByIsolationMVANewDMrun2v1VVTight +
	rerunDiscriminationByIsolationMVAOldDMrun2v1raw2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VVLoose2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VLoose2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1Loose2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1Medium2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1Tight2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VTight2017 +
	rerunDiscriminationByIsolationMVAOldDMrun2v1VVTight2017
)
