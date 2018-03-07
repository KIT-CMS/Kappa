//- Copyright (c) 2010 - All Rights Reserved
//-  * Fred Stober <stober@cern.ch>
//-  * Manuel Zeise <zeise@cern.ch>

#ifndef KAPPA_L1TAUPRODUCER_H
#define KAPPA_L1TAUPRODUCER_H

#include "KBaseMultiLVProducer.h"
#include <DataFormats/L1Trigger/interface/Tau.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include "../../Producers/interface/Consumes.h"

class KL1TauProducer : public KBaseMultiLVProducer<edm::View<l1t::Tau>, KL1Taus>
{
public:
	KL1TauProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiLVProducer<edm::View<l1t::Tau>, KL1Taus>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector)),
		L1TauTag(cfg.getParameter<edm::InputTag>("input"))
        {
                this->L1TauCollection = consumescollector.consumes<l1t::TauBxCollection>(L1TauTag);
                std::cout << "Producer for L1 Taus initialized" << std::endl;
        }
        
	virtual void fillProduct(const InputType &in, OutputType &out,
		const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset)
	{
		// Retrieve additional input products
		cEvent->getByToken(L1TauCollection, L1TauHandle);

                std::cout << "Running L1 Tau Producer" << std::endl;
		// Continue normally
		KBaseMultiLVProducer<edm::View<l1t::Tau>, KL1Taus>::fillProduct(in, out, name, tag, pset);
	}

	virtual void fillSingle(const SingleInputType &in, SingleOutputType &out)
	{
		for (l1t::TauBxCollection::const_iterator bx0TauIt = this->L1TauHandle->begin(0); bx0TauIt != this->L1TauHandle->end(0) ; bx0TauIt++)
                {
                    copyP4((*bx0TauIt).p4(), out.p4);
                    out.hwIso = (*bx0TauIt).hwIso();
                }
	}

	static const std::string getLabel() { return "L1Taus"; }

	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		return true;
	}


private:

        edm::InputTag L1TauTag;
        edm::EDGetTokenT<l1t::TauBxCollection> L1TauCollection;
        edm::Handle<BXVector<l1t::Tau>> L1TauHandle;

};

#endif
