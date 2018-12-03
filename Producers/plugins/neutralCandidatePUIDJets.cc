#ifndef JMEValidator_neutralCandidatePUIDJets_h
#define JMEValidator_neutralCandidatePUIDJets_h


#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "PhysicsTools/SelectorUtils/interface/PFJetIDSelectionFunctor.h"
#include "DataFormats/JetReco/interface/PileupJetIdentifier.h" 
#include "DataFormats/Common/interface/View.h"
#include "DataFormats/PatCandidates/interface/PackedCandidate.h"

#include <iostream>


class neutralCandidatePUIDJets : public edm::stream::EDProducer<> {

  public:
 
  neutralCandidatePUIDJets(const edm::ParameterSet&);
  ~neutralCandidatePUIDJets(){};
  
  void produce(edm::Event&, const edm::EventSetup&);

  void beginJob();
  void endJob(){};

  private:

  edm::InputTag srcJets_;
  edm::InputTag srcCandidates_;
  std::string   neutralParticlesPVJets_ ;
  std::string   neutralParticlesPUJets_ ;
  std::string   neutralParticlesUnclustered_ ;
  std::string   PUJets_;
  std::string   PVJets_;
  std::string   jetPUIDWP_;

  std::string   jetPUIDMapLabel_ ;

  PileupJetIdentifier::Id jetIdSelection_;

  edm::EDGetTokenT<pat::JetCollection> srcJetsToken_;
  edm::EDGetTokenT<reco::CandidateView> srcCandidatesToken_;

  static std::string   jetPUIDNameLabel_ ;
  static bool stringInJetCollection_ ;

  float jetPUIDCut_ [4][3];

};
#endif

bool neutralCandidatePUIDJets::stringInJetCollection_ = false;
std::string neutralCandidatePUIDJets::jetPUIDNameLabel_ = "";

neutralCandidatePUIDJets::neutralCandidatePUIDJets(const edm::ParameterSet& iConfig){

  // new PU Jet ID cuts medium
  // https://indico.cern.ch/event/502737/contribution/3/attachments/1234291/1816811/PileupJetID_76X.pdf
  jetPUIDCut_[0][0] = -0.61; jetPUIDCut_[0][1] = -0.52; jetPUIDCut_[0][2] = -0.40; jetPUIDCut_[0][3] = -0.36;
  jetPUIDCut_[1][0] = -0.61; jetPUIDCut_[1][1] = -0.52; jetPUIDCut_[1][2] = -0.40; jetPUIDCut_[1][3] = -0.36;
  jetPUIDCut_[2][0] = -0.61; jetPUIDCut_[2][1] = -0.52; jetPUIDCut_[2][2] = -0.40; jetPUIDCut_[2][3] = -0.36;
  jetPUIDCut_[3][0] = -0.20; jetPUIDCut_[3][1] = -0.37; jetPUIDCut_[3][2] = -0.22; jetPUIDCut_[3][3] = -0.17;
  jetPUIDCut_[4][0] = -0.20; jetPUIDCut_[4][1] = -0.37; jetPUIDCut_[4][2] = -0.22; jetPUIDCut_[4][3] = -0.17;
   

  srcJets_ = iConfig.getParameter<edm::InputTag>("srcJets");
  srcCandidates_ = iConfig.getParameter<edm::InputTag>("srcCandidates");
  srcJetsToken_ = consumes<pat::JetCollection>(srcJets_);
  srcCandidatesToken_ = consumes<reco::CandidateView>(srcCandidates_);
  neutralParticlesPVJets_ = iConfig.getParameter<std::string>("neutralParticlesPVJetsLabel");
  neutralParticlesPUJets_ = iConfig.getParameter<std::string>("neutralParticlesPUJetsLabel");
  neutralParticlesUnclustered_ = iConfig.getParameter<std::string>("neutralParticlesUnclusteredLabel");
  PUJets_ = "PUJets";
  PVJets_ = "PVJets";

  jetPUIDWP_ = iConfig.getParameter<std::string>("jetPUDIWP");
  if(jetPUIDWP_ != "tight" and jetPUIDWP_ != "medium" and jetPUIDWP_ != "loose" and jetPUIDWP_ != "user")
    throw cms::Exception("Configuration") <<"  [neutralCandidatePUIDJets] wrong label for jetPUID working point ";

  if(jetPUIDWP_ == "tight")
    jetIdSelection_ = PileupJetIdentifier::kTight;
  else if(jetPUIDWP_ == "medium")
    jetIdSelection_ = PileupJetIdentifier::kMedium;
  else if(jetPUIDWP_ == "loose")
    jetIdSelection_ = PileupJetIdentifier::kTight;


  jetPUIDMapLabel_ = iConfig.getParameter<std::string>("jetPUIDMapLabel");  
  
  produces<edm::PtrVector<reco::Candidate> >(neutralParticlesPVJets_);
  produces<edm::PtrVector<reco::Candidate> >(neutralParticlesPUJets_);
  produces<edm::PtrVector<reco::Candidate> >(neutralParticlesUnclustered_);
  produces<pat::JetCollection>(PUJets_);
  produces<pat::JetCollection>(PVJets_);

}

void neutralCandidatePUIDJets::produce(edm::Event& iEvent, const edm::EventSetup& iSetup){

  edm::Handle<pat::JetCollection> jetCollection;
  iEvent.getByToken(srcJetsToken_,jetCollection);

  edm::Handle<reco::CandidateView> candCollection;
  iEvent.getByToken(srcCandidatesToken_,candCollection);

  auto neutralParticlesPVJets = std::make_unique<edm::PtrVector<reco::Candidate>>();
  auto neutralParticlesPUJets = std::make_unique<edm::PtrVector<reco::Candidate>>();
  auto neutralParticlesUnclustered = std::make_unique<edm::PtrVector<reco::Candidate>>();

  auto PUJets = std::make_unique<pat::JetCollection>();
  auto PVJets = std::make_unique<pat::JetCollection>();

  // loop on jets
  for(auto jet : *jetCollection){
    // look if the value is embedded in pat jets
    if(!stringInJetCollection_)
    {
      if(jetPUIDWP_ != "user")
      {
        for(size_t iJet = 0; iJet < jet.userIntNames().size(); iJet++)
        {
          if(jet.userIntNames().at(iJet).find(jetPUIDMapLabel_) != std::string::npos)
          {
            stringInJetCollection_ = true;
            jetPUIDNameLabel_ = jet.userIntNames().at(iJet);
          }
        }
        if(stringInJetCollection_ == false)
          throw cms::Exception("neutralCandidatePUIDJets")<<" user int related to jetPUID not found ";      
      }
      else
      {
        for(size_t iJet = 0; iJet < jet.userFloatNames().size(); iJet++)
        {
          if(jet.userFloatNames().at(iJet).find(jetPUIDMapLabel_) != std::string::npos)
          {
            stringInJetCollection_ = true;
            jetPUIDNameLabel_ = jet.userFloatNames().at(iJet);
          }
        }
        if(stringInJetCollection_ == false)
          throw cms::Exception("neutralCandidatePUIDJets")<<" user float related to jetPUID not found ";      	
      }
    }

    // evaluate PU JET ID
    bool isPassingPUID = false;
    if(jetPUIDWP_ != "user")
    {
      isPassingPUID = PileupJetIdentifier::passJetId(jet.userInt(jetPUIDNameLabel_), jetIdSelection_);
    }
    else
    {

      int ptBin = 0; 
      int etaBin = 0;
      if ( jet.pt() >= 10. && jet.pt() < 20. ) ptBin = 1;
      if ( jet.pt() >= 20. && jet.pt() < 30. ) ptBin = 2;
      if ( jet.pt() >= 30. && jet.pt() < 50. ) ptBin = 3;
      if ( jet.pt() >= 50.                   ) ptBin = 4;
      if ( std::abs(jet.eta()) >= 2.5  && std::abs(jet.eta()) < 2.75) etaBin = 1; 
      if ( std::abs(jet.eta()) >= 2.75 && std::abs(jet.eta()) < 3.0 ) etaBin = 2; 
      if ( std::abs(jet.eta()) >= 3.0  && std::abs(jet.eta()) < 5.0 ) etaBin = 3; 
      isPassingPUID = jet.userFloat(jetPUIDNameLabel_) > jetPUIDCut_[ptBin][etaBin] ? true : false ;

    }
    if(isPassingPUID)
      PVJets->push_back(jet);
    else
      PUJets->push_back(jet);
    // loop on constituents
    for( auto particle : jet.getJetConstituents())
    {
      if(particle->charge() != 0) continue;
      if(isPassingPUID)
        neutralParticlesPVJets->push_back(particle);
      else
        neutralParticlesPUJets->push_back(particle);
    }
  }

  
  // loop on pfParticles to determine if unclustered Neutral
  size_t indexColl = 0;
  for(reco::CandidateView::const_iterator itCand = candCollection->begin(); itCand != candCollection->end(); itCand++)
  {
    assert(itCand->charge() == 0);

    bool clustered = false;
    for(edm::PtrVector<reco::Candidate>::const_iterator iParticle = neutralParticlesPUJets->begin();  iParticle != neutralParticlesPUJets->end(); iParticle++)
    {
      if( itCand->p4() == iParticle->get()->p4())
      {
        clustered = true;
        break;
      }
    }
    for(edm::PtrVector<reco::Candidate>::const_iterator iParticle = neutralParticlesPVJets->begin();  iParticle != neutralParticlesPVJets->end(); iParticle++)
    {
      if( itCand->p4() == iParticle->get()->p4())
      {
        clustered = true;
        break;
      }
    }
    
    if(!clustered)
    {
      neutralParticlesUnclustered->push_back(edm::Ptr<reco::Candidate>(candCollection, indexColl));
    }
    indexColl++;
  }

  iEvent.put(std::move(neutralParticlesPVJets), neutralParticlesPVJets_);
  iEvent.put(std::move(neutralParticlesPUJets), neutralParticlesPUJets_);
  iEvent.put(std::move(neutralParticlesUnclustered), neutralParticlesUnclustered_);
  iEvent.put(std::move(PUJets), PUJets_);
  iEvent.put(std::move(PVJets), PVJets_);

}

DEFINE_FWK_MODULE(neutralCandidatePUIDJets);
