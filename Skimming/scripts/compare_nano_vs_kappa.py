import ROOT as r
import argparse

parser = argparse.ArgumentParser(description='Script for comparison of Kappa skims with NanoAOD')
parser.add_argument('--nanofile', dest='nanofile',required=True,help='NanoAOD File for comparison')
parser.add_argument('--kappafile', dest='kappafile',required=True,help='Kappa File for comparison')
parser.add_argument('--events', dest='events',type=int,nargs='+',required=True,help='Events common between NanoAOD and Kappa files to be compared')
parser.add_argument('--object', dest='object',choices=['Muon','Tau','Electron','Jet','MET','General'],required=True,help='Physics object to be compared')
parser.add_argument('--year', dest='year',type=int,choices=[2016,2017,2018],required=True,help='Year of data-taking')

args = parser.parse_args()
events = args.events
active_object = args.object

nanofile = r.TFile.Open(args.nanofile,"read")
nanotree = nanofile.Get("Events").CopyTree(" || ".join(["event == %s"%str(e) for e in events]))

print "Nano:"
print "number of matched events:",nanotree.GetEntries()
for i,entry in enumerate(nanotree):
    print "\tevent", entry.event
    if active_object == "Electron":
        print "\tnElectron", entry.nElectron
        for j,(dxy,dz,convVeto,lostHits,pt,eta,phi,m,ID,Iso) in enumerate(zip(
            entry.Electron_dxy,
            entry.Electron_dz,
            entry.Electron_convVeto,
            entry.Electron_lostHits,
            entry.Electron_pt,
            entry.Electron_eta,
            entry.Electron_phi,
            entry.Electron_mass,
            entry.Electron_mvaFall17V2noIso,
            entry.Electron_pfRelIso03_all
        )):
            print "\t\tElectron nr. %s pt,eta,phi,m ="%j,pt,eta,phi,m
            print "\t\t\tId discriminator (NoIso Fall17V2)",ID
            print "\t\t\trelative Rho-corrected isolation",Iso
            print "\t\t\tImpact parameter",dxy, dz
            print "\t\t\tNumber of lost hits",ord(lostHits)
            print "\t\t\tpassing conversion veto?",convVeto
            print "\n"
    if active_object == "Muon":
        print "\tnMuon", entry.nMuon
        for j,(dxy,dz,pt,eta,phi,m,ID,Iso) in enumerate(zip(
            entry.Muon_dxy,
            entry.Muon_dz,
            entry.Muon_pt,
            entry.Muon_eta,
            entry.Muon_phi,
            entry.Muon_mass,
            entry.Muon_mediumId,
            entry.Muon_pfRelIso04_all,
        )):
            print "\t\tMuon nr. %s pt,eta,phi,m ="%j,pt,eta,phi,m
            print "\t\t\tImpact parameter",dxy, dz
            print "\t\t\tMedium ID and Iso",ID, Iso
    if active_object == "Tau":
        print "\tnTau", entry.nTau
        for j,(dz,pt,eta,phi,m,reltkPt,dm,dmf,dmfnew,Id,aE) in enumerate(zip(
            entry.Tau_dz,
            entry.Tau_pt,
            entry.Tau_eta,
            entry.Tau_phi,
            entry.Tau_mass,
            entry.Tau_leadTkPtOverTauPt,
            entry.Tau_decayMode,
            entry.Tau_idDecayMode,
            entry.Tau_idDecayModeNewDMs,
            entry.Tau_rawMVAoldDM2017v2,
            entry.Tau_rawAntiEle,
    #        entry.Tau_rawAntiEle2018,
        )):
            print "\t\tTau nr. %s pt,eta,phi,m ="%j,pt,eta,phi,m
            print "\t\t\tImpact parameter", dz
            print "\t\t\tLeading charged track pt",reltkPt*pt
            print "\t\t\tDecayMode, old DM?, new DM? ",dm,dmf,dmfnew
            print "\t\t\tbyIsoId(2017v2) anti-e",Id,aE
    if active_object == "Jet":
        print "\tnJet", entry.nJet
        for j,(pt,eta,phi,m,deepcsv,deepflavour,ID,puID,hflav,pflav,rawF) in enumerate(zip(
            entry.Jet_pt,
            entry.Jet_eta,
            entry.Jet_phi,
            entry.Jet_mass,
            entry.Jet_btagDeepB,
            entry.Jet_btagDeepFlavB,
            entry.Jet_jetId,
            entry.Jet_puId,
            entry.Jet_hadronFlavour,
            entry.Jet_partonFlavour,
            entry.Jet_rawFactor,
        )):
            print "\t\tJet nr. %s pt,eta,phi,m ="%j,pt,eta,phi,m
            print "\t\t\tDeepCSV, DeepFlavour",deepcsv,deepflavour
            print "\t\t\tJetID, pileup JetID",ID,puID
            print "\t\t\tHadron & parton flavour",hflav,pflav
            print "\t\t\trawFactor, uncorr Pt",rawF,pt*(1 -rawF)
    if active_object == "MET":
        if args.year == 2017:
            print "\tMET_pt", entry.METFixEE2017_pt
            print "\tMET_phi", entry.METFixEE2017_phi
            print "\tMET_sumEt", entry.METFixEE2017_sumEt
        else:
            print "\tMET_pt", entry.MET_pt
            print "\tMET_phi", entry.MET_phi
            print "\tMET_sumEt", entry.MET_sumEt
        print "\tPuppiMET_pt", entry.PuppiMET_pt
        print "\tPuppiMET_phi", entry.PuppiMET_phi
        print "\tPuppiMET_sumEt", entry.PuppiMET_sumEt
    if active_object == "General":
        #print "\tL1PreFiringWeight", entry.L1PreFiringWeight_Nom
        pass
nanofile.Close()

kappafile = r.TFile.Open(args.kappafile,"read")
kappatree = kappafile.Get("Events").CopyTree(" || ".join(["nEvent == %s"%str(e) for e in events]))
kappalumitree = kappafile.Get("Lumis")

lumis = [l for l in kappalumitree]

def getEffectiveArea(eta):
    etaBins = [0.0,1.0,1.479,2.0,2.2,2.3,2.4,2.5]
    eAs = [0.1440,0.1562,0.1032,0.0859,0.1116,0.1321,0.1654]
    for i in range(len(eAs)):
        if abs(eta) >= etaBins[i] and abs(eta) < etaBins[i+1]:
            return eAs[i]
    return 0.0

print "Kappa:"
print "number of matched events:",kappatree.GetEntries()
for i,entry in enumerate(kappatree):
    print "\tevent", entry.eventInfo.nEvent
    rho = entry.pileupDensity.rho
    if active_object == "Electron":
        print "\tnElectron",entry.electrons.size()
        for j,e in enumerate(entry.electrons):
            print "\t\tElectron nr. %s pt,eta,phi,m ="%j,e.p4.Pt(),e.p4.Eta(),e.p4.Phi(),e.p4.M()
            e_correction = e.getId("electronCorrection:ecalTrkEnergyPostCorr",lumis[0].electronMetadata)/e.p4.E()
            print "\t\t\tEnergy correction:",e_correction
            correctedP4 = e.p4 * e_correction
            print "\t\t\tCorrected pt,eta,phi,m =",correctedP4.Pt(),correctedP4.Eta(),correctedP4.Phi(),correctedP4.M() # used in NanoAOD
            ElectronId = e.getId("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Fall17NoIsoV2Values",lumis[0].electronMetadata)
            print "\t\t\tId discriminator (NoIso Fall17V2)",ElectronId
            relRhoIso = max(e.sumChargedHadronPt + max(e.sumNeutralHadronEt + e.sumPhotonEt - rho*getEffectiveArea(e.superclusterPosition.Eta()),0.0), 0.0)/e.p4.Pt() # use UNCORRECTED Pt to compute Isolation
            print "\t\t\trelative Rho-corrected isolation",relRhoIso
            print "\t\t\tImpact parameter",e.dxy, e.dz
            print "\t\t\tNumber of lost hits",e.expectedMissingInnerHits
            print "\t\t\tpassing conversion veto?",not (ord(e.electronType) & (1 << r.KElectronType.hasConversionMatch))
    if active_object == "Muon":
        print "\tnMuon",entry.muons.size()
        for j,m in enumerate(entry.muons):
            if m.p4.Pt() > 3 and m.idLoose():
                print "\t\tMuon nr. %s pt,eta,phi,m ="%j,m.p4.Pt(),m.p4.Eta(),m.p4.Phi(),m.p4.M()
                print "\t\t\tImpact parameter",m.dxy, m.dz
                print "\t\t\tMedium ID and Iso",m.idMedium(), (m.sumChargedHadronPtR04 + max(0.0, m.sumNeutralHadronEtR04 + m.sumPhotonEtR04 - 0.5*m.sumPUPtR04))/m.p4.Pt()
    if active_object == "Tau":
        print "\tnTau", entry.taus.size()
        for j,t in enumerate(entry.taus):
            print "\t\tTau nr. %s pt,eta,phi,m ="%j,t.p4.Pt(),t.p4.Eta(),t.p4.Phi(),t.p4.M()
            print "\t\t\tImpact parameter", t.dz
            print "\t\t\tLeading charged track pt",t.track.p4.Pt()
            print "\t\t\tDecayMode, old DM?, new DM? ",t.decayMode,t.getDiscriminator("decayModeFinding",lumis[0].taus), t.getDiscriminator("decayModeFindingNewDMs",lumis[0].taus)
            print "\t\t\tbyIsoId(2017v2) anti-e",t.getDiscriminator("byIsolationMVArun2017v2DBoldDMwLTraw2017",lumis[0].taus), t.getDiscriminator("againstElectronMVA6Raw",lumis[0].taus)
    if active_object == "Jet":
        print "\tnJet", entry.ak4PF.size()
        for k,j in enumerate(entry.ak4PF):
            if j.p4.Pt() > 15:
                print "\t\tJet nr. %s pt,eta,phi,m ="%k,j.p4.Pt(),j.p4.Eta(),j.p4.Phi(),j.p4.M()
                deepcsv = j.getTag("pfDeepCSVJetTagsprobb+pfDeepCSVJetTagsprobbb",lumis[0].jetMetadata,False)
                deepflavour = j.getTag("pfDeepFlavourJetTagsprobb+pfDeepFlavourJetTagsprobbb+pfDeepFlavourJetTagsproblepb",lumis[0].jetMetadata,False)
                puID = j.getTag("pileupJetIdUpdatedfullId",lumis[0].jetMetadata,False)
                puIDOld = j.getTag("pileupJetIdfullId",lumis[0].jetMetadata,False)
                puIDValue = j.getTag("pileupJetIdUpdatedfullDiscriminant",lumis[0].jetMetadata,False)
                puIDOldValue = j.getTag("pileupJetIdfullDiscriminant",lumis[0].jetMetadata,False)
                looseJetId = j.getTag("looseJetId",lumis[0].jetMetadata,False)
                tightJetId = j.getTag("tightJetId",lumis[0].jetMetadata,False)
                tightJetIdLepVeto = j.getTag("tightJetIdLepVeto",lumis[0].jetMetadata,False)
                print "\t\t\tDeepCSV, DeepFlavour",deepcsv,deepflavour
                print "\t\t\tpileup JetID, pileup JetID value, pileup JetID old, pileup JetID old value ",puID,puIDValue,puIDOld,puIDOldValue
                print "\t\t\tJetID loose, tight, tight(LepVeto)", looseJetId, tightJetId, tightJetIdLepVeto
                print "\t\t\tHadron & parton flavour",j.hadronFlavour,j.partonFlavour
                print "\t\t\trawFactor,  uncorrP4", (1- j.jecFactor), j.uncorrectedP4.Pt(), j.uncorrectedP4.Eta(), j.uncorrectedP4.Phi(), j.uncorrectedP4.M()
    if active_object == "MET":
        print "\tMET_pt", entry.met.p4.Pt()
        print "\tMET_phi", entry.met.p4.Phi()
        print "\tMET_sumEt", entry.met.sumEt
        print "\tPuppiMET_pt", entry.metPuppi.p4.Pt()
        print "\tPuppiMET_phi", entry.metPuppi.p4.Phi()
        print "\tPuppiMET_sumEt", entry.metPuppi.sumEt
    if active_object == "General":
        #print "\tL1PreFiringWeight", entry.L1PreFiringWeight_Nom
        pass
kappafile.Close()
