//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>
//-  * Thomas Mueller <tmuller@cern.ch>

#ifndef KAPPA_MUONPRODUCER_H
#define KAPPA_MUONPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include "KTrackProducer.h"

#include <bitset>
#include <TMath.h>
#include <Math/GenVector/VectorUtil.h>
#include <DataFormats/Common/interface/Ref.h>
#include <DataFormats/Common/interface/ValueMap.h>
#include <DataFormats/GeometrySurface/interface/Cylinder.h>
#include <DataFormats/GeometrySurface/interface/Plane.h>
#include <DataFormats/HLTReco/interface/TriggerEvent.h>
#include <DataFormats/MuonReco/interface/MuonFwd.h>
#include <DataFormats/MuonReco/interface/Muon.h>
#include <DataFormats/MuonReco/src/MuonSelectors.cc>
#include <DataFormats/RecoCandidate/interface/IsoDepositVetos.h>
#include <HLTriggerOffline/Muon/src/PropagateToMuon.cc>
#include <PhysicsTools/IsolationAlgos/interface/IsoDepositVetoFactory.h>
#include <TrackingTools/GeomPropagators/interface/Propagator.h>
#include <TrackingTools/Records/interface/TrackingComponentsRecord.h>
#include <TrackingTools/Records/interface/TransientTrackRecord.h>
#include <TrackingTools/TransientTrack/interface/TransientTrackBuilder.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include <DataFormats/VertexReco/interface/Vertex.h>
#include "../../Producers/interface/Consumes.h"
#include "boost/functional/hash.hpp"

class KMuonProducer : public KBaseMultiLVProducer<edm::View<reco::Muon>, KMuons>
{
public:
	KMuonProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<reco::Muon>, KMuons>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		tagHLTrigger(cfg.getParameter<edm::InputTag>("hlTrigger")),
		VertexCollectionSource(cfg.getParameter<edm::InputTag>("vertexcollection")),
		isoValInputTags(cfg.getParameter<std::vector<edm::InputTag> >("isoValInputTags")),
		hltMaxdR(cfg.getParameter<double>("hltMaxdR")),
		hltMaxdPt_Pt(cfg.getParameter<double>("hltMaxdPt_Pt")),
		selectedMuonTriggerObjects(cfg.getParameter<std::vector<std::string> >("muonTriggerObjects")),
		noPropagation(cfg.getParameter<bool>("noPropagation")),
		propagatorToMuonSystem(cfg),
		doPfIsolation(cfg.getParameter<bool>("doPfIsolation")),
		use03ConeForPfIso(cfg.getParameter<bool>("use03ConeForPfIso")),
		muonIsolationPFInitialized(false)
	{
		std::sort(selectedMuonTriggerObjects.begin(), selectedMuonTriggerObjects.end());
		std::vector<std::string>::iterator tempIt = std::unique(
			selectedMuonTriggerObjects.begin(), selectedMuonTriggerObjects.end());
		selectedMuonTriggerObjects.resize(tempIt - selectedMuonTriggerObjects.begin());

		muonMetadata = new KMuonMetadata();
		_lumi_tree->Bronch("muonMetadata", "KMuonMetadata", &muonMetadata);

        this->HLTTriggerToken = consumescollector.consumes<trigger::TriggerEvent>(tagHLTrigger);
		this->VertexCollectionToken = consumescollector.consumes<reco::VertexCollection>(VertexCollectionSource);
        const edm::ParameterSet &psBase = this->psBase;
        std::vector<std::string> names = psBase.getParameterNamesForType<edm::ParameterSet>();

        for (size_t i = 0; i < names.size(); ++i)
        {
            const edm::ParameterSet pset = psBase.getParameter<edm::ParameterSet>(names[i]);
            if(pset.existsAs<edm::InputTag>("vertexcollection")) consumescollector.consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertexcollection"));
			for(size_t j = 0; j < isoValInputTags.size(); ++j)
				isoValTokens.push_back(consumescollector.consumes<edm::ValueMap<double>>(isoValInputTags.at(j)));
        }
	}

	static const std::string getLabel() { return "Muons"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		if(!noPropagation)
			propagatorToMuonSystem.init(setup);

		muonMetadata->hltNames.clear();
		muonTriggerObjectBitMap.clear();

		if (selectedMuonTriggerObjects.size() > 64)
		{
			std::cout << "Too many muon trigger objects selected (" << selectedMuonTriggerObjects.size() << ">64)!" << std::endl;
			throw cms::Exception("Too many muon trigger objects selected");
		}

		for (std::vector<std::string>::iterator it = selectedMuonTriggerObjects.begin(); it != selectedMuonTriggerObjects.end(); it++)
		{
			std::string filterName = *it;
			if (muonTriggerObjectBitMap.find(filterName) != muonTriggerObjectBitMap.end())
				throw cms::Exception("The muon trigger object '" + filterName + "' exists twice. Please remove one from your configuration!");
			if (muonMetadata->hltNames.size() >= 64)
				throw cms::Exception("Too many muon trigger objects selected!");
			if (verbosity > 0)
				std::cout << "KMuonProducer::onLumi : " << filterName << "\n";
			muonMetadata->hltNames.push_back(filterName);
			muonTriggerObjectBitMap[filterName] = muonMetadata->hltNames.size() - 1;
			if (verbosity > 0)
				std::cout << "KMuonProducer::onLumi : muon trigger object: " << (muonMetadata->hltNames.size() - 1) << " = " << filterName << "\n";
		}

		return KBaseMultiLVProducer<edm::View<reco::Muon>, KMuons>::onLumi(lumiBlock, setup);
	}

	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products

		if (tagHLTrigger.label() != "")
			cEvent->getByToken(HLTTriggerToken, triggerEventHandle);

		cEvent->getByToken(VertexCollectionToken, VertexHandle);

		pfIsoVetoCone = pset.getParameter<double>("pfIsoVetoCone");
		pfIsoVetoMinPt = pset.getParameter<double>("pfIsoVetoMinPt");

		isoVals.resize(this->isoValInputTags.size());
		for (size_t j = 0; j < this->isoValInputTags.size(); ++j)
		{
			cEvent->getByToken(isoValTokens[j], isoVals[j]);
			if (isoVals[j].failedToGet())
			{
				doPfIsolation = false;
			}
		}

		// Continue normally
		KBaseMultiLVProducer<edm::View<reco::Muon>, KMuons>::fillProduct(in, out, name, tag, pset);
	}

	/// fill muon from DataFormats/MuonReco/interface/Muon.h
	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		out.leptonInfo = KLeptonFlavour::MUON;
		// hash of pointer as Id
		out.internalId = hasher(&in);
		
		/// momentum:
		copyP4(in, out.p4);

		/// Tracks and track extracted information
		if (in.track().isNonnull())
			KTrackProducer::fillTrack(*in.track(), out.track);
		if (in.globalTrack().isNonnull())
			KTrackProducer::fillTrack(*in.globalTrack(), out.globalTrack);

		reco::Vertex vtx = VertexHandle->at(0);
		if (in.muonBestTrack().isNonnull()) // && &vtx != NULL) TODO
		{
			/// ID var from the bestTrack which is not saved entirely
			out.dxy = in.bestTrack()->dxy(vtx.position()); //dxy from vertex should be using IPTools (e.g. like PAT)
			out.dz = in.bestTrack()->dz(vtx.position());
			out.relBestTrkErr = in.bestTrack()->pt() > 0 ? in.bestTrack()->ptError() / in.bestTrack()->pt() : -1;
		}
		// propagated values of eta and phi
		out.eta_propagated = -1000.;
		out.phi_propagated = -1000.;
		if (in.innerTrack().isNonnull() && !noPropagation)
		{
			TrajectoryStateOnSurface prop = propagatorToMuonSystem.extrapolate(in);
			if (prop.isValid())
			{
				out.eta_propagated = prop.globalPosition().eta();
				out.phi_propagated = prop.globalPosition().phi();
			}
		}

		// Charge, muon system information
		assert(in.charge() == 1 || in.charge() == -1);
		out.leptonInfo |= (in.charge() > 0) ? KLeptonChargeMask : 0;
		out.nChambers = in.numberOfChambers();
		out.nMatches = in.numberOfMatches();
		out.nMatchedStations = in.numberOfMatchedStations();
		out.caloCompatibility = muon::caloCompatibility(in);
		out.segmentCompatibility = muon::segmentCompatibility(in);

		assert(in.type() < 256);
		out.type = in.type();

		// muon ID selection
		// DataFormats/MuonReco/src/MuonSelectors.cc
		std::bitset<32> tmpBits;
		for (size_t i = 0; i < 16; ++i)
			tmpBits.set(i, muon::isGoodMuon(in, (muon::SelectionType) i));
		out.isGoodMuonBits = (unsigned int) tmpBits.to_ulong();

		/// Isolation
		if (doPfIsolation)
		{
			// code copied from KElectronProducer
			// we need the Ref, cf. example EgammaAnalysis/ElectronTools/src/EGammaCutBasedEleIdAnalyzer.cc
			edm::Ref<edm::View<reco::Muon>> m(this->handle, this->nCursor);
			
			// isolation values (PF is used for IDs later)
			double iso_ch = (*(isoVals)[0])[m];
			double iso_ph = (*(isoVals)[1])[m];
			double iso_nh = (*(isoVals)[2])[m];
			double iso_pu = (*(isoVals)[3])[m];

			out.sumChargedHadronPt = iso_ch;
			out.sumNeutralHadronEt = iso_nh;
			out.sumPhotonEt = iso_ph;
			out.sumPUPt = iso_pu;
		}
		else
		{
			/// isolation variables for pfIso
			/// DataFormats/MuonReco/interface/MuonPFIsolation.h
			reco::MuonPFIsolation muonIsolationR03 = in.pfIsolationR03();
			reco::MuonPFIsolation muonIsolationR04 = in.pfIsolationR04();

			out.sumChargedHadronPt   = muonIsolationR03.sumChargedHadronPt;
			out.sumChargedParticlePt = muonIsolationR03.sumChargedParticlePt;
			out.sumNeutralHadronEt   = muonIsolationR03.sumNeutralHadronEt;
			out.sumPhotonEt          = muonIsolationR03.sumPhotonEt;
			out.sumPUPt              = muonIsolationR03.sumPUPt;
			out.sumNeutralHadronEtHighThreshold = muonIsolationR03.sumNeutralHadronEtHighThreshold;
			out.sumPhotonEtHighThreshold        = muonIsolationR03.sumPhotonEtHighThreshold;

			out.sumChargedHadronPtR04   = muonIsolationR04.sumChargedHadronPt;
			out.sumChargedParticlePtR04 = muonIsolationR04.sumChargedParticlePt;
			out.sumNeutralHadronEtR04   = muonIsolationR04.sumNeutralHadronEt;
			out.sumPhotonEtR04          = muonIsolationR04.sumPhotonEt;
			out.sumPUPtR04              = muonIsolationR04.sumPUPt;
			out.sumNeutralHadronEtHighThresholdR04 = muonIsolationR04.sumNeutralHadronEtHighThreshold;
			out.sumPhotonEtHighThresholdR04        = muonIsolationR04.sumPhotonEtHighThreshold;
		}
		// source?
		if(muonIsolationPFInitialized)
		{
			edm::RefToBase<reco::Muon> muonref(edm::Ref<edm::View<reco::Muon> >(handle, this->nCursor));
			reco::IsoDeposit muonIsoDepositPF = (*isoDepsPF)[muonref];
			reco::isodeposit::Direction dir = reco::isodeposit::Direction(in.eta(), in.phi());
			reco::isodeposit::ConeVeto pf_cone_veto(dir, pfIsoVetoCone);
			reco::isodeposit::ThresholdVeto pf_threshold_veto(pfIsoVetoMinPt);

			std::vector<reco::isodeposit::AbsVeto*> vetosPF;
			vetosPF.push_back(&pf_cone_veto);
			vetosPF.push_back(&pf_threshold_veto);
			out.pfIso03    = muonIsoDepositPF.depositWithin(0.3, vetosPF);
			out.pfIso04    = muonIsoDepositPF.depositWithin(0.4, vetosPF);
		}
		/// isolation results
		out.trackIso = in.isolationR03().sumPt;

		/// highpt ID variables
		/** needed variables according to
		    https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMuonId#New_HighPT_Version_recommended
		    not in new CMSSW versions

		reco::TrackRef cktTrack = muon::improvedMuonBestTrack(const reco::Muon & recoMu, muon::improvedTuneP);
		dxy_high = cktTrack->db...
		dz_high = 0;
		pt_high = cktTrack->pt();
		pte_high = cktTrack->ptError();
		*/

		out.hltMatch = getHLTInfo(out.p4);

		/// store variables used in muon ids
		out.normalizedChiSquare = in.globalTrack().isNonnull() ? in.globalTrack()->normalizedChi2() : 0;
		out.chiSquareLocalPos = in.combinedQuality().chi2LocalPosition;
		out.trkKink = in.combinedQuality().trkKink;
		out.validFractionOfTrkHits = in.innerTrack().isNonnull() ? in.innerTrack()->validFraction() : 0;

		/// precomputed muon IDs
		/** https://hypernews.cern.ch/HyperNews/CMS/get/muon/868.html
		    https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideMuonId#Baseline_muon_selections_for_201
			DataFormats/MuonReco/src/MuonSelectors.cc
			automatically use muon::improvedTuneP default as in CMSSW
		    Medium Id definition taken from:
		    https://indico.cern.ch/event/357213/contribution/2/material/slides/0.pdf
		    if release < 74X, otherwise use the method in the muon dataformat
			last update: 2015-06-19
		*/
#if (CMSSW_MAJOR_VERSION < 7) || (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION < 4)
		bool goodGlb = in.isGlobalMuon() &&
			       (in.globalTrack().isNonnull() ? (in.globalTrack()->normalizedChi2() < 3.) : 0 ) &&
			       in.combinedQuality().chi2LocalPosition < 12. &&
			       in.combinedQuality().trkKink < 20.;
		bool isMediumMuon = (in.innerTrack().isNonnull() ? (in.innerTrack()->validFraction() >= 0.8) : 0 ) &&
			       muon::segmentCompatibility(in) >= (goodGlb ? 0.303 : 0.451);
#else
		bool isMediumMuon = muon::isMediumMuon(in);
#endif

		out.ids = KLeptonId::ANY;
		out.ids |= (muon::isLooseMuon(in)      << KLeptonId::LOOSE);
		out.ids |= (isMediumMuon               << KLeptonId::MEDIUM);
		out.ids |= (muon::isTightMuon(in, vtx) << KLeptonId::TIGHT);
		out.ids |= (muon::isSoftMuon(in, vtx)  << KLeptonId::SOFT);
#if CMSSW_MAJOR_VERSION == 5 && CMSSW_MINOR_VERSION < 15
		out.ids |= (muon::isHighPtMuon(in, vtx, reco::improvedTuneP) << KLeptonId::HIGHPT);
#else
		out.ids |= (muon::isHighPtMuon(in, vtx) << KLeptonId::HIGHPT);
#endif
		assert((out.ids & 145) == 0); // 145 = 0b10010001, these bits should be zero
	}

private:
	edm::InputTag tagHLTrigger;
	edm::InputTag VertexCollectionSource;
	std::vector<edm::InputTag>  isoValInputTags;
	edm::EDGetTokenT<trigger::TriggerEvent> HLTTriggerToken;
	edm::EDGetTokenT<reco::VertexCollection> VertexCollectionToken;
	std::vector<edm::EDGetTokenT<edm::ValueMap<double>>> isoValTokens;
	double hltMaxdR, hltMaxdPt_Pt;
	double pfIsoVetoCone, pfIsoVetoMinPt;
	std::vector<std::string> selectedMuonTriggerObjects;
	bool noPropagation;
	PropagateToMuon propagatorToMuonSystem;
	edm::Handle<edm::ValueMap<reco::IsoDeposit> > isoDepsPF;
	edm::Handle<trigger::TriggerEvent> triggerEventHandle;
	edm::Handle<reco::VertexCollection> VertexHandle;
	KMuonMetadata *muonMetadata;
	boost::hash<const reco::Muon*> hasher;
	
	std::vector<edm::Handle<edm::ValueMap<double> > > isoVals;
	bool doPfIsolation;
	bool use03ConeForPfIso;
	bool muonIsolationPFInitialized;

	std::map<std::string, int> muonTriggerObjectBitMap;

	unsigned long long getHLTInfo(const RMFLV p4)
	{
		if (!triggerEventHandle.isValid())
			return 0;
		unsigned long long ret = 0;

		const size_t sizeFilters = triggerEventHandle->sizeFilters();

		for (size_t iF = 0; iF < sizeFilters; ++iF)
		{
			const std::string nameFilter(triggerEventHandle->filterTag(iF).label());
			const trigger::Keys & keys = triggerEventHandle->filterKeys(iF);

			if (muonTriggerObjectBitMap.find(nameFilter) == muonTriggerObjectBitMap.end())
				continue;

			for (size_t iK = 0; iK < keys.size(); ++iK)
			{
				trigger::TriggerObject triggerObject(triggerEventHandle->getObjects().at(keys[iK]));
				RMFLV tmpP4(triggerObject.pt(), triggerObject.eta(), triggerObject.phi(), triggerObject.mass());

				if ((ROOT::Math::VectorUtil::DeltaR(p4, tmpP4) < hltMaxdR) && (std::abs(p4.pt() - tmpP4.pt()) / tmpP4.pt() < hltMaxdPt_Pt))
				{
					ret |= ((unsigned long long)1 << muonTriggerObjectBitMap[nameFilter]);
				}
			}
		}
		return ret;
	}
};

#endif
