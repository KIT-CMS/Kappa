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
                default='fixmeifUcan',
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

# CMSSW 94X -> trigger object is 'slimmedPatTrigger'
process.kappaTuple.TriggerObjectStandalone.triggerObjects = cms.PSet(
    src=cms.InputTag("slimmedPatTrigger")
)

# read in trigger results from 'HLT' process
process.kappaTuple.Info.hltSource = cms.InputTag("TriggerResults", "", "HLT")

# set flag to prevent KAPPA error if process name is something other than 'HLT'
process.kappaTuple.Info.overrideHLTCheck = cms.untracked.bool(True)

# read in MET filter bits from RECO/PAT trigger results (use RECO for PromptReco)
process.kappaTuple.TriggerObjectStandalone.metfilterbits = cms.InputTag("TriggerResults", "", "RECO")


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
process.kappaTuple.Muons.minPt = 8.0
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
process.kappaTuple.Electrons.srcIds = cms.string("standalone");
process.kappaTuple.Electrons.ids = cms.VInputTag(
    # cut-based VIDs
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-veto",
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-loose",
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-medium",
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V1-tight",
    #
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-loose",
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-medium",
    "egmGsfElectronIDs:cutBasedElectronID-Fall17-94X-V2-tight",
)


# -- call the default KAPPA electron setup routine
setupElectrons(process, "slimmedElectrons", id_modules=['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff', 'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff'])

# -- add electron ID task to KAPPA Task
process.kappaTask.add(process.egmGsfElectronIDTask)


######################
# Configure JTB Jets #
######################

# jet collections obtained with 'JetToolbox' CMSSW module:
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetToolbox
from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox

# -- set up jet toolbox jets

jtb_sequence_name = 'sequence'

# go through all combinations of jet radius and PU subtraction algorithms
for _jet_algo_radius in ('ak4', 'ak8'):
    # for _jet_algo_radius in ('ak4',):
    for _PU_method in ("", "CHS", "Puppi"):
        _seq_name = "{}{}{}".format(jtb_sequence_name, _jet_algo_radius, _PU_method)

        # calculate and evaluate PUJetID only for ak4CHS jets (TODO: do we need this?)
        _do_PUJetID = False
        _do_CTagger = False
        if _jet_algo_radius == 'ak4' and _PU_method == "CHS":
            _do_PUJetID = True
            _do_CTagger = True
            process.kappaTuple.PatJets.ids = cms.vstring(
                "AK4PFCHSpileupJetIdEvaluator:fullDiscriminant",  # Tell KAPPA to get PuJetID from JetToolBox instead of slimmedJets
                "AK4PFCHSpileupJetIdEvaluator:cutbasedId",
                "AK4PFCHSpileupJetIdEvaluator:fullId",
                "QGTaggerAK4PFCHS:qgLikelihood",  # Tell KAPPA to extract qg-tags
                "pfCombinedInclusiveSecondaryVertexV2BJetTags",  # Tell KAPPA to extract b-tags
                "pfCombinedCvsLJetTags",  # Tell KAPPA to extract c-tags 
                "pfCombinedCvsBJetTags",
            )
        # create jet sequence with jet toolbox
        jetToolbox(process,
                   _jet_algo_radius,
                   _seq_name,
                   'out',
                   # miniAOD=True,
                   dataTier='miniAOD',
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
                   addPUJetID=_do_PUJetID,
                   addQGTagger=_do_CTagger,
                   verbosity=3)

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


# -- activate KAPPA producers

# PatJet producer
process.kappaTuple.active += cms.vstring('PatJets')


# GenJets (=='LV') producer
if not options.isData:
    process.kappaTuple.active += cms.vstring('LV')
    # write out 'ak*GenJetsNoNu' four-vectors
    process.kappaTuple.LV.ak4GenJetsNoNu = cms.PSet(src=cms.InputTag("ak4GenJetsNoNu"))
    process.kappaTuple.LV.ak8GenJetsNoNu = cms.PSet(src=cms.InputTag("ak8GenJetsNoNu"))

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

from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

## create collection of PF candidates likely coming from the primary vertex
#process.packedPFCandidatesCHSNotFromPV = cms.EDFilter('CandPtrSelector',
#    src = cms.InputTag('packedPFCandidates'),
#    cut = cms.string('fromPV==0')  # only loose selection (0)
#)
#process.path *= (process.packedPFCandidatesCHSNotFromPV)
#process.packedPFCandidatesCHS = cms.EDFilter('CandPtrSelector',
#    src = cms.InputTag('packedPFCandidates'),
#    cut = cms.string('fromPV() > 0')  # only loose selection (0)
#)
#process.path *= (process.packedPFCandidatesCHS)

# -- start of MET recipe

# the following lines are for default MET for Type1 corrections

# If you only want to re-correct for JEC and get the proper uncertainties for the default MET
runMetCorAndUncFromMiniAOD(process,
                           isData=options.isData,
                           # pfCandColl='packedPFCandidatesCHS',
                           # recoMetFromPFCs=True
                           )

# TODO: check if the JetToolBox does this already
## If you would like to re-cluster both jets and met and get the proper uncertainties
#runMetCorAndUncFromMiniAOD(process,
#                           isData=options.isData,
#                           pfCandColl=cms.InputTag("packedPFCandidates"),
#                           recoMetFromPFCs=True,
#                           CHS = True, # this is an important step and determines what type of jets to be reclustered
#                           reclusterJets = True
#                           )

#process.kappaTuple.active += cms.vstring('packedPFCandidates')
#process.kappaTuple.packedPFCandidates.pfCandidates = cms.PSet(src=cms.InputTag("packedPFCandidates"))

# wire CHS MET to new collection from the "KAPPA" process
process.kappaTuple.PatMET.metCHS = cms.PSet(src=cms.InputTag("slimmedMETs"),
                                            uncorrected=cms.bool(True))
if not options.isData:
    # MC: wire PF MET to older collection from the PAT process
    process.kappaTuple.PatMET.metPF = cms.PSet(src=cms.InputTag("slimmedMETs", "", "PAT"),
                                               uncorrected=cms.bool(True))
else:
    # no PAT process in data -> use RECO
    # process.kappaTuple.PatMET.metPF = cms.PSet(src=cms.InputTag("slimmedMETs", "", "RECO"),
    #                                            uncorrected=cms.bool(True))
    process.kappaTuple.PatMET.metPF = cms.PSet(src=cms.InputTag("slimmedMETs"),
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

process.kappaTuple.VertexSummary.goodOfflinePrimaryVerticesSummary = cms.PSet(
    src=cms.InputTag("goodOfflinePrimaryVertices"))

# add to Kappa 'PileupDensity': pileup energy density ('rho')
process.kappaTuple.PileupDensity.pileupDensity = cms.PSet(
    src=cms.InputTag("fixedGridRhoFastjetAll")
)


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

# for debugging: dump entire cmsRun python configuration
if options.dumpPython:
    with open('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', 'w') as f:
            f.write(process.dumpPython())
    # sys.exit(1)

def _print_path_info(path):
    assert isinstance(path, cms.Path) or isinstance(path, cms.EndPath)

    for _module in str(path._seq).split(','):
        print "  - {}".format(_module)
    print ""
    if path._tasks:
        print "  Associated tasks"
        print "  ----------------"
        for _task in path._tasks:
            print "    - {}:".format(_task.label())
            for _module in str(_task).split(', '):
                print "      - {}".format(_module)
        print ""

# final information:
print ""
print "-------- CONFIGURATION ----------"
print ""
print "CMSSW path"
print "=========="
_print_path_info(process.path)

print "CMSSW endpath"
print "============="
_print_path_info(process.endpath)

print "Kappa producers:"
for p in sorted(process.kappaTuple.active):
    print "  %s" % p
print "---------------------------------"
