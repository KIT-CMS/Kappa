//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_PATMETPRODUCER_H
#define KAPPA_PATMETPRODUCER_H

#include "KBaseMultiProducer.h"
#include "KMETProducer.h"
#include "../../DataFormats/interface/KBasic.h"
#include "../../DataFormats/interface/KDebug.h"
#include <DataFormats/METReco/interface/PFMET.h>
#include <DataFormats/PatCandidates/interface/MET.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KPatMETProducer : public KBaseMultiProducer<edm::View<pat::MET>, KMET>
{
public:
	KPatMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<pat::MET>, KMET>(cfg, _event_tree, _lumi_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		uncorrected(cfg.getParameter<bool>("uncorrected")){
		genMet = new KMET;
		_event_tree->Bronch("genmetTrue", "KMET", &genMet);
	}

	static const std::string getLabel() { return "PatMET"; }

	static void fillMET(const pat::MET &in, KMET &out, bool uncor = false)
	{
		// fill properties of basic MET
		KMETProducer::fillMET<pat::MET>(in, out);
		if(uncor){
			#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 6) || (CMSSW_MAJOR_VERSION > 7)
				out.p4 = in.uncorP4();
				out.sumEt = in.uncorSumEt();
				if (verbosity > 0){
					std::cout << "KPatMETProducer::fillMET : MET uncorrection enabled."<< std::endl;
				}
			#else
			std::cout << "ERROR: MET is not uncorrected! Use CMSSW 7 or higher to use this feature." << std::endl; 
			#endif
		}
		if(in.isPFMET())
		{
			// additional PF properties
			out.photonFraction = in.NeutralEMFraction(); // Todo: check if equivalent to photonEtFraction
			out.neutralHadronFraction = in.NeutralHadEtFraction();
			out.electronFraction = in.ChargedEMEtFraction();
			out.chargedHadronFraction = in.ChargedHadEtFraction();
			out.muonFraction = in.MuonEtFraction();
			out.hfHadronFraction = in.Type6EtFraction();
			out.hfEMFraction = in.Type7EtFraction();
		}
		#if (CMSSW_MAJOR_VERSION == 7 && CMSSW_MINOR_VERSION >= 6) || (CMSSW_MAJOR_VERSION > 7)
			// retrieve and save shifted four vector and sumEt of MET for all uncertainties
			for (const auto metUnc : KMETUncertainty::All)
			{
				// The following 'uncertainties' result in runtime errors.
				// No idea for what purpose they exist in pat::MET::METUncertainty
				if (metUnc == KMETUncertainty::NoShift ||
					metUnc == KMETUncertainty::METUncertaintySize ||
					metUnc == KMETUncertainty::JetResUpSmear ||
					metUnc == KMETUncertainty::JetResDownSmear ||
					metUnc == KMETUncertainty::METFullUncertaintySize)
					continue;
				// For now, only type-1 corrected MET (default) is saved.
				copyP4(in.shiftedP4(static_cast<pat::MET::METUncertainty>(metUnc)),out.p4_shiftedByUncertainties[static_cast<KMETUncertainty::Type>(metUnc)]);
				out.sumEt_shiftedByUncertainties[static_cast<KMETUncertainty::Type>(metUnc)] = in.shiftedSumEt(static_cast<pat::MET::METUncertainty>(metUnc));
			}
		#endif
	}

protected:
	virtual void clearProduct(OutputType &output) { output.p4.SetCoordinates(0, 0, 0, 0); output.sumEt = -1; }
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		if (in.size() != 1)
		{
			if (verbosity > 1)
				std::cout << "KMETProducer::fillProduct: Found " << in.size() << " pat::MET objects!" << std::endl;
			return;
		}

		fillMET(in.at(0), out, uncorrected);
		// fill GenMET
		if (in.at(0).genMET())
		{
			const reco::GenMET* recoGenMet = in.at(0).genMET();
			KMETProducer::fillMET<reco::GenMET>(*recoGenMet, *genMet);
		}
	}

private:
	TTree* _event_tree_pointer;
	KMET* genMet;
	bool uncorrected;
};

#endif
