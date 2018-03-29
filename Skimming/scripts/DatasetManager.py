#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import json,os
from  Kappa.Skimming.datasetsHelperTwopz import datasetsHelperTwopz
import argparse
from Kappa.Skimming.tools import read_grid_control_includes



class DataSetManagerBase:
	def __init__(self, in_dataset_file,  tag_key = None, tag_values_str = None, query = None, nick_regex = None):
		self.in_dataset_file = in_dataset_file
		self.dataset = datasetsHelperTwopz(in_dataset_file)
		self.orginal = datasetsHelperTwopz(in_dataset_file) #Just a copy to compare
		self.tag_key = tag_key
		if tag_values_str:
			self.tag_values = tag_values_str.strip('][').replace(' ','').split(',')
		else:
			self.tag_values = None
		self.query = query
		self.nick_regex = nick_regex
	def get_nick_list(self, tag_key=None, tag_values=None ,query=None, nick_regex=None): 
		""" get the list with matching requerments, default use setting provided by arg parser"""
		if (not tag_key) and (not query) and (not nick_regex):
			return self.dataset.get_nick_list(tag_key=self.tag_key, tag_values=self.tag_values, query=self.query, nick_regex=self.nick_regex)
		else:
			return self.dataset.get_nick_list(tag_key=tag_key, tag_values=tag_values, query=query, nick_regex=nick_regex)
	def save_dataset(self, output_file , overwrite=False):
		""" Here the store action begins. We have three cases to store
		Outfile given: no overwrite -> Try to save to output file but will not overwrit any exsisting file
		Outfile given: overwrite -> Will save to outputfile anyway
		 Mo Outfile: overwrite -> Will save to the original database """
		if output_file:
			if overwrite:
				self.dataset.keep_input_json = False
			self.dataset.write_to_jsonfile(output_file)
		elif overwrite:
			 self.dataset.keep_input_json = False
			 self.dataset.write_to_jsonfile(None)
		else:
			self.dataset.write_to_jsonfile(None)
	def dict_diff(self):
		#self.orginal["AToZhToLLTauTauM400_RunIIFall15MiniAODv2_PU25nsData2015v1_13TeV_MINIAOD_madgraph"] = {"n_files" : u"4"}
		#self.dataset["dummy"] = {"n_files" : u"4"}
		#self.orginal["dummy"] = {"n_files" : u"4"}
		#self.orginal["dummy"] = {"adsfa" : {"dddd" : { "noch" : "einer" }}}
		
		print "only NEW:"
		print self.dataset.dataset_diff_onlyinthis(self.orginal)
		print "------------------"
		print "only OLD:"
		print self.dataset.dataset_diff_notinthis(self.orginal)
	#  print self.dataset.dataset_diff(self.dataset.base_dict,self.orginal.base_dict)
	def add_tag_to_nicks(self, add_tag_key, add_tag_values_str):
		if not add_tag_values_str:
			print "Nothing to add for the tag, ",add_tag_key," pleas add the --addtagvalues option"
			return
		nick_list = self.get_nick_list()
		self.dataset.addTags(add_tag_key, add_tag_values_str.strip('[]').replace(' ','').split(',') ,nick_list)
	
	def add_globaltag(self, add_globaltag):
		nick_list = self.get_nick_list()
		for nick in nick_list:
			self.dataset[nick]['globalTag'] = add_globaltag
	
	def rm_tags(self, rm_tag_key, rm_tag_values_str): 
		nick_list = self.get_nick_list()
		if rm_tag_values_str:
			self.dataset.rmTags(rm_tag_key, rm_tag_values_str.strip('[]').replace(' ','').split(',') ,nick_list)
		else:
			self.dataset.rmTags(rm_tag_key, None ,nick_list)
	
	def get_energy(self,  test_string):
		akt_energy = "13"
		if "14TeV" in test_string: 
			akt_energy = "14"
		elif "7TeV" in test_string: 
			akt_energy = "7"
		elif "8TeV" in test_string: 
			akt_energy = "8"
		elif "2011" in test_string:
			akt_energy = "7"
		elif "2012" in test_string:
			akt_energy = "8"
		return akt_energy
	def get_campaign(self, details, energy=None):
		campaign = details.split("-")[0]
		if energy == "8":
			campaign = campaign.split("_")[0]
		if "reHLT" in details:
			campaign = campaign+"reHLT"
		return campaign 
	
	def get_scenario(self, details, energy=None, data=False):
		if data:
			return ''.join(details.split('-')[1:])
		else:
			scenario = details.split("-")[1]
			if (energy == "7" or energy == "8"):
				scenario = scenario.split("_")[0] +"_"+ scenario.split("_")[1]
			if (energy == "13" or energy =="14"):
				scenario = scenario.split("_")[0]
			return scenario
				
				
	def get_generator(self, pd_name, data=False, isembedded=None):
		if data:
			return ""
		elif isembedded:
			return "pythia8"
		else:
			pos = pd_name.find("TeV")+4
			generators = []
			if "amcatnlo" in pd_name[pos:]:
				generators.append("amcatnlo")
			if "powheg" in pd_name[pos:]:
				generators.append("powheg")
			if "madgraph" in pd_name[pos:]:
				generators.append("madgraph")
			if "JHUgen" in pd_name[pos:]: #TODO: Generalize for any version
				if "JHUgenv628" in pd_name[pos:]:
					generators.append("JHUgenv628")
				elif "JHUgenv698" in pd_name[pos:]:
					generators.append("JHUgenv698")
				else:
					generators.append("JHUgen")
			if "pythia" in pd_name[pos:]:
				generators.append(pd_name[pos:][pd_name[pos:].find("pythia"):pd_name[pos:].find("pythia")+7])
			generator = '-'.join(generators)
			if generator == "":
				generator = "unspecified"
			return generator
	def get_process(self, pd_name):
		pos = pd_name.find("_")
		if(pos!=-1):
			process = pd_name[0:pos]
		else:
			process = pd_name
		posMass = pd_name.find("_M-")
		if posMass != -1:
			length = 3+ pd_name[posMass+3:].find("_")
			try:
				int (pd_name[posMass+3])
				process = pd_name[0:posMass+length].replace("-", "")
			except:
				pass
		else:
			posMass = pd_name.find("_M")
			if posMass != -1:
				length = 2+ pd_name[posMass+2:].find("_")
				try:
					int (pd_name[posMass+2])
					process = pd_name[0:posMass+length]
				except:
					pass
		htPos = pd_name.find("HT-")
		if(htPos!=-1):
			length = pd_name[htPos:].find("_")
			process += "_"+pd_name[htPos: htPos + length]
		ST_pos = pd_name.find("ST_t")
		if(ST_pos == 0):
			length = pd_name[0:pd_name.find("TeV")].rfind("_")
			process = pd_name[0:length].replace("_", "")
		pos = pd_name.find("CPmixing")
		if pos != -1:
			process += "_"+pd_name[pos:]
		process = process.replace("EmbeddingRun","Embedding") ## Since Run201 is Reserved for Data 
		return process
	def get_format(self,filetype):
		return filetype.replace("AODSIM", "AOD")

	def get_extension(self, details, data=False):
		if data:
			return ""
		else:
			startpos = details.find("ext")
                        endpos = details.find("-v")
                        return details[startpos:endpos]

        def get_version(self, details, data=False, embedded=False):
                if data and not embedded:
                        return ""
                else:
                        startpos = details.rfind("v")
                        return details[startpos:]

	def set_n_events_files(self, new_entry):
		new_entry["n_events_generated"]    = "-1"
		new_entry["n_files"] = "-1"
		inputDBS = new_entry.get("inputDBS", "global")
		if inputDBS in ["global","phys03","phys02","phys01"]:
			url = 'https://cmsweb.cern.ch/dbs/prod/'+inputDBS+'/DBSReader'
			from Kappa.Skimming.getNumberGeneratedEventsFromDB import RestClient
			cert = os.environ['X509_USER_PROXY']
			if not cert.strip():
				print "X509_USER_PROXY not properly set. Get a voms proxy and set this environment variable to get N events/files from siteDB"
				return 
			rest_client = RestClient(cert=cert)
			import ast
			dataset = new_entry["dbs"]
			answer=ast.literal_eval(rest_client.get(url, api='blocksummaries', params={'dataset': dataset}))
			new_entry["n_events_generated"] = str(answer[0]["num_event"])
			new_entry["n_files"] = str(answer[0]["num_file"])
		elif inputDBS in ["list"]:
			file_in = open(new_entry["dbs"] , 'r')
			n_files = 0
			n_events = 0
			for akt_line in file_in.readlines():
				if "root =" in akt_line:
					n_files +=1
					n_events += int(akt_line.split('=')[1])
					new_entry["n_events_generated"]    = str(n_events)
					new_entry["n_files"] = str(n_files)
				else:
					print "This inputDBS(",inputDBS,") can not provide event and file numbers"
		
	
	def add_dataset(self,dbs,inputDBS=None,xsec=None,nick_name=None,globaltag=None):
		new_entry = {'dbs' : dbs}
		self.query = new_entry  ## now it can be used to set tags
		if len(self.get_nick_list(query=new_entry)) > 0:
			print "dbs:",dbs," already in ",self.get_nick_list(query=new_entry)[0]
			return
	 
		if inputDBS:
			new_entry["inputDBS"] = inputDBS ## default will be global
		if globaltag is not None:
			new_entry["globalTag"] = globaltag
		new_entry["data"] = True if "Run20" in dbs else False
		if "Embedding" in dbs:
			new_entry["embedded"]  = True ## if not given assume false ;)
		## Not sure if it is important at all, but lets keep it 
		new_entry["energy"] = self.get_energy(dbs)
		if not nick_name:
			pd_name, details, filetype = dbs.strip("/").split("/")
			if xsec is not None:
				new_entry["xsec"] = float(xsec)
			new_entry["campaign"]  = self.get_campaign(details=details,energy=new_entry["energy"])
			new_entry["scenario"]  = self.get_scenario(details=details,energy=new_entry["energy"],data=new_entry["data"])
			new_entry["generator"] = self.get_generator(pd_name, data=new_entry["data"], isembedded=new_entry.get("embedded", False) )
			new_entry["process"]   = self.get_process(pd_name)
			new_entry["format"]    = self.get_format(filetype)
			new_entry["extension"] = self.get_extension(details,data=new_entry["data"] )
                        new_entry["version"] = self.get_version(details,data=new_entry["data"],embedded=new_entry.get("embedded",False))
			nick_name = self.dataset.make_nickname(new_entry)
		self.set_n_events_files(new_entry)   
		self.dataset[nick_name] = new_entry

	def query_datasets(self,pattern,inputDBS=None, xsec=None, nick_name=None, globaltag=None):
		from Kappa.Skimming.getNumberGeneratedEventsFromDB import RestClient
		cert = os.environ['X509_USER_PROXY']
		if not cert.strip():
			print "X509_USER_PROXY not properly set. Get a voms proxy and set this environment variable to get N events/files from siteDB"
			return
		rest_client = RestClient(cert=cert)
		url = 'https://cmsweb.cern.ch/dbs/prod/'+inputDBS+'/DBSReader'
		import ast
		print pattern
		dataset_list = [d["dataset"]  for d in ast.literal_eval(rest_client.get(url, api='datasets', params={'dataset': pattern}))]
		print "Adding missing datasets queried from the pattern: "
		print pattern
		print "---------------------------------------------"
		for dataset in dataset_list:
			self.add_dataset(dataset, inputDBS=inputDBS, xsec=xsec, nick_name=nick_name, globaltag=globaltag)
		return

	def delete_datasets(self):
		nicks = self.get_nick_list()
		for del_nick in nicks:
			self.dataset.base_dict.pop(del_nick)
	def print_skim(self, keys_to_print):
		nicks = self.get_nick_list()
		print "---------------------------------------------------------"
		for nick in nicks:
			print nick
			for item_to_print in self.dataset.base_dict[nick].keys() if "all" in keys_to_print else keys_to_print:
				if item_to_print in self.dataset.base_dict[nick].keys():
					print "%15s : %s" % (item_to_print, self.dataset.base_dict[nick][item_to_print])
			print "---------------------------------------------------------"
			

	def add_entry(self, entry):
		if os.path.isfile(entry):
			entry=json.load(open(entry))
		else:
			entry=json.loads(entry)
			entry=dict(entry)
		nicks = self.get_nick_list()
		self.dataset.addEntry(entry,nicks)

	def merge_json(self,newfile):
		new = datasetsHelperTwopz(newfile)
		self.dataset.merge(new)

        def copy_xsec_from_campaign(self,new_campaign,old_campaign):
            new_nick_list = [nick for nick in self.get_nick_list() if self.dataset.base_dict[nick]["campaign"] == new_campaign]
            old_nick_list = [nick for nick in self.get_nick_list() if self.dataset.base_dict[nick]["campaign"] == old_campaign and "xsec" in self.dataset.base_dict[nick]]
            xsec_dict = {}
            old_processes_xsec_per_nick_list = [(self.dataset.base_dict[nick]["process"],self.dataset.base_dict[nick]["xsec"]) for nick in old_nick_list]
            not_updated_nicks = []
            for info in old_processes_xsec_per_nick_list:
                    if not info[0] in xsec_dict:
                            xsec_dict[info[0]] = info[1]
                    else:
                            if xsec_dict[info[0]] == info[1]: continue
                            else:
                                print "WARINING: inconsistent xsec values for process %s. Please query them for the following campaign: %s"%(info[0],old_campaign)
                                print "Values: ", xsec_dict[info[0]], "vs", info[1]
                                print "--------------------"
            for nick in new_nick_list:
                if self.dataset.base_dict[nick]["process"] in xsec_dict:
                        entry = {"xsec" : float(xsec_dict[self.dataset.base_dict[nick]["process"]])}
                        self.dataset.addEntry(entry,[nick])
                else:
                        print "WARNING: cross-section not found for %s, Please set it by hand or choose a different reference campaign."%nick
                        not_updated_nicks.append(nick)
            print "Summary of not updated nicks:"
            for n in not_updated_nicks:
                print n
            process_pattern = "^("
            not_covered_process_list = set([self.dataset.base_dict[n]["process"] for n in not_updated_nicks])
            process_pattern += "|".join(list(not_covered_process_list))
            process_pattern += ")$"
            print "--query \'{\"process\" : \"%s\"}\'"%process_pattern
if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Tools for modify the dataset data base (aka datasets.json)")
	
	def_input = os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/datasets.json")
	parser.add_argument("-i", "--input", dest="inputfile", help="input data base (default=%s)"%def_input, default=def_input)
	
	parser.add_argument("--save", default="datasets.json", dest="save", help="save data base to file. For local storage please make ./filname.json otherwise $CMSSW_BASE/src/Kappa/Skimming/data/filename.json is used ")
	parser.add_argument("--overwrite", dest="overwrite", help="Allow to overwrite the database", action='store_true')
	
	parser.add_argument("--query", dest="query", help="Query which each dataset has to fulfill. Works with regex e.g: --query '{\"campaign\" : \"RunIISpring16MiniAOD.*reHLT\"}' \n((!!! For some reasons the most outer question marks must be the \'))")
	parser.add_argument("--nicks", dest="nicks", help="Query which each dataset has to fulfill. Works with regex e.g: --nicks \".*_Run2016(B|C|D).*\"")
	parser.add_argument("--tag", dest="tag", help="Ask for a specific tag of a dataset. Optional arguments are --TagValues")
	parser.add_argument("--tagvalues", dest="tagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base',Skim_Exetend\" ")
	parser.add_argument("--mergejson",default=None, dest="mergejson", help="Add new JSON file to merge with input JSON. In case of same keys inputfile will be overwritten with new keys.")

	parser.add_argument("--addentry", dest="addentry", default=None, help="Add a dict entry to all dicts that match query, e.g. --addentry '{\"NewKey\" : \"NewValue\"}' (!!! outer parentheses must be \'), or json file. Existing values with the same Key will be overwritten. [Default : %(default)s]")
	parser.add_argument("--copy_xsec_from_campaign", dest="copy_xsec_from_campaign", default=None, help="Copy xsec values process-wise from one campaign to another. Format: new_campaign,old_campaign")

	parser.add_argument("--addtag", dest="addtag", help="Add the to this tag the TagValues -> requieres -- addtagvaluesoption\nAlso either the --query or --nicks option must be given (for matching) ")
	parser.add_argument("--addtagvalues", dest="addtagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base',Skim_Exetend\" ")
	
	parser.add_argument("--globaltag", dest="globaltag", default=None, help="Add a global tag to all that matches query [Default : %(default)s]")

	parser.add_argument("--rmtag", dest="rmtag", help="Remove the to this tag the TagValues -> requieres --TagValues option\nAlso either the --query or --nicks option must be given (for matching) ")
	parser.add_argument("--rmtagvalues", dest="rmtagvalues", help="The tag values, must be a comma separated string (e.g. --TagValues \"Skim_Base',Skim_Extend\" ")
	
	parser.add_argument("--addDatasets", dest="addDatasets", help="Add one or more datasets which match a given DAS pattern with the structure /*/*/*.")
	parser.add_argument("--inputDBS", dest="inputDBS", default="global", help="Change the dbs instance, default will be global (for official samples), for private production choose phys03")
	parser.add_argument("--xsec", dest="xsec", help="Add a cross section to this Dataset ")
	
	parser.add_argument("--deleteDatasets", dest="deleteDatasets", help="Delete Datasets which are matched", action='store_true')
	
	parser.add_argument("--print", dest="print_ds", help="Print ", action='store_true')
	parser.add_argument("--printkeys", dest="printkeys", help="which keys to print [Default : %(default)s]. Choose \"all\" for printing everything.", nargs="+", default=["dbs"])
	
	args = parser.parse_args()
	if not os.path.isabs(args.inputfile):
		if os.path.exists(os.path.join(os.path.abspath(args.inputfile))):
			args.inputfile=os.path.join(os.path.abspath(args.inputfile))
		elif os.path.exists(os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/"+args.inputfile)):
			args.inputfile=os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/"+args.inputfile)
		else: 
			print "No input file could be found under either "+os.path.join(os.path.abspath(args.inputfile))+" or "+os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/"+args.inputfile)
			print "Please specify correct file path."
			exit()
		print "Using input database at "+args.inputfile
	else:
		if not os.path.exists(args.inputfile):
			print "Input Database "+args.inputfile+" could not be found. Please specify correct file path."
			exit()
	DSM = DataSetManagerBase(args.inputfile, tag_key=args.tag, tag_values_str=args.tagvalues, query=args.query, nick_regex=args.nicks )

	if args.addDatasets and (args.addentry or args.addtag or args.rmtag):
		print "Adding Datasets and adding/removing entries or tags in same instance not supported. Please do separately."
		exit()
	if args.addDatasets:
		DSM.query_datasets(args.addDatasets, inputDBS=args.inputDBS, xsec=args.xsec, globaltag=args.globaltag)
	else:
		if args.addentry:
			DSM.add_entry(entry=args.addentry)
		if args.addtag:
			DSM.add_tag_to_nicks(add_tag_key=args.addtag,add_tag_values_str=args.addtagvalues)
		if args.globaltag:
			DSM.add_globaltag(add_globaltag=str(args.globaltag))
		if args.rmtag:
			DSM.rm_tags(rm_tag_key=args.rmtag,rm_tag_values_str=args.rmtagvalues)
                if args.copy_xsec_from_campaign:
		        DSM.copy_xsec_from_campaign(args.copy_xsec_from_campaign.split(",")[0],args.copy_xsec_from_campaign.split(",")[1])
			
	if args.deleteDatasets: 
		 DSM.delete_datasets()
	if args.mergejson:
		DSM.merge_json(newfile=args.mergejson)
	DSM.dict_diff()
	
	if args.print_ds:
		DSM.print_skim(keys_to_print=args.printkeys)
			 
		
		
# Always show the difference between old an new

	if not os.path.isabs(args.save):
		args.save=os.path.join(os.environ.get("CMSSW_BASE"),"src/Kappa/Skimming/data/"+args.save)
# Add the end store the result (default is not to store at all 
	DSM.save_dataset(args.save, args.overwrite)

