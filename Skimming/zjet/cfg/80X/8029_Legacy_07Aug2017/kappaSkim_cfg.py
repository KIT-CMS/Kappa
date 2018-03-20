# Kappa test: CMSSW 8.0.29

import math
import os
import sys

import FWCore.ParameterSet.Config as cms
import Kappa.Producers.EventWeightCountProducer_cff


#################
# Options setup #
#################
#
# Define options for 'cmsRun' here. These can be accessed later in the
# script using 'options.<optionName>'
#
# Note: Some options are pre-defined by CMSSW. These include:
# ----
#       inputFiles      :  list of input filenames [default: <empty list>]
#       outputFile      :  name of the output file [default: "output.root"]
#       maxEvents       :  maximum number of events to process [default: -1 (=no limit)]

from Kappa.Skimming.optionsInterface import options, register_option

# specify some custom command-line arguments
register_option('isData',
                default=True,
                type_=bool,
                description="True if sample is data, False if Monte Carlo (default: True)")
register_option('globalTag',
                default='80X_dataRun2_2016LegacyRepro_v4',
                type_=str,
                description='Global tag')
register_option('reportEvery',
                default=1000,
                type_=int,
                description=("Print a message after each <reportEvery> "
                             "events processed (default: 1000)"))
register_option('kappaVerbosity',
                default=0,
                type_=int,
                description='Verbosity of KAPPA debug output (default: 0)')
register_option('edmOut',
                default='',
                type_=str,
                description=('(for testing only) write edm file (e.g miniAOD) to '
                             'this path (if empty/unset, no edm file is written).'))
register_option('dumpPythonAndExit',
                default=False,
                type_=bool,
                description=('(for testing only) dump the full cmsRun Python config '
                             'and exit.'))


# parse the command-line arguments
options.parseArguments()


################
# Remote setup #
################

# if submitted with grid-control, assume this is a remote skimming job
# -> override the global tag and data/MC flag options
if os.getenv("GC_VERSION"):
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    options.edmOut = ""
    options.dumpPythonAndExit = False
    options.kappaVerbosity = 0
    options.reportEvery = int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]


########################
# Create CMSSW Process #
########################
process = cms.Process("KAPPA")

# most CMSSW analysis modules will be added to the path
process.path = cms.Path()

# CMSSW output modules will be added to the endpath
process.endpath = cms.EndPath()

# limit the number of processed events (or set to -1 for no limit)
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

# configure process with options
process.options = cms.untracked.PSet(
    wantSummary=cms.untracked.bool(True),
    allowUnscheduled=cms.untracked.bool(True),  # some modules need the unscheduled mode!
    emptyRunLumiMode=cms.untracked.string('doNotHandleEmptyRunsAndLumis'),
    #SkipEvent=cms.untracked.vstring('ProductNotFound')   # only for debugging
)

# set the input files
process.source = cms.Source("PoolSource",
    fileNames=cms.untracked.vstring(options.inputFiles)
)

# -- print process configuration
print "\n----- CMSSW configuration -----"
print "input:          ", (process.source.fileNames[0] if len(process.source.fileNames) else ""), ("... (%d files)" % len(process.source.fileNames) if len(process.source.fileNames) > 1 else "")
print "file type:      ", "miniAOD"
print "data:           ", options.isData
print "output:         ", options.outputFile
print "global tag:     ", options.globalTag
print "max events:     ", (str(process.maxEvents.input)[20:-1])
print "cmssw version:  ", os.environ["CMSSW_VERSION"]
print "---------------------------------\n"



#################
# CMSSW modules #
#################

# -- CMSSW message logger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
process.MessageLogger.default = cms.untracked.PSet(
    ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5))
)

# -- CMSSW geometry and detector conditions
# (These are needed for some PAT tuple production steps)
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.GlobalTag.globaltag = cms.string(options.globalTag)


#########
# KAPPA #
#########

# -- add kappa tuple producer (CMSSW EDAnalyzer)
process.load('Kappa.Producers.KTuple_cff')
process.kappaTuple = cms.EDAnalyzer(
    'KTuple',
    process.kappaTupleDefaultsBlock,  # load Kappa default config
    outputFile=cms.string(options.outputFile),
)

#process.kappaTuple.Info.printHltList =  cms.bool(True)
process.kappaTuple.verbose = options.kappaVerbosity
process.kappaTuple.active = cms.vstring('VertexSummary', 'BeamSpot')
process.kappaTuple.Info.pileUpInfoSource = cms.InputTag("slimmedAddPileupInfo")

if options.isData:
    process.kappaTuple.active += cms.vstring('DataInfo')
else:
    process.kappaTuple.active += cms.vstring('GenInfo', 'GenParticles')
    process.kappaTuple.GenParticles.genParticles.src = cms.InputTag("prunedGenParticles")

# add KAPPA tuple sequence to output
process.kappaOut = cms.Sequence(process.kappaTuple)


###########
# Trigger #
###########

# -- configure KAPPA trigger object
process.kappaTuple.active += cms.vstring('TriggerObjectStandalone')

# CMSSW 80X -> trigger object is 'selectedPatTrigger'
process.kappaTuple.TriggerObjectStandalone.triggerObjects = cms.PSet(
    src=cms.InputTag("selectedPatTrigger")
)

# read in trigger results from 'HLT' process
process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")

# set flag to prevent KAPPA error if process name is something other than 'HLT'
# TODO: flag pending deletion
process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)

# read in MET filter bits from RECO/PAT trigger object (use RECO for PromptReco)
process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO")


# write out HLT information for trigger names matching regex
process.kappaTuple.Info.hltWhitelist = cms.vstring(
    # HLT regex selection can be tested at https://regex101.com (with gm options)
    # single muon triggers, e.g. HLT_Mu50_v1
    "^HLT_(Iso)?(Tk)?Mu[0-9]+(_eta2p1|_TrkIsoVVL)?_v[0-9]+$",
    # double muon triggers, e.g. HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v1
    "^HLT_Mu[0-9]+(_TrkIsoVVL)?_(Tk)?Mu[0-9]+(_TrkIsoVVL)?(_DZ)?_v[0-9]+$",
    # double electrons trigger
    "^HLT_Ele[0-9]+_Ele[0-9]+(_CaloIdL)?(_TrackIdL)?(_IsoVL)?(_DZ)?_v[0-9]+$",
)


#################
# Event Filters #
#################

# In data, a few events do not have a valid PF candidate collection
# These events get vetoed by the following filter:
if options.isData:
    process.pfFilter = cms.EDFilter('CandViewCountFilter',
        src = cms.InputTag('packedPFCandidates'),
        minNumber = cms.uint32(1),
        filter = cms.bool(False)  # add Filter option
    )
    process.path *= (process.pfFilter)


###########################
# Configure PF Candidates #
###########################

# -- load default Kappa config for skimming PF candidates
process.load("Kappa.Skimming.KPFCandidates_miniAOD_cff")

## TODO: seems to do nothing -> pending review for deletion
### -- filter PV collection to obtain "good" offline primary vertices
##from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
##process.goodOfflinePrimaryVertices = cms.EDFilter(
##    'PrimaryVertexObjectFilter',
##    filterParams=pvSelector.clone(maxZ = 24.0),  # ndof >= 4, rho <= 2
##    src=cms.InputTag('offlineSlimmedPrimaryVertices'),
##)


# for an explanation of 'fromPV', refer to:
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016#PV_Assignment

# -- apply filters to obtain some special PF candidate collections

# PF candidates likely not from pileup
process.pfNoPileUpIso = cms.EDFilter("CandPtrSelector",
    src = cms.InputTag("packedPFCandidates"),
    cut = cms.string("fromPV > 1")  # high 'fromPV' score
)

# PF candidates possibly from pileup
process.pfPileUpIso = cms.EDFilter("CandPtrSelector",
    src = cms.InputTag("packedPFCandidates"),
    cut = cms.string("fromPV <= 1")  # low 'fromPV' score
)

# PF candidates marked as neutral hadrons or photons
process.pfAllNeutralHadronsAndPhotons = cms.EDFilter("CandPtrSelector",
    src = cms.InputTag("pfNoPileUp"),
    cut = cms.string(
        "abs(pdgId) = 111  | "  # neutral pion
        "abs(pdgId) = 130  | "  # neutral kaon (long)
        "abs(pdgId) = 310  | "  # neutral kaon (short)
        "abs(pdgId) = 2112 | "  # neutron
        "abs(pdgId) = 22"       # photon
    )
)

process.path *= (
    #process.goodOfflinePrimaryVertices*  # pending review for deletion
    process.pfNoPileUpIso*
    process.pfPileUpIso*
    process.makeKappaPFCandidates*
    process.pfAllNeutralHadronsAndPhotons
)


###################
# Configure Muons #
###################

# -- load default Kappa config for skimming muons
process.load("Kappa.Skimming.KMuons_miniAOD_cff")
process.kappaTuple.active += cms.vstring('Muons')

# -- set basic skimming parameters
process.kappaTuple.Muons.minPt = 8.0
process.kappaTuple.Muons.muons.src = cms.InputTag("slimmedMuons")
# TODO: check which one of these is actually used
#process.kappaTuple.Muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
process.kappaTuple.Muons.muons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")

# -- muon isolation

# should calculate and store muon PF isolation quantities?
process.kappaTuple.Muons.doPfIsolation = cms.bool(False)

# don't look for inexistent isolation PF candidates
process.kappaTuple.Muons.muons.srcMuonIsolationPF = cms.InputTag("")

# specify collection to use for calculating the muon isolations
for iso_label in ["muPFIsoDepositCharged",
                  "muPFIsoDepositChargedAll",
                  "muPFIsoDepositNeutral",
                  "muPFIsoDepositGamma",
                  "muPFIsoDepositPU"]:
    setattr(getattr(process, iso_label), "src", cms.InputTag("slimmedMuons"))

# -- other flags
process.kappaTuple.Muons.noPropagation = cms.bool(True)  # TODO: document this

# -- add to process
process.path *= (process.makeKappaMuons)


#######################
# Configure Electrons #
#######################

from Kappa.Skimming.KElectrons_miniAOD_cff import setupElectrons

# -- load default Kappa config for skimming electrons
process.load("Kappa.Skimming.KElectrons_miniAOD_cff")
process.kappaTuple.active += cms.vstring('Electrons')

# -- set basic skimming parameters
process.kappaTuple.Electrons.minPt = 8.0
process.kappaTuple.Electrons.electrons.src = cms.InputTag("slimmedElectrons")
# TODO: check which one of these is actually used
process.kappaTuple.Electrons.electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")
process.kappaTuple.Electrons.vertexcollection = cms.InputTag("offlineSlimmedPrimaryVertices")

# -- electron isolation
process.kappaTuple.Electrons.electrons.rhoIsoInputTag = cms.InputTag("slimmedJets", "rho")

# -- electron IDs
process.load("RecoEgamma/ElectronIdentification/ElectronIDValueMapProducer_cfi")
process.kappaTuple.Electrons.srcIds = cms.string("standalone");
process.kappaTuple.Electrons.ids = cms.VInputTag(
    "egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-veto",
    "egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-loose",
    "egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-medium",
    "egmGsfElectronIDs:cutBasedElectronID-Summer16-80X-V1-tight",
    "electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring16GeneralPurposeV1Values"
)

# -- apply regression correction?
# https://twiki.cern.ch/twiki/bin/view/CMS/EGMRegression

# to allow reading regression weights from the database
from EgammaAnalysis.ElectronTools.regressionWeights_cfi import regressionWeights
process = regressionWeights(process)

## add regression sequence to path
process.load('EgammaAnalysis.ElectronTools.regressionApplication_cff')
process.path += process.regressionApplication

# -- apply electron scale correction (on data) or energy smearing (on MC)
# https://twiki.cern.ch/twiki/bin/view/CMS/EGMSmearer

# In order to avoid annoying crashes please add the following selector to the
# electrons before the calibrated collection is produced (in the meantime we
# are providing a protection in the calibrator itself):
process.electronsForScaleSmearing = cms.EDFilter('PATElectronSelector',
              src=cms.InputTag('slimmedElectrons'),
              cut=cms.string("pt>5 && abs(superCluster.eta)<2.5")
)
process.path += process.electronsForScaleSmearing

# apply scale/smearing
# note: the following needs 'git cms-merge-topic cms-egamma:EGM_gain_v1'
_egamma_smearing_file = "EgammaAnalysis/ElectronTools/data/ScalesSmearings/Legacy2016_07Aug2017_ele_unc"
process.calibratedPatElectrons = cms.EDProducer("CalibratedPatElectronProducerRun2",
    # input collections
    electrons = cms.InputTag('electronsForScaleSmearing'),
    gbrForestName = cms.vstring(
        'electron_eb_ECALTRK_lowpt', 'electron_eb_ECALTRK',
        'electron_ee_ECALTRK_lowpt', 'electron_ee_ECALTRK',
        'electron_eb_ECALTRK_lowpt_var', 'electron_eb_ECALTRK_var',
        'electron_ee_ECALTRK_lowpt_var', 'electron_ee_ECALTRK_var'
    ),

    # if isMC is true, MC smearing is applied
    # if isMC is false, data corrections are applied
    isMC = cms.bool(not options.isData),
    autoDataType = cms.bool(True),

    # set to True to get special "fake" smearing for synchronization.
    # (*don't* use in production, *only* for synchronization)
    isSynchronization = cms.bool(False),
    # file containing corrections
    correctionFile = cms.string(_egamma_smearing_file),
    recHitCollectionEB = cms.InputTag('reducedEgamma:reducedEBRecHits'),
    recHitCollectionEE = cms.InputTag('reducedEgamma:reducedEERecHits')
)

# -- need random number generator for smearing
process.load('Configuration.StandardSequences.Services_cff')
process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    calibratedPatElectrons=cms.PSet(
        # seed is from TWiki example. TODO: use a different seed?
        initialSeed=cms.untracked.uint32(81),
        engineName=cms.untracked.string('TRandom3'),
    )
)

process.path += process.calibratedPatElectrons

# selection criteria for ensuring well-defined VIDs
process.selectedElectrons = cms.EDFilter("PATElectronSelector",
    src = cms.InputTag("calibratedPatElectrons"),
    cut = cms.string("pt>5 && abs(eta)")
)

process.path += process.selectedElectrons

# -- call the KAPPA electron setup routine with calibrated collection
_electron_tag = "selectedElectrons"
setupElectrons(process, _electron_tag)

process.egmGsfElectronIDs.physicsObjectSrc = cms.InputTag(_electron_tag)
process.electronIDValueMapProducer.srcMiniAOD = cms.InputTag(_electron_tag)
process.electronRegressionValueMapProducer.srcMiniAOD = cms.InputTag(_electron_tag)
process.electronMVAValueMapProducer.srcMiniAOD = cms.InputTag(_electron_tag)
process.kappaTuple.Electrons.electrons.src = _electron_tag


# -- add to process
process.path *= (process.makeKappaElectrons)


######################
# Configure JTB Jets #
######################

# jet collections obtained with 'JetToolbox' CMSSW module:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox


# -- set basic skimming parameters
process.kappaTuple.Jets.minPt = 5.0
process.kappaTuple.Jets.taggers = cms.vstring()  # TODO: do we need this?

# -- set up jet toolbox jets

jtb_sequence_name = 'sequence'

# go through all combinations of jet radius and PU subtraction algorithms
for _jet_algo_radius in ('ak4', 'ak8'):
    for _PU_method in ("", "CHS", "Puppi"):
        _seq_name = "{}{}{}".format(jtb_sequence_name, _jet_algo_radius, _PU_method)

        # calculate and evaluate PUJetID only for ak4CHS jets (TODO: do we need this?)
        _do_PUJetID = False
        #if _jet_algo_radius == 'ak4' and _PU_method == "CHS":
        #    _do_PUJetID = True

        # create jet sequence with jet toolbox
        jetToolbox(process,
                   _jet_algo_radius,
                   _seq_name,
                   'out',
                   miniAOD=True,
                   runOnMC=not options.isData,
                   JETCorrPayload="None",  # do *not* correct jets with JEC
                   PUMethod=_PU_method,    # PU subtraction method
                   addPruning=False,
                   addSoftDrop=False,
                   addPrunedSubjets=False,
                   addNsub=False,
                   maxTau=6,
                   addTrimming=False,
                   addFiltering=False,
                   addNsubSubjets=False,
                   addPUJetID=_do_PUJetID)

        # add jet sequence to process
        process.path *= getattr(process, _seq_name)

        # add PUJetID calculator and evaluator to process
        if _do_PUJetID:
            process.path *= getattr(process, "{}PF{}pileupJetIdCalculator".format(_jet_algo_radius.upper(), _PU_method))
            process.path *= getattr(process, "{}PF{}pileupJetIdEvaluator".format(_jet_algo_radius.upper(), _PU_method))


######################
# Configure PAT Jets #
######################

from Kappa.Skimming.KPatJets_miniAOD_cff import setup_PatJets

# -- set up PAT jets

# make sure all hadrons and partons are available
if not options.isData:
   # Select the genpartons to be used for flavour info
    process.patJetPartons = cms.EDProducer('HadronAndPartonSelector',
                                           src = cms.InputTag("generator"),
                                           particles = cms.InputTag("prunedGenParticles"),
                                           partonMode = cms.string("Auto"),
                                           fullChainPhysPartons = cms.bool(True)
                                           )
    ##process.path += process.patJetPartons

# set up PAT jets
patJets = setup_PatJets(process, options.isData)

# go through all combinations of jet radius and PU subtraction algorithms
for _jet_radius in (4, 8):
    for _PU_method in ("", "CHS", "Puppi"):
        _jet_collection_name = "ak%dPFJets%s" % (_jet_radius, _PU_method)
        _patJet_collection_name = "AK%dPF%s" % (_jet_radius, _PU_method)

        _jets_for_kappa_producer = 'selectedPatJets'+_patJet_collection_name

        # update jet flavor definition
        # https://twiki.cern.ch/twiki/bin/view/Main/BackportNewFlavourDefCMSSW8
        if not options.isData:
            # Create the jet:flavour mapping using your jets and selected genpartons
            _flavorinfo_module = "{}FlavorInfos".format(_patJet_collection_name)
            setattr(process, _flavorinfo_module,
                             cms.EDProducer("JetFlavourClustering",
                                            jets = cms.InputTag('selectedPatJets'+_patJet_collection_name),
                                            bHadrons = cms.InputTag("patJetPartons", "bHadrons"),
                                            cHadrons = cms.InputTag("patJetPartons", "cHadrons"),
                                            partons = cms.InputTag("patJetPartons", "physicsPartons"),
                                            leptons = cms.InputTag("patJetPartons", "leptons"),
                                            jetAlgorithm = cms.string("AntiKt"),
                                            rParam = cms.double(float(_jet_radius)/10.),  # Must match the parameter of the input jets
                                            ghostRescaling = cms.double(1e-18),
                                            relPtTolerance = cms.double(5),  # large as we are dealing with calibrated jets
                                            hadronFlavourHasPriority = cms.bool(False)))

            # produce a flavor-updated PAT jet collection
            _updated_module = "flavUpdatedPatJets{}".format(_patJet_collection_name)
            setattr(process, _updated_module,
                             cms.EDProducer("UpdatePatJetFlavourInfo",
                                            jetSrc = cms.InputTag('selectedPatJets'+_patJet_collection_name),
                                            jetFlavourInfos = cms.InputTag(_flavorinfo_module)))
            # tell KAPPA to use the collection as its jet collection
            _jets_for_kappa_producer = _updated_module

        # add KAPPA PatJet config to KAPPA Tuple
        setattr(process.kappaTuple.PatJets,
            _jet_collection_name,
            cms.PSet(
                src = cms.InputTag(_jets_for_kappa_producer)
            )
        )

        # add to process
        process.path *= patJets[_patJet_collection_name]

    # GenJets
    if not options.isData:
        _jet_collection_name = "ak%sGenJetsNoNu" % (_jet_radius)
        # GenJets are just KLVs: add collection to whitelist
        process.kappaTuple.LV.whitelist += cms.vstring(_jet_collection_name)

# -- activate KAPPA producers

# PatJet producer
process.kappaTuple.active += cms.vstring('PatJets')

# GenJets (=='LV') producer
if not options.isData:
    process.kappaTuple.active += cms.vstring('LV')

    process.kappaTuple.LV.ak4GenJetsNoNu = cms.PSet(src=cms.InputTag("ak4GenJetsNoNu"))
    process.kappaTuple.LV.ak8GenJetsNoNu = cms.PSet(src=cms.InputTag("ak8GenJetsNoNu"))

# PileupDensity producer
process.kappaTuple.active += cms.vstring('PileupDensity')
process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")


#################
# Configure MET #
#################

# official Prescription for calculating corrections and uncertainties on Missing Transverse Energy (MET):
# https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription#Instructions_for_8_0_X_X_26_patc

from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

# create collection of PF candidates likely coming from the primary vertex
process.packedPFCandidatesCHSNotFromPV = cms.EDFilter('CandPtrSelector',
    src = cms.InputTag('packedPFCandidates'),
    cut = cms.string('fromPV==0')  # only loose selection (0)
)
process.path *= (process.packedPFCandidatesCHSNotFromPV)
process.packedPFCandidatesCHS = cms.EDFilter('CandPtrSelector',
    src = cms.InputTag('packedPFCandidates'),
    cut = cms.string('fromPV() > 0')  # only loose selection (0)
)
process.path *= (process.packedPFCandidatesCHS)

# -- start of MET recipe

# the following lines are for default MET for Type1 corrections

# If you only want to re-correct for JEC and get the proper uncertainties for the default MET
runMetCorAndUncFromMiniAOD(process,
                           isData=options.isData,
                           pfCandColl='packedPFCandidatesCHS',
                           recoMetFromPFCs=True)

## If you would like to re-cluster both jets and met and get the proper uncertainties
#runMetCorAndUncFromMiniAOD(process,
#                           isData=options.isData,
#                           pfCandColl=cms.InputTag("packedPFCandidates"),
#                           recoMetFromPFCs=True,
#                           CHS = True, # this is an important step and determines what type of jets to be reclustered
#                           reclusterJets = True
#                           )


if not options.isData:

    # ! NOTE: This probably won't work for Summer16 MC

    # Now you are creating the bad muon corrected MET
    process.load('RecoMET.METFilters.badGlobalMuonTaggersMiniAOD_cff')
    process.badGlobalMuonTaggerMAOD.taggingMode = cms.bool(True)
    process.cloneGlobalMuonTaggerMAOD.taggingMode = cms.bool(True)

    from PhysicsTools.PatUtils.tools.muonRecoMitigation import muonRecoMitigation

    muonRecoMitigation(
        process=process,
        pfCandCollection = "packedPFCandidatesCHS", #input PF Candidate Collection
        runOnMiniAOD = True,
        selection="", # You can use a custom selection for your bad muons.
                      # Leave empty if you would like to use the bad muon recipe definition.
        muonCollection="", # The muon collection name where your custom selection will be applied to.
                           # Leave empty if you would like to use the bad muon recipe definition.
        cleanCollName="cleanMuonsPFCandidatesCHS", #output pf candidate collection name
        cleaningScheme="all", # Options are: "all", "computeAllApplyBad","computeAllApplyClone".
                              # Decides which (or both) bad muon collections to be used for MET
                              # cleaning coming from the bad muon recipe.
        postfix="" #Use if you would like to add a post fix to your muon / pf collections
    )

    runMetCorAndUncFromMiniAOD(
        process,
        isData=options.isData,
        pfCandColl="cleanMuonsPFCandidatesCHS",
        recoMetFromPFCs=True,
        postfix="MuEGClean"
    )

    #process.mucorMET = cms.Sequence(
    #   process.badGlobalMuonTaggerMAOD*
    #   process.cloneGlobalMuonTaggerMAOD*
    #   process.badMuons*  # if you are using cleaning mode "all", uncomment this line
    #   process.cleanMuonsPFCandidatesCHS*
    #   process.fullPatMetSequenceMuClean
    #)


    process.path *= process.slimmedMETsMuEGClean
    # wire CHS MET
    process.kappaTuple.PatMET.metCHS = cms.PSet(src=cms.InputTag("slimmedMETsMuEGClean"),
                                            uncorrected=cms.bool(True))
    # wire PF MET to MET from PAT process (for Summer16 MC)
    process.kappaTuple.PatMET.metPF = cms.PSet(src=cms.InputTag("slimmedMETs", "", "PAT"),
                                           uncorrected=cms.bool(True))
else:
    # wire CHS MET
    process.kappaTuple.PatMET.metCHS = cms.PSet(src=cms.InputTag("slimmedMETs"),
                                            uncorrected=cms.bool(True))
    # wire PF MET to MET from RECO process (for legacy data)
    process.kappaTuple.PatMET.metPF = cms.PSet(src=cms.InputTag("slimmedMETs", "", "RECO"),
                                           uncorrected=cms.bool(True))

# this should be OK: 'slimmedMETsPuppi' is in miniAOD
process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"),
                                              uncorrected=cms.bool(True))

# uncorrect MET: correcting step done in Excalibur for calibration purposes
process.kappaTuple.PatMET.uncorrected = cms.bool(True)

# -- end of MET recipe

# -- activate KAPPA producers
process.kappaTuple.active += cms.vstring('PatMET')



################
# Kappa Output #
################

# add 'kappaOut' sequence/task to endpath
process.endpath *= (process.kappaOut)

# -- wire 'Kappa' branches to miniAOD quantities

# add to Kappa 'BeamSpot': 'offlineBeamSpot'
process.kappaTuple.BeamSpot.offlineBeamSpot = cms.PSet(
    src=cms.InputTag("offlineBeamSpot"))

# add to Kappa 'VertexSummary': 'offlineSlimmedPrimaryVertices'
process.kappaTuple.VertexSummary.offlinePrimaryVerticesSummary = cms.PSet(
    src=cms.InputTag("offlineSlimmedPrimaryVertices"))


### TODO: 'good' collection obsolete -> pending review
##process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(
##    src=cms.InputTag("goodOfflinePrimaryVertices"))

# add to Kappa 'PileupDensity': pileup energy density ('rho')
process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(
    src=cms.InputTag("fixedGridRhoFastjetAll")
)

# -- calculate quantities related to the event weights/count
process.load("Kappa.Producers.EventWeightCountProducer_cff")
if not options.isData:
    # if MC, set some flags
    process.nEventsTotal.isMC = cms.bool(True)
    process.nNegEventsTotal.isMC = cms.bool(True)
    process.nEventsFiltered.isMC = cms.bool(True)
    process.nNegEventsFiltered.isMC = cms.bool(True)
process.path.insert(0, process.nEventsTotal + process.nNegEventsTotal)
process.path.insert(-1, process.nEventsFiltered + process.nNegEventsFiltered)

# make Kappa branch 'FilterSummary' active
process.kappaTuple.active += cms.vstring('FilterSummary')

#########################
# Testing and Debugging #
#########################

# write out original collections to a slimmed miniAOD file
if options.edmOut:  # only for testing
    process.writeOutMiniAOD = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string(options.edmOut),
        outputCommands = cms.untracked.vstring(
            [
                'drop *',
                'keep *_ak4PFJets_*_*',
                'keep *_ak4PFJetsCHS_*_*',
                'keep patJets_flavUpdatedPatJetsAK*_*_*',
                'keep patJets_selectedPatJetsAK*_*_*',
                'keep *_slimmedElectrons_*_*',
                'keep *_calibratedPatElectrons_*_*',
                'keep *_selectedElectrons_*_*',
                # add other collections you want to write out here
            ]
        )
    )
    process.endpath *= process.writeOutMiniAOD


# for debugging: dump entire cmsRun python configuration
if options.dumpPythonAndExit:
    with open('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', 'w') as f:
            f.write(process.dumpPython())
    sys.exit(1)


# final information:
print "-------- CONFIGURATION ----------"
print ""
print "CMSSW producers:"
for p in str(process.path).split('+'):
    print "  %s" % p
print ""
print "CMSSW endpath producers:"
for p in str(process.endpath).split('+'):
    print "  %s" % p
print ""
print "Kappa producers:"
for p in sorted(process.kappaTuple.active):
    print "  %s" % p
print "---------------------------------"
