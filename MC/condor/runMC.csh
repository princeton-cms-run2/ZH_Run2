mkdir DY1JetsToLL
cd DY1JetsToLL
python ../makeCondor.py --dataSet /DY1JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName DY1JetsToLL --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir DY2JetsToLL
cd DY2JetsToLL
python ../makeCondor.py --dataSet /DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName DY2JetsToLL --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir DY3JetsToLL
cd DY3JetsToLL
python ../makeCondor.py --dataSet /DY3JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM --nickName DY3JetsToLL --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir DY4JetsToLL
cd DY4JetsToLL
python ../makeCondor.py --dataSet /DY4JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_v2_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName DY4JetsToLL --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir DYJetsToLL
cd DYJetsToLL
python ../makeCondor.py --dataSet /DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/CMSSW_10_2_9-102X_mc2017_realistic_v6_RelVal_nanoaod94X2017-v2/DQMIO --nickName DYJetsToLL --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir EWKWPlus2Jets
cd EWKWPlus2Jets
python ../makeCondor.py --dataSet /EWKWPlus2Jets_WToLNu_M-50_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName EWKWPlus2Jets --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir EWKZ2JetsLL
cd EWKZ2JetsLL
python ../makeCondor.py --dataSet /EWKZ2Jets_ZToLL_M-50_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName EWKZ2JetsLL --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir EWKZ2JetsNuNu
cd EWKZ2JetsNuNu
python ../makeCondor.py --dataSet /EWKZ2Jets_ZToNuNu_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName EWKZ2JetsNuNu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir GluGluHToTauTau
cd GluGluHToTauTau
python ../makeCondor.py --dataSet /GluGluHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM --nickName GluGluHToTauTau --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ST1
cd ST1
python ../makeCondor.py --dataSet /ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ST1 --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ST2
cd ST2
python ../makeCondor.py --dataSet /ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ST2 --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ST3
cd ST3
python ../makeCondor.py --dataSet /ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ST3 --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ST4
cd ST4
python ../makeCondor.py --dataSet /ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ST4 --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ttHToTauTau
cd ttHToTauTau
python ../makeCondor.py --dataSet /ttHToTauTau_M125_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ttHToTauTau --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir TTTo2L2Nu
cd TTTo2L2Nu
python ../makeCondor.py --dataSet /TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName TTTo2L2Nu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir TTToHadronic
cd TTToHadronic
python ../makeCondor.py --dataSet /TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName TTToHadronic --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir TTToSemiLeptonic
cd TTToSemiLeptonic
python ../makeCondor.py --dataSet /TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName TTToSemiLeptonic --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir VBFHToTauTau
cd VBFHToTauTau
python ../makeCondor.py --dataSet /VBFHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName VBFHToTauTau --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir W1JetsToLNu
cd W1JetsToLNu
python ../makeCondor.py --dataSet /W1JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName W1JetsToLNu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir W2JetsToLNu
cd W2JetsToLNu
python ../makeCondor.py --dataSet /W2JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName W2JetsToLNu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir W3JetsToLNu
cd W3JetsToLNu
python ../makeCondor.py --dataSet /W3JetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName W3JetsToLNu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WJetsToLNu
cd WJetsToLNu
python ../makeCondor.py --dataSet /WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM --nickName WJetsToLNu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WminusHToTauTau
cd WminusHToTauTau
python ../makeCondor.py --dataSet /WminusHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WminusHToTauTau --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WplusHToTauTau
cd WplusHToTauTau
python ../makeCondor.py --dataSet /WplusHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WplusHToTauTau --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WWTo2L2Nu
cd WWTo2L2Nu
python ../makeCondor.py --dataSet /WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WWTo2L2Nu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WWTo4Q
cd WWTo4Q
python ../makeCondor.py --dataSet /WWTo4Q_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WWTo4Q --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WWToLNuQQ
cd WWToLNuQQ
python ../makeCondor.py --dataSet /WWToLNuQQ_NNPDF31_TuneCP5_13TeV-powheg-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WWToLNuQQ --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WZ
cd WZ
python ../makeCondor.py --dataSet /WZ_TuneCP5_13TeV-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WZ --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WZTo1L1Nu2Q
cd WZTo1L1Nu2Q
python ../makeCondor.py --dataSet /WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WZTo1L1Nu2Q --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WZTo1L3Nu
cd WZTo1L3Nu
python ../makeCondor.py --dataSet /WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8_v2/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WZTo1L3Nu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WZTo2L2Q
cd WZTo2L2Q
python ../makeCondor.py --dataSet /WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WZTo2L2Q --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir WZTo3LNu
cd WZTo3LNu
python ../makeCondor.py --dataSet /WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName WZTo3LNu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ZHToTauTau
cd ZHToTauTau
python ../makeCondor.py --dataSet /ZHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ZHToTauTau --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ZZ
cd ZZ
python ../makeCondor.py --dataSet /ZZ_TuneCP5_13TeV-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ZZ --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ZZTo2L2Nu
cd ZZTo2L2Nu
python ../makeCondor.py --dataSet /ZZTo2L2Nu_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ZZTo2L2Nu --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ZZTo2L2Q
cd ZZTo2L2Q
python ../makeCondor.py --dataSet /ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM --nickName ZZTo2L2Q --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
mkdir ZZTo4L
cd ZZTo4L
python ../makeCondor.py --dataSet /ZZTo4L_13TeV_powheg_pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6_ext1-v1/NANOAODSIM --nickName ZZTo4L --mode anaXRD
cd /uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/MC/condor
