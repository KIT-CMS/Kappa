# Class Listing {#classes}

Overview of the classes of the Kappa data format

Instructions: Edit only this file (classes.md) by hand.
This file is interpreted by doxygen as markdown and shown in the docs.
Each class must be on a separate line starting with a hyphen or plus.
The occurance of the class names in all other places
is then automatically adapted by running `classes.UP`.


## Basic ROOT objects ################################

ROOT Lorentz vectors in float and double precision
(the - sign tells classes.UP not to put these into Kappa.h and KDebug.h)

- RMFLV
- RMFLV_Store
- RMDLV
- RMDLV_Store


## Event tree classes ################################

These classes can be filled for each event in the skim.
Plural forms are standard vectors of the classes with singular class names.

### Event info
+ KEventInfo
+ KGenEventInfo

### Particles and per event objects
+ KBasicJet              KBasicJets
+ KBasicTau              KBasicTaus
+ KBeamSpot              KBeamSpots
+ KCaloJet               KCaloJets
+ KElectron              KElectrons
+ KLV                    KLVs
+ KGenJet                KGenJets
+ KGenParticle           KGenParticles
+ KLHEParticle           KLHEParticles
+ KGenPhoton             KGenPhotons
+ KGenTau                KGenTaus
+ KHit                   KHits
+ KJet                   KJets
+ KL1Muon                KL1Muons
+ KLepton                KLeptons
+ KLeptonPair            KLeptonPairs
+ KMET                   KMETs
+ KMuon                  KMuons
+ KMuonTriggerCandidate  KMuonTriggerCandidates
+ KParticle              KParticles
+ KPFCandidate           KPFCandidates
+ KPhoton                KPhotons
+ KPileupDensity
+ KTau                   KTaus
+ KExtendedTau           KExtendedTaus
+ KTaupairVerticesMap    KTaupairVerticesMaps
+ KTrack                 KTracks
+ KTriggerObjects
+ KVertex                KVertices
+ KRefitVertex           KRefitVertices

### Summaries
+ KFilterSummary
+ KHCALNoiseSummary
+ KTrackSummary
+ KVertexSummary


## Lumi tree classes #################################

These classes should be filled once per lumi section.

### Lumi section info
+ KLumiInfo
+ KGenRunInfo
+ KDataLumiInfo

### Object metadata
+ KElectronMetadata
+ KFilterMetadata
+ KMuonMetadata
+ KGenEventInfoMetadata
+ KJetMetadata
+ KTauMetadata
+ KTriggerObjectMetadata

### Provenance information
+ KProvenance
