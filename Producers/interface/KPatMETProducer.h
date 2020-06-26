//- Copyright (c) 2010 - All Rights Reserved
//-  * Armin Burgmeier <burgmeier@ekp.uni-karlsruhe.de>
//-  * Bastian Kargoll <bastian.kargoll@cern.ch>
//-  * Fred Stober <stober@cern.ch>
//-  * Joram Berger <joram.berger@cern.ch>

#ifndef KAPPA_PATMETPRODUCER_H
#define KAPPA_PATMETPRODUCER_H

#include <stdexcept>

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
	KPatMETProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<edm::View<pat::MET>, KMET>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)){

		genMet = new KMET;
		_event_tree->Bronch("genmetTrue", "KMET", &genMet);

		// use global PatMET.correctionLevel (or Type1 if not given) as default for all MET targets
		auto defaultCorrLevel = resolveCorrLevelFromPSet(cfg, pat::MET::Type1);

		// compute enum members for MET correction levels and store in target PSets
		for (auto& targetSetup : targetSetupMap) {
			const edm::ParameterSet &pset = std::get<0>(targetSetup.second);
			corrLevelMap[targetSetup.first] = resolveCorrLevelFromPSet(pset, defaultCorrLevel);
		}
	}

	static const std::string getLabel() { return "PatMET"; }

	static void fillMET(const pat::MET &in, KMET &out, pat::MET::METCorrectionLevel corrLevel = pat::MET::Type1)
	{
		// fill properties of basic MET
		KMETProducer::fillMET<pat::MET>(in, out);

		out.p4 = in.corP4(corrLevel);
		out.sumEt = in.corSumEt(corrLevel);

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

		fillMET(in.at(0), out, corrLevelMap[&out]);
		// fill GenMET
		if (in.at(0).genMET())
		{
			const reco::GenMET* recoGenMet = in.at(0).genMET();
			KMETProducer::fillMET<reco::GenMET>(*recoGenMet, *genMet);
		}
	}

	/** Turn correction level specified as string to pat::MET::METCorrectionLevel enum member */
	static pat::MET::METCorrectionLevel getMETCorrectionLevel(const std::string& correctionLevelSpec) {
		if (correctionLevelSpec == "Raw") return pat::MET::Raw;
		if (correctionLevelSpec == "Type1") return pat::MET::Type1;
		if (correctionLevelSpec == "Type01") return pat::MET::Type01;
		if (correctionLevelSpec == "TypeXY") return pat::MET::TypeXY;
		if (correctionLevelSpec == "Type1XY") return pat::MET::Type1XY;
		if (correctionLevelSpec == "Type01XY") return pat::MET::Type01XY;
		if (correctionLevelSpec == "Type1Smear") return pat::MET::Type1Smear;
		if (correctionLevelSpec == "Type01Smear") return pat::MET::Type01Smear;
		if (correctionLevelSpec == "Type1SmearXY") return pat::MET::Type1SmearXY;
		if (correctionLevelSpec == "Type01SmearXY") return pat::MET::Type01SmearXY;
		if (correctionLevelSpec == "RawCalo") return pat::MET::RawCalo;
		if (correctionLevelSpec == "RawChs") return pat::MET::RawChs;
		if (correctionLevelSpec == "RawTrk") return pat::MET::RawTrk;
		throw std::invalid_argument("Invalid MET correction level: " + correctionLevelSpec);
	}

	/** resolve correction level from PSet */
	static pat::MET::METCorrectionLevel resolveCorrLevelFromPSet(
	    const edm::ParameterSet& pset,
	    pat::MET::METCorrectionLevel defaultCorrLevel = pat::MET::Type1)
	{
		// handle deprecated 'uncorrected' keyword
		if (pset.exists("uncorrected") && pset.getParameter<bool>("uncorrected")) {
			std::cout << "[KPatMETProducer] WARNING: Keyword 'uncorrected' is deprecated. "
			          << "Use correctionLevel='Raw' instead. MET will remain uncorrected." << std::endl;
			return pat::MET::Raw;
		}

		// use 'correctionLevel' keyword (or Type1 if not given)
		return pset.exists("correctionLevel") ?
		       getMETCorrectionLevel(pset.getParameter<std::string>("correctionLevel")) :
		       defaultCorrLevel;
	}

private:
	TTree* _event_tree_pointer;
	KMET* genMet;
	std::map<KMET*, pat::MET::METCorrectionLevel> corrLevelMap;
};

#endif
