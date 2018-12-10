
import FWCore.ParameterSet.Config as cms
import Kappa.Skimming.tools as tools

cmssw_version_number = tools.get_cmssw_version_number()

from PhysicsTools.SelectorUtils.tools.vid_id_tools import *


# https://github.com/ikrav/EgammaWork/blob/v1/ElectronNtupler/test/runElectrons_VID_MVA_PHYS14_demo.py
from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDElectronIdProducer, DataFormat
from RecoEgamma.ElectronIdentification.egmGsfElectronIDs_cff import *


def setupElectrons(process, electrons, id_modules=None):

	# use `electrons` as source for electron objects
	egmGsfElectronIDs.physicsObjectSrc = cms.InputTag(electrons)

	# enable the electron VID producer
	switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
	
	# if no `id_modules` are given, use a sensible default selection:
	if id_modules is None:
		#  always include Spring15 modules (for backward compatibility)
		id_modules = [
			'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_25ns_V1_cff',
			'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring15_25ns_nonTrig_V1_cff',
		]

		# include newer electron VID modules depending on the CMSSW version

		if tools.is_above_cmssw_version([8]):
			id_modules.extend([
				'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Summer16_80X_V1_cff',
				'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_GeneralPurpose_V1_cff',
			])

		if tools.is_above_cmssw_version([9,4]):
			id_modules.extend([
				'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V1_cff',
				'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V1_cff',
				'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V1_cff',
			])

	# set up all VIDs defined in `id_modules`
	for id_module in id_modules:
		setupAllVIDIdsInModule(process, id_module, setupVIDElectronSelection)

	# overwrite input tags to use `electrons` as physics object source
	process.elPFIsoDepositCharged.src = cms.InputTag(electrons)
	process.elPFIsoDepositChargedAll.src = cms.InputTag(electrons)
	process.elPFIsoDepositNeutral.src = cms.InputTag(electrons)
	process.elPFIsoDepositGamma.src = cms.InputTag(electrons)
	process.elPFIsoDepositPU.src = cms.InputTag(electrons)

## for electron iso
from CommonTools.ParticleFlow.Isolation.pfElectronIsolation_cff import *
elPFIsoValueCharged03PFIdPFIso = elPFIsoValueCharged03PFId.clone()
elPFIsoValueChargedAll03PFIdPFIso = elPFIsoValueChargedAll03PFId.clone()
elPFIsoValueGamma03PFIdPFIso = elPFIsoValueGamma03PFId.clone()
elPFIsoValueNeutral03PFIdPFIso = elPFIsoValueNeutral03PFId.clone()
elPFIsoValuePU03PFIdPFIso = elPFIsoValuePU03PFId.clone()

elPFIsoValueGamma03PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.08)','EcalBarrel:ConeVeto(0.08)'))
elPFIsoValueNeutral03PFIdPFIso.deposits[0].vetos = (cms.vstring())
elPFIsoValuePU03PFIdPFIso.deposits[0].vetos = (cms.vstring())
elPFIsoValueCharged03PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)'))
elPFIsoValueChargedAll03PFIdPFIso.deposits[0].vetos = (cms.vstring('EcalEndcaps:ConeVeto(0.015)','EcalBarrel:ConeVeto(0.01)'))

electronPFIsolationValuesSequence = cms.Sequence(
	elPFIsoValueCharged03PFIdPFIso+
	elPFIsoValueChargedAll03PFIdPFIso+
	elPFIsoValueGamma03PFIdPFIso+
	elPFIsoValueNeutral03PFIdPFIso+
	elPFIsoValuePU03PFIdPFIso
)
elPFIsoDepositGamma.ExtractorPSet.ComponentName = cms.string("CandViewExtractor")

# electron/muon PF iso sequence
pfElectronIso = cms.Sequence(
	electronPFIsolationDepositsSequence +
	electronPFIsolationValuesSequence
)

makeKappaElectrons = cms.Sequence(
	egmGsfElectronIDSequence
	#pfElectronIso
	)
