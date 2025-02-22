# Kappa test: CMSSW 10.6.X

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
                default='106X_dataRun2_v37',
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
register_option('dumpPython',
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
    options.dumpPython = False
    options.kappaVerbosity = 0
    options.reportEvery = int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]


########################
# Create CMSSW Process #
########################

from Configuration.StandardSequences.Eras import eras

process = cms.Process("KAPPA", eras.Run2_2017)

# some CMSSW analysis modules will be added to the path
process.path = cms.Path()

# most CMSSW analysis modules will be added to a task (for unscheduled execution)
process.kappaTask = cms.Task()

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
print("\n----- CMSSW configuration -----")
print("input:          ", (process.source.fileNames[0] if len(process.source.fileNames) else ""), ("... (%d files)" % len(process.source.fileNames) if len(process.source.fileNames) > 1 else ""))
print("file type:      ", "miniAOD")
print("data:           ", options.isData)
print("output:         ", options.outputFile)
print("global tag:     ", options.globalTag)
print("max events:     ", (str(process.maxEvents.input)[20:-1]))
print("cmssw version:  ", os.environ["CMSSW_VERSION"])
print("---------------------------------\n")


#################
# CMSSW modules #
#################

# -- CMSSW message logger
process.load("FWCore.MessageLogger.MessageLogger_cfi")
#process.MessageLogger = cms.Service("MessageLogger")
process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery
process.MessageLogger.default = cms.untracked.PSet(
    ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5))
)

# -- CMSSW geometry and detector conditions
# (These are needed for some PAT tuple production steps)
process.load("Configuration.Geometry.GeometryRecoDB_cff")  # new phase-1 geometry
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

# Gen settings for Herwig samples/non-standard MC
# Empty Parton Shower weights
process.kappaTuple.Info.genWeightNames = cms.PSet()

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

process.kappaTuple.TriggerObjectStandalone.triggerObjects = cms.PSet(
    src=cms.InputTag("slimmedPatTrigger")
)

# read in trigger results from 'HLT' process
process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")

# set flag to prevent KAPPA error if process name is something other than 'HLT'
process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)

# read in MET filter bits from PAT process
process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "PAT")
#process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "KAPPA")


# write out HLT information for trigger names matching regex
process.kappaTuple.Info.hltWhitelist = cms.vstring(
    # HLT regex selection can be tested at https://regex101.com (with gm options)
    # single muon triggers, e.g. HLT_Mu50_v1
    "^HLT_(Iso)?(Tk)?Mu[0-9]+(_eta2p1|_TrkIsoVVL)?_v[0-9]+$",
    # double muon triggers, e.g. HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v1
    "^HLT_Mu[0-9]+(_TrkIsoVVL)?_(Tk)?Mu[0-9]+(_TrkIsoVVL)?(_DZ)?(_Mass[0-9p]+)?_v[0-9]+$",
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
    )
    # need path to effectively veto affected events (even in unscheduled mode)
    process.path *= (process.pfFilter)


#################
# PF Candidates #
#################

process.kappaTuple.active += cms.vstring('packedPFCandidates')
process.kappaTuple.packedPFCandidates.pfCandidates = cms.PSet(
    src=cms.InputTag("packedPFCandidates")
)

####################
# Primary Vertices #
####################

# -- filter PV collection to obtain "good" offline primary vertices
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector
process.goodOfflinePrimaryVertices = cms.EDFilter(
    'PrimaryVertexObjectFilter',
    filterParams=pvSelector.clone(maxZ = 24.0),  # ndof >= 4, rho <= 2
    src=cms.InputTag('offlineSlimmedPrimaryVertices'),
)

# add good PV producer to KAPPA task
process.kappaTask.add(process.goodOfflinePrimaryVertices)


###################
# Configure Muons #
###################

# -- load default Kappa config for skimming muons
process.load("Kappa.Skimming.KMuons_miniAOD_cff")
process.kappaTuple.active += cms.vstring('Muons')

# -- set basic skimming parameters
process.kappaTuple.Muons.minPt = 5.0
process.kappaTuple.Muons.muons.src = cms.InputTag("slimmedMuons")
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


'''
#######################
# Configure Electrons #
#######################

# from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
# setupEgammaPostRecoSeq(process,
#                        runVID=False, #saves CPU time by not needlessly re-running VID, if you want the Fall17V2 IDs, set this to True or remove (default is True)
#                        era='2017-UL')    
# 
# process.path *= process.egammaPostRecoSeq

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
process.kappaTuple.Electrons.srcIds = cms.string("pat")
process.kappaTuple.Electrons.ids = cms.VInputTag(
    # cut-based VIDs
    cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-veto"),
    cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-loose"),
    cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-medium"),
    cms.InputTag("egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-tight"),
    # MVA IDs
    cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp90"),
    cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wp80"),
    cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-noIso-V2-wpLoose"),
    cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp90"),
    cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wp80"),
    cms.InputTag("egmGsfElectronIDs:mvaEleID-Fall17-iso-V2-wpLoose"),
)

# -- electron corrections
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


# -- call the default KAPPA electron setup routine
# setupElectrons(process, "slimmedElectrons", id_modules=['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff', 'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff'])

# -- add electron ID task to KAPPA Task
# process.kappaTask.add(process.egmGsfElectronIDTask)
'''

######################
# Configure JTB Jets #
######################

# jet collections obtained with 'JetToolbox' CMSSW module:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox

# -- set basic skimming parameters
process.kappaTuple.Jets.minPt = 5.0

# -- set up jet toolbox jets
jtb_sequence_name = 'sequence'

# go through all combinations of jet radius and PU subtraction algorithms
for _jet_algo_radius in ('ak4', 'ak8'):
    for _PU_method in ("CHS", "Puppi"):
        _seq_name = "{}{}{}".format(jtb_sequence_name, _jet_algo_radius, _PU_method)
        JETCorrPayload = (_jet_algo_radius+"PF"+_PU_method).upper()
        # create jet sequence with jet toolbox
        jetToolbox(process,
                   _jet_algo_radius,
                   _seq_name,
                   'noOutput',
                   runOnMC=not options.isData,
                   # JETCorrPayload=JETCorrPayload,
                   JETCorrPayload="None",  # do *not* correct jets with JEC
                   PUMethod=_PU_method,
                   verbosity=3)
        # Completetly re-derive PileUpJetID, broken otherwise
        if _jet_algo_radius == 'ak4' and _PU_method == "CHS":
            from RecoJets.JetProducers.PileupJetID_cfi import pileupJetId, _chsalgos_106X_UL17
            updatedPileUpJetID = pileupJetId.clone(
                jets=cms.InputTag("ak4PFJetsCHS"),
                inputIsCorrected=False,
                applyJec=True,
                vertexes=cms.InputTag("offlineSlimmedPrimaryVertices"),
                algos=cms.VPSet(_chsalgos_106X_UL17),
            )
            from PhysicsTools.PatAlgos.tools.helpers import getPatAlgosToolsTask, addToProcessAndTask
            task = getPatAlgosToolsTask(process)
            addToProcessAndTask("pileupJetIdUpdated", updatedPileUpJetID, process, task)
            getattr(process, "patJetsAK4PFCHS").userData.userFloats.src += [
                "pileupJetIdUpdated:fullDiscriminant",
            ]
            getattr(process, "patJetsAK4PFCHS").userData.userInts.src += [
                "pileupJetIdUpdated:cutbasedId",
                "pileupJetIdUpdated:fullId",
            ]

            # Add PuJetID to Kappa
            process.kappaTuple.PatJets.ids = cms.vstring(
                "pileupJetIdUpdated:fullDiscriminant",
                "pileupJetIdUpdated:cutbasedId",
                "pileupJetIdUpdated:fullId",
            )

process.kappaTuple.PatJets.ak4PFJetsCHS = cms.PSet(src=cms.InputTag("patJetsAK4PFCHS"))
process.kappaTuple.PatJets.ak4PFJetsPuppi = cms.PSet(src=cms.InputTag("patJetsAK4PFPuppi"))
process.kappaTuple.PatJets.ak8PFJetsCHS = cms.PSet(src=cms.InputTag("patJetsAK8PFCHS"))
process.kappaTuple.PatJets.ak8PFJetsPuppi = cms.PSet(src=cms.InputTag("patJetsAK8PFPuppi"))

"""
######################
# Configure PAT Jets #
######################

# go through all combinations of jet radius and PU subtraction algorithms
for _jet_radius in (4, 8):
    for _PU_method in ("", "CHS", "Puppi"):
        _jet_collection_name = "ak%dPFJets%s" % (_jet_radius, _PU_method)
        _patJet_collection_name = "AK%dPF%s" % (_jet_radius, _PU_method)

        # add KAPPA PatJet config to KAPPA Tuple
        setattr(process.kappaTuple.PatJets,
            _jet_collection_name,
            cms.PSet(
                src = cms.InputTag('selectedPatJets'+_patJet_collection_name)
            )
        )

    # GenJets
    if not options.isData:
        _jet_collection_name = "ak%sGenJetsNoNu" % (_jet_radius)
        # GenJets are just KLVs: add collection to whitelist
        process.kappaTuple.LV.whitelist += cms.vstring(_jet_collection_name)
"""

# -- activate KAPPA producers

# PatJet producer
process.kappaTuple.active += cms.vstring('PatJets')

# GenJets (=='LV') producer
if not options.isData:
    process.kappaTuple.active += cms.vstring('LV')
    # write out 'ak*GenJetsNoNu' four-vectors
    #process.kappaTuple.LV.ak4GenJetsNoNu = cms.PSet(src=cms.InputTag("ak4GenJetsNoNu"))
    #process.kappaTuple.LV.ak8GenJetsNoNu = cms.PSet(src=cms.InputTag("ak8GenJetsNoNu"))
    process.kappaTuple.LV.ak4GenJets = cms.PSet(src=cms.InputTag("slimmedGenJets"))
    process.kappaTuple.LV.ak8GenJets = cms.PSet(src=cms.InputTag("slimmedGenJetsAK8"))

#######################
# PileupDensity (rho) #
#######################

process.kappaTuple.active += cms.vstring('PileupDensity')
process.kappaTuple.PileupDensity.whitelist = cms.vstring("fixedGridRhoFastjetAll")
process.kappaTuple.PileupDensity.rename = cms.vstring("fixedGridRhoFastjetAll => pileupDensity")



#################
# Configure MET #
#################

# official Prescription for calculating corrections and uncertainties on Missing Transverse Energy (MET):
# https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription#Instructions_for_8_0_X_X_26_patc

#from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

## create collection of PF candidates likely coming from the primary vertex
#process.packedPFCandidatesCHSNotFromPV = cms.EDFilter('CandPtrSelector',
#    src = cms.InputTag('packedPFCandidates'),
#    cut = cms.string('fromPV==0')  # only loose selection (0)
#)
#
#process.packedPFCandidatesCHS = cms.EDFilter('CandPtrSelector',
#    src = cms.InputTag('packedPFCandidates'),
#    cut = cms.string('fromPV() > 0')  # only loose selection (0)
#)


# re-correct MET for JEC and get the proper uncertainties
# Note: this only affects the default (i.e. Type1-corrected) MET.
# Since we only write out the raw MET, this line likely has no effect.
#runMetCorAndUncFromMiniAOD(process, isData=options.isData)

# -- end of MET recipe

# wire miniAOD METs to collection from the "KAPPA" process
process.kappaTuple.PatMET.metPF = cms.PSet(src=cms.InputTag("slimmedMETs"), correctionLevel=cms.string('Raw'))
process.kappaTuple.PatMET.metCHS = cms.PSet(src=cms.InputTag("slimmedMETs"), correctionLevel=cms.string('RawChs'))
process.kappaTuple.PatMET.metPuppi = cms.PSet(src=cms.InputTag("slimmedMETsPuppi"), correctionLevel=cms.string('Raw'))

# -- activate KAPPA producers
process.kappaTuple.active += cms.vstring('PatMET')

# NOTE: has not effect by itself -> need to add to TriggerResults object
#       luckily, it is already present for MiniAODv2
## -- add Filter manually...
#process.load('RecoMET.METFilters.BadPFMuonDzFilter_cfi')


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

process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(
    src=cms.InputTag("goodOfflinePrimaryVertices"))

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

# from FWCore.ParameterSet.Utilities import convertToUnscheduled
# process=convertToUnscheduled(process)

# write out original collections to a slimmed miniAOD file
if options.edmOut:  # only for testing
    process.writeOutMiniAOD = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string(options.edmOut),
        outputCommands = cms.untracked.vstring(
            [
                'drop *',
                'keep *_ak4PFJets_*_*',
                'keep *_slimmedMETs_*_*',
                'keep *_selectedPatJetsAK4PF_*_*',
                'keep *_ak4PFJetsCHS_*_*',
                'keep *_selectedPatJetsAK4PFCHS_*_*',
                'keep *_chs_*_*',
                'keep *_packedPFCandidates_*_*',
                'keep *_packedPFCandidatesCHSNotFromPV_*_*',
                'keep *_packedPFCandidatesCHS_*_*',
                # add other collections you want to write out here
            ]
        )
    )
    process.endpath *= process.writeOutMiniAOD


# associate all modules in kappaTask to the end path
process.endpath.associate(process.kappaTask)
process.endpath.associate(process.patAlgosToolsTask)

# for debugging: dump entire cmsRun python configuration
if options.dumpPython:
    with open('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', 'w') as f:
            f.write(process.dumpPython())

def _print_path_info(path):
    assert isinstance(path, cms.Path) or isinstance(path, cms.EndPath)

    for _module in str(path._seq).split(','):
        print("  - {}".format(_module))
    print("")
    if path._tasks:
        print("  Associated tasks")
        print("  ----------------")
        for _task in path._tasks:
            print("    - {}:".format(_task.label()))
            for _module in str(_task).split(', '):
                print("      - {}".format(_module))
        print("")

# final information:
print("")
print("-------- CONFIGURATION ----------")
print("")
print("CMSSW path")
print("==========")
_print_path_info(process.path)

print("CMSSW endpath")
print("=============")
_print_path_info(process.endpath)

print("Kappa producers:")
for p in sorted(process.kappaTuple.active):
    print("  %s" % p)
print("---------------------------------")
