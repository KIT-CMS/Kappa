//- Copyright (c) 2018 - All Rights Reserved
//-  * Artur Gottmann <artur.gottmann@cern.ch>

#ifndef KAPPA_REDUCEDTRIGGEROBJECTPRODUCER_H
#define KAPPA_REDUCEDTRIGGEROBJECTPRODUCER_H

#include "KBaseMultiProducer.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Math/interface/deltaR.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"

#include <regex>



class KReducedTriggerObjectProducer : public KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KReducedTriggerObjects>
{
public:
	KReducedTriggerObjectProducer(const edm::ParameterSet &cfg, TTree *_event_tree, TTree *_lumi_tree, TTree *_run_tree, edm::ConsumesCollector && consumescollector) :
		KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KReducedTriggerObjects>(cfg, _event_tree, _lumi_tree, _run_tree, getLabel(), std::forward<edm::ConsumesCollector>(consumescollector), true)
	{
		triggerBits_ = cfg.getParameter<edm::InputTag>("bits");
		metFilterBits_ = cfg.getParameter<edm::InputTag>("metfilterbits");
                matchpattern_ = cfg.getParameter<std::string>("matchpattern");
		
		toMetadata = new KTriggerObjectMetadata;
		_lumi_tree->Bronch("triggerObjectMetadata", "KTriggerObjectMetadata", &toMetadata);

		this->triggerBitsToken_ = consumescollector.consumes<edm::TriggerResults>(triggerBits_);
		this->metFilterBitsToken_ = consumescollector.consumes<edm::TriggerResults>(metFilterBits_);
	
	}

	static const std::string getLabel() { return "ReducedTriggerObject"; }


	virtual bool onLumi(const edm::LuminosityBlock &lumiBlock, const edm::EventSetup &setup)
	{
		toMetadata->menu = KInfoProducerBase::hltConfig.tableName();
		toMetadata->toFilter.clear();
		return true;
	}

	virtual bool onFirstEvent(const edm::Event &event, const edm::EventSetup &setup)
	{
		KBaseMultiProducer<pat::TriggerObjectStandAloneCollection, KReducedTriggerObjects>::onFirstEvent(event, setup);
		edm::Handle<edm::TriggerResults> metFilterBits;
		event.getByToken(this->metFilterBitsToken_, metFilterBits);
		// preselect met filters
		metFilterNames_ = event.triggerNames(*metFilterBits);
		for(size_t i = 0; i < metFilterBits->size(); i++)
		{
			std::string metFilterName = metFilterNames_.triggerName(i);
			if(metFilterName.find("Flag") != std::string::npos)
				selectedMetFilters_.push_back(i);
		}
		nMetFilters_ = selectedMetFilters_.size();
		if(nMetFilters_ >=(8* sizeof(int)))
		{
			std::cout << "Tried to read " << nMetFilters_ << " but only able to store " << (sizeof(int)*8) << " bits." << std::endl;
			assert(false);
		}
		for(auto i : selectedMetFilters_)
		{
			toMetadata->metFilterNames.push_back(metFilterNames_.triggerName(i));
		}
		return true;
	}

	virtual bool onEvent(const edm::Event &event, const edm::EventSetup &setup) override
	{
		
		event.getByToken(this->triggerBitsToken_, triggerBitsHandle_);
		event.getByToken(this->metFilterBitsToken_, metFilterBitsHandle_);
		event_ = &(event);
		return KBaseMultiProducer::onEvent(event, setup);
	}


	virtual void clearProduct(KReducedTriggerObjects &prod)
	{
		prod.trgObjects.clear();
		prod.filterLabels.clear();
	}
	  
protected:
	KTriggerObjectMetadata *toMetadata;

	virtual void fillProduct(const InputType &in, KReducedTriggerObjects &out, const std::string &name, const edm::InputTag *tag, const edm::ParameterSet &pset) override
	{
            out.metFilterBits = 0;
            for(size_t i = 0; i < nMetFilters_; i++)
            {
            	if(metFilterBitsHandle_->accept(selectedMetFilters_[i]))
            	    out.metFilterBits = ( out.metFilterBits | ( 1 << i ));
            }
            
            out.trgObjects.clear();
            out.filterLabels.clear();
            std::regex re(matchpattern_);
            for(auto obj : in)
            {
                obj.unpackFilterLabels( *event_, *triggerBitsHandle_);
                for (auto l : obj.filterLabels())
                {
                    std::smatch m;
                    std::string label(l);
                    if(std::regex_match(label,m,re))
                    {
                        KLV triggerObject;
                        copyP4(obj.p4(),triggerObject.p4);
                        out.trgObjects.push_back(triggerObject);
                        out.filterLabels.push_back(obj.filterLabels());
                        break;
                    }
                }
            }
	}

private:
	edm::InputTag triggerBits_;
	edm::InputTag metFilterBits_;
	edm::Handle<edm::TriggerResults> triggerBitsHandle_;
	edm::Handle<edm::TriggerResults> metFilterBitsHandle_;
	edm::EDGetTokenT<edm::TriggerResults> triggerBitsToken_;
	edm::EDGetTokenT<edm::TriggerResults> metFilterBitsToken_;

	const edm::Event *event_;
        std::string matchpattern_;
	
	edm::TriggerNames metFilterNames_;
	size_t nMetFilters_;
	std::vector<size_t> selectedMetFilters_;
		
	
};

#endif
