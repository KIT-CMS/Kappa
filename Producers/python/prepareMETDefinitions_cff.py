import FWCore.ParameterSet.Config as cms
import sys

from RecoMET.METProducers.PFMET_cfi import pfMet

def prepareMETs(process, jetCollectionPF):

    #### Input definitions like in classic MVA MET
    ### tracks from PV
    process.pfChargedPV = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('fromPV && charge !=0'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    ### tracks not from PV
    process.pfChargedPU = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('!fromPV && charge !=0'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    ### all neutrals
    process.pfNeutrals  = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('charge ==0'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    #### Neutrals in Jets passing PU Jet ID
    #### and Neutrals in Jets not passing PU Jet ID
    process.neutralInJets = cms.EDProducer("neutralCandidatePUIDJets",
                                           srcJets = cms.InputTag(jetCollectionPF),
                                           srcCandidates = cms.InputTag("pfNeutrals"),
                                           neutralParticlesPVJetsLabel = cms.string("neutralPassingPUIDJets"),
                                           neutralParticlesPUJetsLabel = cms.string("neutralFailingPUIDJets"),
                                           neutralParticlesUnclusteredLabel = cms.string("neutralParticlesUnclustered"),
                                           jetPUDIWP = cms.string("user"),
                                           jetPUIDMapLabel = cms.string("fullDiscriminant"))
  
    #### Track MET
    process.pfTrackMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(cms.InputTag("pfChargedPV")))
    ## No-PU MET
    process.pfNoPUMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(        cms.InputTag("pfChargedPV"),
                                                                                          cms.InputTag("neutralInJets", "neutralPassingPUIDJets")))
    ## PU corrected MET
    process.pfPUCorrectedMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag( cms.InputTag("pfChargedPV"), 
                                                                                          cms.InputTag("neutralInJets", "neutralPassingPUIDJets"),
                                                                                          cms.InputTag("neutralInJets", "neutralParticlesUnclustered")))
    ## PU MET
    process.pfPUMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(          cms.InputTag("pfChargedPU"),
                                                                                          cms.InputTag("neutralInJets", "neutralFailingPUIDJets")))
                                                          
    from PhysicsTools.PatAlgos.producersLayer1.metProducer_cfi import patMETs
    patMETsForMVA = patMETs.clone()
    patMETsForMVA.computeMETSignificance = cms.bool(False)
    patMETsForMVA.addGenMET = cms.bool(False)


    for met in ["pfTrackMET", "pfNoPUMET", "pfPUCorrectedMET", "pfPUMET"]:
        # create PF METs
        setattr(process, met, pfMet.clone(src = cms.InputTag(met+"Cands"), alias = cms.string(met)))
        # convert METs to pat objects
        setattr(process, "pat"+met,      patMETsForMVA.clone(metSource = cms.InputTag(met)))
