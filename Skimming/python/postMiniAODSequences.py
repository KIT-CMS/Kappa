import FWCore.ParameterSet.Config as cms
from Configuration.StandardSequences.Eras import eras

# Year & datatype specific dictionaries

globalTag = {
    2016 : {
        'MC' : '102X_mcRun2_asymptotic_v6',
        'data' : '102X_dataRun2_nanoAOD_2016_v1',
        'embedding' : '102X_dataRun2_nanoAOD_2016_v1',
    },
    2017 : {
        'MC' : '102X_mc2017_realistic_v6',
        'data' : '102X_dataRun2_v8',
        'embedding' : '102X_dataRun2_v8',
    },
    2018 : {
        'MC' : '102X_upgrade2018_realistic_v18',
        'data' : '102X_dataRun2_Sep2018ABC_v2',
        'data-prompt' : '102X_dataRun2_Prompt_v13',
        'embedding' : '102X_dataRun2_Sep2018ABC_v2',
        'embedding-prompt' : '102X_dataRun2_Prompt_v13',
    },
}

testfile = {
    2016 : {
        'MC' : '/store/mc/RunIISummer16MiniAODv3/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v2/40000/E67525C3-2B2C-E911-B297-C81F66B7C6E0.root',
        'data' : '/store/data/Run2016H/SingleMuon/MINIAOD/17Jul2018-v1/40000/FECFA65B-8C8B-E811-A529-001E67A3FEAC.root',
        'embedding' : '/store/user/jbechtel/gc_storage/MuTau_data_2016_CMSSW826_freiburg/TauEmbedding_MuTau_data_2016_CMSSW826_Run2016H/2/62/merged_4961.root',
    },
    2017 : {
        'MC' : '/store/mc/RunIIFall17MiniAODv2/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/E04EE70F-B643-E811-9970-0CC47ABB5178.root',
        'data' : '/store/data/Run2017F/SingleMuon/MINIAOD/31Mar2018-v1/80000/0095E95F-0037-E811-A88C-008CFAC942A0.root',
        'embedding' : '/store/user/aakhmets/gc_storage/MuTau_data_2017_CMSSW944_gridka/TauEmbedding_MuTau_data_2017_CMSSW944_Run2017F/17/merged_15816.root',
    },
    2018 : {
        'MC' : '/store/mc/RunIIAutumn18MiniAOD/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/102X_upgrade2018_realistic_v15_ext1-v1/80000/BA60B642-B308-7D46-B12F-40CCF2BBB6E8.root',
        'data' : '/store/data/Run2018C/SingleMuon/MINIAOD/17Sep2018-v1/60000/FD80B832-1D9C-2E4B-825B-5126ED09B958.root',
        'data-prompt' : '/store/data/Run2018D/SingleMuon/MINIAOD/22Jan2019-v2/60001/92EE1312-A04F-1C45-8311-01C681E081AD.root',
        'embedding' : '/store/user/sbrommer/gc_storage/MuTau_data_2018ABC_CMSSW1020/TauEmbedding_MuTau_data_2018ABC_CMSSW1020_Run2018C/94/merged_2593.root',
        'embedding-prompt' : '',
    },
}

EGammaPostRecoSequences = {
    2016 : '2016-Legacy',
    2017 : '2017-Nov17ReReco',
    2018 : '2018-Prompt',
}

Prefiring = {
    2016 : '2016BtoH',
    2017 : '2017BtoF',
    2018 : '2017BtoF', # no prefiring weights needed for 2018, so explicit setting is irrelevant
}

def create_postMiniAODSequences(year,dataset_type):
    print "Using year = %s and dataset_type = %s"%(year,dataset_type)
    if not (year in [2016, 2017, 2018] and dataset_type in ['data', 'data-prompt', 'MC', 'embedding', 'embedding-prompt']):
        print "Wrong assignment of year and/or dataset type. Please check appropriate settings by: cmsRun postMiniAODSequences.py help"
        exit(1)
    if year in [2016, 2017]:
        dataset_type = dataset_type.strip("-prompt") # only for 2018 data-taking, there are prompt versions for Run2018D

    outputfilename = "output_%s_%s.root"%(year,dataset_type)

    # Define flags for dataset types
    isData = 'data' in dataset_type
    isEmbedded = "embedding" in dataset_type
    isMC = "MC" in dataset_type

    # Definition & general setup for process
    process = cms.Process("SKIM")

    process.load('Configuration.StandardSequences.MagneticField_cff')
    process.load('Configuration.Geometry.GeometryRecoDB_cff')

    process.load("FWCore.MessageLogger.MessageLogger_cfi")

    process.MessageLogger.cerr.threshold = 'INFO'
    process.MessageLogger.categories.append('Ntuples')
    process.MessageLogger.cerr.INFO = cms.untracked.PSet(
        limit = cms.untracked.int32(10)
    )

    process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

    # Testfile
    process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring(
            testfile[year][dataset_type]
        )
    )

    # GT
    process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
    from Configuration.AlCa.GlobalTag import GlobalTag
    process.GlobalTag = GlobalTag( process.GlobalTag,  globalTag[year][dataset_type])

    dataset_type = dataset_type.strip("-prompt") # it's only important for GT & testfile to distinguish between prompt and rereco


    process.p = cms.Path()

    # HTXS 
    if isMC or isEmbedded: # no impact on embedding, just needed for the syntax of KIT setup
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
    if isMC:
        process.p *= cms.Sequence(process.mergedGenParticles*process.myGenerator*process.rivetProducerHTXS)
    elif isEmbedded:
        process.p *= cms.Sequence(process.mergedGenParticles)

    # additional MET Filter (full Run II legacy status)
    process.load('RecoMET.METFilters.ecalBadCalibFilter_cfi')

    baddetEcallist = cms.vuint32(
        [872439604,872422825,872420274,872423218,
         872423215,872416066,872435036,872439336,
         872420273,872436907,872420147,872439731,
         872436657,872420397,872439732,872439339,
         872439603,872422436,872439861,872437051,
         872437052,872420649,872422436,872421950,
         872437185,872422564,872421566,872421695,
         872421955,872421567,872437184,872421951,
         872421694,872437056,872437057,872437313,
         #  A more complete list of noisy crystals is currently tested (post-Moriond2019):
         872438182,872438951,872439990,872439864,872439609, 872437181,872437182,872437053,872436794,872436667,872436536,872421541,872421413, 872421414,872421031,872423083,872421439, # extra under test
         ])


    process.ecalBadCalibReducedMINIAODFilter = cms.EDFilter(
        "EcalBadCalibFilter",
        EcalRecHitSource = cms.InputTag("reducedEgamma:reducedEERecHits"),
        ecalMinEt        = cms.double(50.),
        baddetEcal    = baddetEcallist,
        taggingMode = cms.bool(True),
        debug = cms.bool(False)
        )
    process.p *= process.ecalBadCalibReducedMINIAODFilter

    # Electrons
    from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
    setupEgammaPostRecoSeq(
        process,
        runVID=True,
        eleIDModules=[
                'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff',

                'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff',
                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
        ],
        phoIDModules=[],
        era=EGammaPostRecoSequences[year],
    )
    process.p *= process.egammaPostRecoSeq

    # Taus
    from RecoTauTag.RecoTau.tools.runTauIdMVA import TauIDEmbedder
    na = TauIDEmbedder(process, cms,
        debug=False,
        toKeep=[
            "2017v2",
            "DPFTau_2016_v0",
            "DPFTau_2016_v1",
            "deepTau2017v1",
            "againstEle2018",
        ]
    )
    na.runTauID()
    process.p *= ( process.rerunMvaIsolationSequence)
    process.p *= getattr(process, "slimmedTausNewID")

    # PF and PUPPI MET (Type 1 + EE Noise corrected)
    from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
    from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD

    makePuppiesFromMiniAOD( process, True)

    runMetCorAndUncFromMiniAOD( # serves as also as input for PuppiMET production
        process,
        isData = isData or isEmbedded,
        fixEE2017 = False
        )

    runMetCorAndUncFromMiniAOD(
        process,
        isData = isData or isEmbedded,
        fixEE2017 = True,
        postfix = "ModifiedMET"
        )

    runMetCorAndUncFromMiniAOD(
        process,
        isData = isData or isEmbedded,
        metType = "Puppi",
        jetFlavor = "AK4PFPuppi",
        postfix = "Puppi"
        )

    process.puppiNoLep.useExistingWeights = False
    process.puppi.useExistingWeights = False

    process.p *= cms.Sequence(
        process.puppiMETSequence*
        process.fullPatMetSequence*
        process.fullPatMetSequenceModifiedMET*
        process.fullPatMetSequencePuppi
    )

    # Jets: JEC + DeepJet b-taggers + PU Jet ID
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

    process.load("RecoJets.JetProducers.PileupJetID_cfi")
    process.pileupJetIdUpdated = process.pileupJetId.clone(
        jets=cms.InputTag("slimmedJets"),
        inputIsCorrected=True,
        applyJec=True,
        vertexes=cms.InputTag("offlineSlimmedPrimaryVertices")
    )
    process.updatedPatJetsUpdatedJEC.userData.userInts.src += ['pileupJetIdUpdated:fullId']
    process.updatedPatJetsUpdatedJEC.userData.userFloats.src += ['pileupJetIdUpdated:fullDiscriminant']

    process.jecSequence = cms.Sequence(
        process.pileupJetIdUpdated
        *process.patJetCorrFactorsUpdatedJEC
        *process.updatedPatJetsUpdatedJEC
        *process.pfImpactParameterTagInfosUpdatedJEC
        *process.pfInclusiveSecondaryVertexFinderTagInfosUpdatedJEC
        *process.pfDeepCSVTagInfosUpdatedJEC
        *process.pfDeepFlavourTagInfosUpdatedJEC
        *process.pfDeepFlavourJetTagsUpdatedJEC
        *process.patJetCorrFactorsTransientCorrectedUpdatedJEC
        *process.updatedPatJetsTransientCorrectedUpdatedJEC
        *process.selectedUpdatedPatJetsUpdatedJEC
    )
    process.p *= process.jecSequence

    # Prefiring weights
    process.prefiringweight = cms.EDProducer(
            "L1ECALPrefiringWeightProducer",
            DataEra=cms.string(Prefiring[year]),  # Use 2016BtoH for 2016
            UseJetEMPt=cms.bool(False),  # can be set to true to use jet prefiring maps parametrized vs pt(em) instead of pt
            PrefiringRateSystematicUncty=cms.double(0.2)  # Minimum relative prefiring uncty per object
    )
    process.p *= process.prefiringweight

    process.out = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string(outputfilename),
        outputCommands = cms.untracked.vstring(
            "drop *",

            "keep *_rivetProducerHTXS_*_SKIM",
            "keep *_ecalBadCalibReducedMINIAODFilter_*_SKIM",
            "keep *_slimmedElectrons_*_SKIM",
            "keep *_slimmedTausNewID_*_SKIM",
            "keep *_slimmedMETsModifiedMET_*_SKIM", # to be used for 2017
            "keep *_slimmedMETs_*_SKIM", # to be used for 2016 & 2018
            "keep *_slimmedMETsPuppi_*_SKIM",
            "keep *_prefiringweight_*_SKIM",
            "keep patJets_selectedUpdatedPatJetsUpdatedJEC_*_SKIM",

            "keep GenEventInfoProduct_generator__SIM",
            "keep GenEventInfoProduct_generator__SIMembedding",

            "keep *_TriggerResults_*_HLT",
            "keep *_TriggerResults_*_SIMembedding",

            "keep *_caloStage2Digis_Tau_RECO",
            "keep *_fixedGridRhoFastjetAll__RECO",
            "keep recoBeamSpot_offlineBeamSpot__RECO",

            "keep *_caloStage2Digis_Tau_SIMembedding",
            "keep *_fixedGridRhoFastjetAll__MERGE",
            "keep recoBeamSpot_offlineBeamSpot__LHEembeddingCLEAN",

    #	"keep recoDeDxHitInfosedmAssociation_isolatedTracks__PAT",
    #	"keep recoBaseTagInfosOwned_slimmedJetsPuppi_tagInfos_PAT",
    #	"keep CSCDetIdCSCSegmentsOwnedRangeMap_slimmedMuons__PAT",
    #	"keep DTChamberIdDTRecSegment4DsOwnedRangeMap_slimmedMuons__PAT",
    #	"keep patPackedTriggerPrescales_patTrigger__PAT",
    #	"keep patPackedTriggerPrescales_patTrigger_l1max_PAT",
    #	"keep patPackedTriggerPrescales_patTrigger_l1min_PAT",
    #	"keep recoJetFlavourInfoMatchingCollection_slimmedGenJetsFlavourInfos__PAT",
    #	"keep patCompositeCandidates_oniaPhotonCandidates_conversions_PAT",
    #	"keep patPhotons_slimmedOOTPhotons__PAT",
    #	"keep patPhotons_slimmedPhotons__PAT",
    #	"keep patMETs_slimmedMETs__PAT",
    #	"keep patMETs_slimmedMETsNoHF__PAT",
    #	"keep patMETs_slimmedMETsPuppi__PAT",
    #	"keep patTaus_slimmedTaus__PAT",
    #	"keep patTaus_slimmedTausBoosted__PAT",
    #	"keep recoCaloJets_slimmedCaloJets__PAT",
    #	"keep recoVertexCompositePtrCandidates_slimmedKshortVertices__PAT",
    #	"keep recoVertexCompositePtrCandidates_slimmedLambdaVertices__PAT",
    #	"keep recoVertexCompositePtrCandidates_slimmedSecondaryVertices__PAT",
    #	"keep recoGenJets_slimmedGenJetsAK8__PAT",
    #	"keep recoGenJets_slimmedGenJetsAK8SoftDropSubJets__PAT",
    #	"keep patJets_slimmedJets__PAT",
    #	"keep patJets_slimmedJetsAK8__PAT",
    #	"keep patElectrons_slimmedElectrons__PAT",
    #	"keep patJets_slimmedJetsAK8PFPuppiSoftDropPacked_SubJets_PAT",
    #	"keep floatedmValueMap_offlineSlimmedPrimaryVertices__PAT",
    #	"keep patIsolatedTracks_isolatedTracks__PAT",
    #	"keep patPackedCandidates_lostTracks__PAT",
    #	"keep patPackedCandidates_lostTracks_eleTracks_PAT",
    #	"keep recoDeDxHitInfos_isolatedTracks__PAT",
    #	"keep Strings_slimmedPatTrigger_filterLabels_PAT",
    #	"keep uint_bunchSpacingProducer__PAT",
    #	"keep EcalRecHitsSorted_reducedEgamma_reducedEBRecHits_PAT",
    #	"keep EcalRecHitsSorted_reducedEgamma_reducedEERecHits_PAT",
    #	"keep EcalRecHitsSorted_reducedEgamma_reducedESRecHits_PAT",
    #	"keep recoConversions_reducedEgamma_reducedSingleLegConversions_PAT",
    #	"keep recoPhotonCores_reducedEgamma_reducedGedPhotonCores_PAT",
    #	"keep recoPhotonCores_reducedEgamma_reducedOOTPhotonCores_PAT",
    #	"keep recoSuperClusters_reducedEgamma_reducedOOTSuperClusters_PAT",
    #	"keep recoCaloClusters_reducedEgamma_reducedOOTEBEEClusters_PAT",
    #	"keep recoCaloClusters_reducedEgamma_reducedOOTESClusters_PAT",

            "keep recoCaloClusters_reducedEgamma_reducedEBEEClusters_PAT",
            "keep recoCaloClusters_reducedEgamma_reducedESClusters_PAT",
            "keep recoConversions_reducedEgamma_reducedConversions_PAT",
            "keep recoGsfElectronCores_reducedEgamma_reducedGedGsfElectronCores_PAT",
            "keep recoGsfTracks_reducedEgamma_reducedGsfTracks_PAT",
            "keep recoSuperClusters_reducedEgamma_reducedSuperClusters_PAT",

            "keep recoGenJets_slimmedGenJets__PAT",
            "keep PileupSummaryInfos_slimmedAddPileupInfo__PAT",
            "keep recoGenParticles_prunedGenParticles__PAT",
            "keep patJets_slimmedJetsPuppi__PAT",
            "keep patMuons_slimmedMuons__PAT",
            "keep edmTriggerResults_TriggerResults__PAT",
            "keep patTriggerObjectStandAlones_slimmedPatTrigger__PAT",
            "keep recoVertexs_offlineSlimmedPrimaryVertices__PAT",
            "keep patPackedGenParticles_packedGenParticles__PAT",
            "keep patPackedCandidates_packedPFCandidates__PAT",

            "keep recoCaloClusters_reducedEgamma_reducedEBEEClusters_DQM",
            "keep recoCaloClusters_reducedEgamma_reducedESClusters_DQM",
            "keep recoConversions_reducedEgamma_reducedConversions_DQM",
            "keep recoGsfElectronCores_reducedEgamma_reducedGedGsfElectronCores_DQM",
            "keep recoGsfTracks_reducedEgamma_reducedGsfTracks_DQM",
            "keep recoSuperClusters_reducedEgamma_reducedSuperClusters_DQM",

            "keep recoGenJets_slimmedGenJets__DQM",
            "keep PileupSummaryInfos_slimmedAddPileupInfo__DQM",
            "keep recoGenParticles_prunedGenParticles__DQM",
            "keep patJets_slimmedJetsPuppi__DQM",
            "keep patMuons_slimmedMuons__DQM",
            "keep edmTriggerResults_TriggerResults__DQM",
            "keep patTriggerObjectStandAlones_slimmedPatTrigger__DQM",
            "keep recoVertexs_offlineSlimmedPrimaryVertices__DQM",
            "keep patPackedGenParticles_packedGenParticles__DQM",
            "keep patPackedCandidates_packedPFCandidates__DQM",

            "keep recoCaloClusters_reducedEgamma_reducedEBEEClusters_RECO",
            "keep recoCaloClusters_reducedEgamma_reducedESClusters_RECO",
            "keep recoConversions_reducedEgamma_reducedConversions_RECO",
            "keep recoGsfElectronCores_reducedEgamma_reducedGedGsfElectronCores_RECO",
            "keep recoGsfTracks_reducedEgamma_reducedGsfTracks_RECO",
            "keep recoSuperClusters_reducedEgamma_reducedSuperClusters_RECO",

            "keep recoGenJets_slimmedGenJets__RECO",
            "keep PileupSummaryInfos_slimmedAddPileupInfo__RECO",
            "keep recoGenParticles_prunedGenParticles__RECO",
            "keep patJets_slimmedJetsPuppi__RECO",
            "keep patMuons_slimmedMuons__RECO",
            "keep edmTriggerResults_TriggerResults__RECO",
            "keep patTriggerObjectStandAlones_slimmedPatTrigger__RECO",
            "keep recoVertexs_offlineSlimmedPrimaryVertices__RECO",
            "keep patPackedGenParticles_packedGenParticles__RECO",
            "keep patPackedCandidates_packedPFCandidates__RECO",

            "keep recoCaloClusters_reducedEgamma_reducedEBEEClusters_MERGE",
            "keep recoCaloClusters_reducedEgamma_reducedESClusters_MERGE",
            "keep recoConversions_reducedEgamma_reducedConversions_MERGE",
            "keep recoGsfElectronCores_reducedEgamma_reducedGedGsfElectronCores_MERGE",
            "keep recoGsfTracks_reducedEgamma_reducedGsfTracks_MERGE",
            "keep recoSuperClusters_reducedEgamma_reducedSuperClusters_MERGE",

            "keep recoGenJets_slimmedGenJets__MERGE",
            "keep PileupSummaryInfos_slimmedAddPileupInfo__MERGE",
            "keep recoGenParticles_prunedGenParticles__MERGE",
            "keep patJets_slimmedJetsPuppi__MERGE",
            "keep patMuons_slimmedMuons__MERGE",
            "keep edmTriggerResults_TriggerResults__MERGE",
            "keep patTriggerObjectStandAlones_slimmedPatTrigger__MERGE",
            "keep patTriggerObjectStandAlones_selectedPatTrigger__MERGE",
            "keep recoVertexs_offlineSlimmedPrimaryVertices__MERGE",
            "keep patPackedGenParticles_packedGenParticles__MERGE",
            "keep patPackedCandidates_packedPFCandidates__MERGE",
            )
        )

    process.ep = cms.EndPath(process.out)
    f = open("dump_%s_%s.py"%(year,dataset_type),"w")
    f.write(process.dumpPython())
    f.close()
    return process


if __name__ == "__main__":
    from FWCore.ParameterSet.VarParsing import VarParsing

    options = VarParsing('python')
    options.register('year', 2017, VarParsing.multiplicity.singleton, VarParsing.varType.int, 'Data-taking year. Please choose from 2016, 2017 or 2018')
    options.register('dtype', 'MC', VarParsing.multiplicity.singleton, VarParsing.varType.string, 'Dataset type. Please choose from data, data-prompt, MC, embedding or embedding-prompt')
    options.parseArguments()

    process = create_postMiniAODSequences(options.year, options.dtype)
