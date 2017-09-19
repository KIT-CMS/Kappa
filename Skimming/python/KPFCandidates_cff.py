#-# Copyright (c) 2014 - All Rights Reserved
#-#   Joram Berger <joram.berger@cern.ch>
#-#   Roger Wolf <roger.wolf@cern.ch>

import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

cmssw_version_number = tools.get_cmssw_version_number()

## ------------------------------------------------------------------------
## Good offline PV selection: 
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

goodOfflinePrimaryVertices = cms.EDFilter('PrimaryVertexObjectFilter',
    src = cms.InputTag('offlinePrimaryVertices'),
    filterParams = pvSelector.clone( minNdof = 4.0, maxZ = 24.0 ),
)

goodOfflinePrimaryVertexEvents = cms.EDFilter("KVertexFilter",
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(999999),
    src = cms.InputTag("goodOfflinePrimaryVertices")
)

## ------------------------------------------------------------------------
## TopProjections from CommonTools/ParticleFlow:
from CommonTools.ParticleFlow.PFBRECO_cff import *
if (cmssw_version_number.startswith("7_4")):
	from CommonTools.ParticleFlow.pfParticleSelection_cff import *

## pf candidate configuration for everything but CHS jets
pfPileUpIso.PFCandidates        = 'particleFlow'
pfPileUpIso.Vertices            = 'offlineSlimmedPrimaryVertices'
pfPileUpIso.checkClosestZVertex = True
pfNoPileUpIso.bottomCollection  = 'particleFlow'

## pf candidate configuration for deltaBeta corrections for muons and electrons 
pfNoPileUpChargedHadrons        = pfAllChargedHadrons.clone()
pfNoPileUpNeutralHadrons        = pfAllNeutralHadrons.clone()
pfNoPileUpPhotons 	        = pfAllPhotons.clone()
pfPileUpChargedHadrons	        = pfAllChargedHadrons.clone(src = 'pfPileUpIso')

## pf candidate configuration for CHS jets
pfPileUp.Vertices               = 'offlineSlimmedPrimaryVertices'
pfPileUp.checkClosestZVertex    = False

## ------------------------------------------------------------------------
## Definition of sequences

## run this to produce only those pf candidate collections that should go
## into the KappaTuple and nothing more
makeKappaPFCandidates = cms.Sequence(
    pfParticleSelectionSequence
    )

## run this to run the full PFBRECO sequence, which is needed e.g. for CHS
## jets ()
makePFBRECO = cms.Sequence(
    PFBRECO
    )

## run this to produce the particle flow collections that are expected to
## be present for deltaBeta corrections for muons and electrons. This needs
## at least makeKappaPFCandidates to be run beforehand
makePFCandidatesForDeltaBeta = cms.Sequence(
	pfNoPileUpChargedHadrons *
	pfNoPileUpNeutralHadrons *
	pfNoPileUpPhotons *
	pfPileUpChargedHadrons
	)
