from collections import OrderedDict

class Sample(object):
    def __init__(self, year, das, cfg, out):
        self.year = str(year)
        self.das = das
        self.cfg = cfg
        self.out = out
        # shorten the names, bloody crab tops at 100 characters...
        self.name = '_'.join(das.split('/')[1:-1])
        self.name = self.name.replace('RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15', 'Autumn18')
        self.name = self.name.replace('RunIIAutumn18MiniAOD-FlatPU0to70_102X_upgrade2018_realistic_v15', 'Autumn18FlatPU')
        self.name = self.name.replace('RunIIAutumn18MiniAOD-FlatPU0to70RAW_102X_upgrade2018_realistic_v15', 'Autumn18FlatPU')
        self.name = self.name.replace('RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14', 'Fall17')
        self.name = self.name.replace('RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14', 'Fall17newPMX')
        self.name = self.name.replace('RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14', 'Fall17RECOSIM')
        self.name = self.name.replace('RunIIFall17MiniAODv2-PU2017_12Apr2018_v2_94X_mc2017_realistic_v14', 'Fall17v2')
        self.name = self.name.replace('RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3', 'Summer16')
        self.name = self.name.replace('-', '_')

# samples = [
#     Sample(2018, "/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-FlatPU0to70_102X_upgrade2018_realistic_v15-v1/MINIAODSIM"               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
#     Sample(2018, "/Tau/Run2018A-17Sep2018-v1/MINIAOD"        , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
# 
#     Sample(2017, "/WW_TuneCP5_13TeV-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                                          , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
#     Sample(2017, "/SingleMuon/Run2017C-Nano14Dec2018-v1/NANOAOD"    , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
# 
#     Sample(2016, "/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"                                                   , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
#     Sample(2016, "/SingleMuon/Run2016D-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
# ]


samples = [
    # MC 2018
    Sample(2018, "/QCD_Pt-15to7000_TuneCP5_Flat_13TeV_pythia8/RunIIAutumn18MiniAOD-FlatPU0to70RAW_102X_upgrade2018_realistic_v15_ext2-v1/MINIAODSIM"              , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/RunIIAutumn18MiniAOD-FlatPU0to70RAW_102X_upgrade2018_realistic_v15-v1/MINIAODSIM"               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    ###########
    Sample(2018, "/WW_TuneCP5_13TeV-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                                                    , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/WZ_TuneCP5_13TeV-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v3/MINIAODSIM"                                                    , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/ZZ_TuneCP5_13TeV-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                                                    , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    ###########
    Sample(2018, "/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                                , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    ########### 
    Sample(2018, "/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-FlatPU0to70_102X_upgrade2018_realistic_v15-v1/MINIAODSIM"               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                       , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM"                           , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                          , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                          , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v2/MINIAODSIM"                          , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM"                          , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    ###########
    Sample(2018, "/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM"                               , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM"                                   , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM"                                      , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    ###########
    Sample(2018, "/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v1/MINIAODSIM"          , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v1/MINIAODSIM"              , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/ST_t-channel_top_5f_TuneCP5_13TeV-powheg-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM"                            , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15-v1/MINIAODSIM", 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    Sample(2018, "/VBFHToTauTau_M125_13TeV_powheg_pythia8/RunIIAutumn18MiniAOD-102X_upgrade2018_realistic_v15_ext1-v1/MINIAODSIM"                                 , 'myNanoProdMc2018_NANO.py', 'myNanoProdMc2018_NANO.root'),
    # data 2018
    Sample(2018, "/Tau/Run2018A-17Sep2018-v1/MINIAOD"        , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/Tau/Run2018B-17Sep2018-v1/MINIAOD"        , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/Tau/Run2018C-17Sep2018-v1/MINIAOD"        , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/Tau/Run2018D-PromptReco-v2/MINIAOD"       , 'myNanoProdData2018D_NANO.py'  , 'myNanoProdData2018D_NANO.root'  ),
    ###########
    Sample(2018, "/SingleMuon/Run2018A-17Sep2018-v2/MINIAOD" , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/SingleMuon/Run2018B-17Sep2018-v1/MINIAOD" , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/SingleMuon/Run2018C-17Sep2018-v1/MINIAOD" , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/SingleMuon/Run2018D-PromptReco-v2/MINIAOD", 'myNanoProdData2018D_NANO.py'  , 'myNanoProdData2018D_NANO.root'  ),
    ###########
    Sample(2018, "/EGamma/Run2018A-17Sep2018-v2/MINIAOD"     , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/EGamma/Run2018B-17Sep2018-v1/MINIAOD"     , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/EGamma/Run2018C-17Sep2018-v1/MINIAOD"     , 'myNanoProdData2018ABC_NANO.py', 'myNanoProdData2018ABC_NANO.root'),
    Sample(2018, "/EGamma/Run2018D-PromptReco-v2/MINIAOD"    , 'myNanoProdData2018D_NANO.py'  , 'myNanoProdData2018D_NANO.root'  ),

    ###########
    ###########

    # MC 2017
    Sample(2017, "/WW_TuneCP5_13TeV-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                                          , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/WW_TuneCP5_13TeV-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM"                                                          , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/WZ_TuneCP5_13TeV-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                                          , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ZZ_TuneCP5_13TeV-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v2/MINIAODSIM"                                                  , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    ###########
    Sample(2017, "/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v2/MINIAODSIM"                                 , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3/MINIAODSIM"                                      , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM"                                      , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v3/MINIAODSIM"                                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v4/MINIAODSIM"                                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v4/MINIAODSIM"                                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v5/MINIAODSIM"                                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/W4JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v2/MINIAODSIM"                             , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    ###########
    Sample(2017, "/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v2/MINIAODSIM"                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                      , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017RECOSIMstep_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM"                 , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM"                        , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14_ext1-v2/MINIAODSIM"                   , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14_ext1-v2/MINIAODSIM"                   , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/MINIAODSIM"                           , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_v2_94X_mc2017_realistic_v14-v2/MINIAODSIM"                             , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    ###########
    Sample(2017, "/TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM"                             , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v2/MINIAODSIM"                                 , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM"                                    , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    ###########
    Sample(2017, "/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM"                     , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"                         , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM"                         , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_new_pmx_94X_mc2017_realistic_v14-v1/MINIAODSIM", 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/MINIAODSIM"    , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    Sample(2017, "/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/MINIAODSIM"    , 'myNanoProdMc2017_NANO.py', 'myNanoProdMc2017_NANO.root'),
    # data 2017
    Sample(2017, "/Tau/Run2017B-Nano14Dec2018-v1/NANOAOD"           , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/Tau/Run2017C-Nano14Dec2018-v1/NANOAOD"           , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/Tau/Run2017D-Nano14Dec2018-v1/NANOAOD"           , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/Tau/Run2017E-Nano14Dec2018-v1/NANOAOD"           , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/Tau/Run2017F-Nano14Dec2018-v1/NANOAOD"           , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    ###########
    Sample(2017, "/SingleMuon/Run2017B-Nano14Dec2018-v1/NANOAOD"    , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleMuon/Run2017C-Nano14Dec2018-v1/NANOAOD"    , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleMuon/Run2017D-Nano14Dec2018-v1/NANOAOD"    , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleMuon/Run2017E-Nano14Dec2018-v1/NANOAOD"    , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleMuon/Run2017F-Nano14Dec2018-v1/NANOAOD"    , 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    ###########
    Sample(2017, "/SingleElectron/Run2017B-Nano14Dec2018-v1/NANOAOD", 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleElectron/Run2017C-Nano14Dec2018-v1/NANOAOD", 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleElectron/Run2017D-Nano14Dec2018-v1/NANOAOD", 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleElectron/Run2017E-Nano14Dec2018-v1/NANOAOD", 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),
    Sample(2017, "/SingleElectron/Run2017F-Nano14Dec2018-v1/NANOAOD", 'myNanoProdData2017_NANO.py', 'myNanoProdData2017_NANO.root'),

    ###########
    ###########

    # MC 2016
    Sample(2016, "/WW_TuneCUETP8M1_13TeV-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/WW_TuneCUETP8M1_13TeV-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                                            , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/WZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/WZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                                            , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/ZZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/ZZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                                            , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    ###########
    Sample(2016, "/WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                        , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v2/MINIAODSIM"                                   , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                       , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v1/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    ###########
    Sample(2016, "/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                               , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                              , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                              , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                              , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                              , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v2/MINIAODSIM"                              , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext2-v2/MINIAODSIM"                              , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v2/MINIAODSIM"                                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    ###########
    Sample(2016, "/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v1/MINIAODSIM"                      , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3_ext1-v1/MINIAODSIM"                  , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"          , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    Sample(2016, "/ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"      , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),
    ###########
    Sample(2016, "/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/RunIISummer16MiniAODv3-PUMoriond17_94X_mcRun2_asymptotic_v3-v1/MINIAODSIM"                                                   , 'myNanoProdMc2016_NANO.py', 'myNanoProdMc2016_NANO.root'),

    # data 2016
    Sample(2016, "/Tau/Run2016B-17Jul2018_ver2-v1/MINIAOD"           , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/Tau/Run2016C-17Jul2018-v1/MINIAOD"                , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/Tau/Run2016D-17Jul2018-v1/MINIAOD"                , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/Tau/Run2016E-17Jul2018-v1/MINIAOD"                , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/Tau/Run2016F-17Jul2018-v1/MINIAOD"                , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/Tau/Run2016G-17Jul2018-v1/MINIAOD"                , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/Tau/Run2016H-17Jul2018-v1/MINIAOD"                , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    ###########
    Sample(2016, "/SingleMuon/Run2016B-17Jul2018_ver2-v1/MINIAOD"    , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleMuon/Run2016C-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleMuon/Run2016D-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleMuon/Run2016E-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleMuon/Run2016F-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleMuon/Run2016G-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleMuon/Run2016H-17Jul2018-v1/MINIAOD"         , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    ###########
    Sample(2016, "/SingleElectron/Run2016B-17Jul2018_ver2-v1/MINIAOD", 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleElectron/Run2016C-17Jul2018-v1/MINIAOD"     , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleElectron/Run2016D-17Jul2018-v1/MINIAOD"     , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleElectron/Run2016E-17Jul2018-v1/MINIAOD"     , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleElectron/Run2016F-17Jul2018-v1/MINIAOD"     , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleElectron/Run2016G-17Jul2018-v1/MINIAOD"     , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
    Sample(2016, "/SingleElectron/Run2016H-17Jul2018-v1/MINIAOD"     , 'myNanoProdData2016_NANO.py', 'myNanoProdData2016_NANO.root'),
]






