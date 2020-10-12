#
# estimate fake rate for irreducilble backgrounds 
#

import ROOT
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, TLegend, TAxis, TGraphAsymmErrors,  gInterpreter
from ROOT import gSystem, gStyle, gROOT, kTRUE, TMatrixD
from math import sqrt, sin, cos, pi
from array import array
from ROOT import RooWorkspace as WS
import os
import os.path
import sys
#sys.path.append('../modules/')
import ScaleFactor as SF
sys.path.append('./TauPOG')
from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool

gROOT.SetBatch(True)

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    #parser.add_argument("-i","--inFileRoot",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-f","--inFileName",default='./MCsamples_2017_small.csv',help="File to be analyzed.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    parser.add_argument("-l","--LTcut",default=0,type=float,help="LT cut")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="Selection")
    parser.add_argument("-r","--region",default='SS',type=str,help="OS or SS")
    parser.add_argument("-j", "--inSystematics",type=str, default='',help='systematic variation')
    parser.add_argument("-i", "--isLocal",type=str, default=0,help='local or condor')
    parser.add_argument("-t", "--gType",type=str, default='',help='type : data, Signal, Other')
    return parser.parse_args()


def OverFlow(htest) :

    nb = htest.GetNbinsX()

    lastbincont = htest.GetBinContent(nb)
    overbincont = htest.GetBinContent(nb+1)
    lastbinerror = htest.GetBinError(nb)
    overbinerror = htest.GetBinError(nb+1)

    htest.SetBinContent(nb, 0)
    htest.SetBinContent(nb, lastbincont+overbincont)
    htest.SetBinContent(nb+1, 0.)
    htest.SetBinError(nb, sqrt(lastbinerror*lastbinerror + overbinerror*overbinerror))
    htest.SetBinError(nb+1, 0.)




def search(values, searchFor):
    for k in values:
        for v in values[k]:
            if searchFor==v:
                return True
    return False

class dupeDetector() :
    
    def __init__(self):
        self.nCalls = 0 
        self.runEventList = []
        self.DuplicatedEvents = []

    def checkEvent(self,entry,cat) :
        self.nCalls += 1 
        #runEvent = "{0:d}:{1:d}:{2:d}".format(entry.lumi,entry.run,entry.evt)
        runEvent = "{0:d}:{1:d}:{2:d}:{3:s}".format(entry.lumi,entry.run,entry.evt,cat)
        if runEvent in self.runEventList :
            #print("Event in list: runEventList={0:s}".format(str(self.runEventList)))
            self.DuplicatedEvents.append(runEvent)
	    #print 'duplicated event', entry.lumi,entry.run,entry.evt
            return True
        else :
            self.runEventList.append(runEvent)
            #print("New event: runEventList={0:s}".format(str(self.runEventList)))
            return False

        print 'print report', self.DuplicatedEvents

    def printSummary(self) :
        print("Duplicate Event Summary: Calls={0:d} Unique Events={1:d}".format(self.nCalls,len(self.runEventList)))
        return


def OverFlow(htest) :

    nb = htest.GetNbinsX()

    lastbincont = htest.GetBinContent(nb)
    overbincont = htest.GetBinContent(nb+1)
    lastbinerror = htest.GetBinError(nb)
    overbinerror = htest.GetBinError(nb+1)

    htest.SetBinContent(nb, 0)
    htest.SetBinContent(nb, lastbincont+overbincont)
    htest.SetBinContent(nb+1, 0.)
    htest.SetBinError(nb, sqrt(lastbinerror*lastbinerror + overbinerror*overbinerror))
    htest.SetBinError(nb+1, 0.)


    #return htest
campaign = {2016:'2016Legacy', 2017:'2017ReReco', 2018:'2018ReReco'}

iso_mu = 0.15
iso_el = 0.15

tt_tau_vse = 4
tt_tau_vsmu = 1

et_tau_vse = 32
et_tau_vsmu = 1

mt_tau_vse = 4
mt_tau_vsmu = 8

args = getArgs()
era = str(args.year)
nBins, xMin, xMax = 10, 0., 200.
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}
preCutOff = True
tights = True
et = TLorentzVector()
mut = TLorentzVector()
ptMiss = TLorentzVector() 

isW = False
isDY = False
muonMass = 0.106
electronMass = 0.000511


MetV = TLorentzVector()
tauV3 = TLorentzVector()
tauV4 = TLorentzVector()
L1 = TLorentzVector()
L2 = TLorentzVector()
L1.SetXYZM(0,0,0,0)
L2.SetXYZM(0,0,0,0)
MetV.SetXYZM(0,0,0,0)
tauV3.SetXYZM(0,0,0,0)
tauV4.SetXYZM(0,0,0,0)

islocal=False
if str(args.isLocal) == '1' or str(args.isLocal) =='yes' : islocal=True

gInterpreter.ProcessLine(".include .")
'''
for baseName in ['./HTT-utilities/RecoilCorrections/src/MEtSys', './HTT-utilities/RecoilCorrections/src/RecoilCorrector'] : 
for baseName in ['./HTT-utilities/RecoilCorrections/src/MEtSys', './HTT-utilities/RecoilCorrections/src/RecoilCorrector'] : 
    if os.path.isfile("{0:s}_cc.so".format(baseName)) :
	gInterpreter.ProcessLine(".L {0:s}_cc.so".format(baseName))
    else :
	gInterpreter.ProcessLine(".L {0:s}.cc++".format(baseName))   
	# .L is not just for .so files, also .cc
'''

if era == '2016' : 
    weights = {'lumi':35.92, 'tauID_w' :0.87, 'tauES_DM0' : -0.6, 'tauES_DM1' : -0.5,'tauES_DM10' : 0.0, 'mutauES_DM0' : -0.2, 'mutauES_DM1' : 1.5, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 9.5}

    TriggerSF={'dir' : './tools/ScaleFactors/TriggerEffs/', 'fileMuon' : 'Muon/SingleMuon_Run2016_IsoMu24orIsoMu27.root', 'fileElectron' : 'Electron/SingleElectron_Run2016_Ele25orEle27.root'}
    LeptonSF={'dir' : './tools/ScaleFactors/LeptonEffs/', 'fileMuon0p2' : 'Muon/Muon_Run2016_IdIso_0p2.root', 'fileMuon0p15' : 'Muon/Muon_Run2016_IdIso_0p15.root', 'fileElectron0p1' : 'Electron/Electron_Run2016_IdIso_0p1.root',  'fileElectron0p15' : 'Electron/Electron_Run2016_IdIso_0p15.root'}
    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_2016Legacy.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2016.root'}


if era == '2017' : 
    weights = {'lumi':41.53, 'tauID_w' :0.89, 'tauES_DM0' : 0.7, 'tauES_DM1' : -0.2,'tauES_DM10' : 0.1, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.3, 'eltauES_DM1' : 3.6}


    TriggerSF={'dir' : './tools/ScaleFactors/TriggerEffs/', 'fileMuon' : 'Muon/SingleMuon_Run2017_IsoMu24orIsoMu27.root', 'fileElectron' : 'Electron/SingleElectron_Run2017_Ele32orEle35.root'}
    LeptonSF={'dir' : './tools/ScaleFactors/LeptonEffs/', 'fileMuon0p2' : 'Muon/Muon_Run2017_IdIso_0p2.root', 'fileMuon0p15' : 'Muon/Muon_Run2017_IdIso_0p15.root', 'fileElectron0p1' : 'Electron/Electron_Run2017_IdIso_0p1.root',  'fileElectron0p15' : 'Electron/Electron_Run2017_IdIso_0p15.root'}
    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_2017ReReco.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2017.root'}

if era == '2018' : 
    weights = {'lumi':59.74, 'tauID_w' :0.90, 'tauES_DM0' : -1.3, 'tauES_DM1' : -0.5,'tauES_DM10' : -1.2, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 0.0}

    TriggerSF={'dir' : './tools/ScaleFactors/TriggerEffs/', 'fileMuon' : 'Muon/SingleMuon_Run2018_IsoMu24orIsoMu27.root', 'fileElectron' : 'Electron/SingleElectron_Run2018_Ele32orEle35.root'}
    LeptonSF={'dir' : './tools/ScaleFactors/LeptonEffs/', 'fileMuon0p2' : 'Muon/Muon_Run2018_IdIso_0p2.root', 'fileMuon0p15' : 'Muon/Muon_Run2018_IdIso_0p15.root', 'fileElectron0p1' : 'Electron/Electron_Run2018_IdIso_0p1.root',  'fileElectron0p15' : 'Electron/Electron_Run2018_IdIso_0p15.root'}
    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_2018ReReco.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2018.root'}

'''
if era == '2016' : recoilCorrector  = ROOT.RecoilCorrector("./Type1_PFMET_Run2016BtoH.root");
if era == '2017' : recoilCorrector  = ROOT.RecoilCorrector("./Type1_PFMET_2017.root");
if era == '2018' : recoilCorrector  = ROOT.RecoilCorrector("./TypeI-PFMet_Run2018.root");
'''
finWS=("{0:s}{1:s}".format(WorkSpace['dir'],WorkSpace['fileWS']))
fInws=TFile(finWS, 'read') 
fInws.cd()


#ROOT.gROOT.LoadMacro("CrystalBallEfficiency.cxx+")
wspace = WS.RooWorkspace("w")
wspace=fInws.Get("w")


scaleSyst = ["Central"]

scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']

for i, sys in enumerate(scale) :
    scaleSyst.append(sys+'Up')
    scaleSyst.append(sys+'Down')


#listsyst=['njets', 'nbtag', 'jpt', 'jeta', 'jflavour','MET_T1_pt', 'MET_T1_phi', 'MET_pt', 'MET_phi', 'MET_T1Smear_pt', 'MET_T1Smear_phi']

jes=['jesAbsolute', 'jesAbsolute{0:s}'.format(str(era)), 'jesBBEC1', 'jesBBEC1{0:s}'.format(str(era)), 'jesEC2', 'jesEC2{0:s}'.format(str(era)), 'jesFlavorQCD', 'jesHF', 'jesHF{0:s}'.format(str(era)), 'jesRelativeBal', 'jesRelativeSample{0:s}'.format(str(era)), 'jesHEMIssue', 'jesTotal', 'jer']

jesSyst=[]
for i, sys in enumerate(jes) :
    jesSyst.append(sys+'Up')
    jesSyst.append(sys+'Down')


otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')


#jesSyst hold the jes systematic  - we need njets, nbtag, nflavor, jpt

sysall = scaleSyst+jesSyst+OtherSyst

print 'systematics', sysall


if str(args.inSystematics) not in sysall : 
    print 'the input ', args.inSystematics, ' systematic does not exist, choose on from:', sysall
    #exit() 

systematic=str(args.inSystematics)
#systematic='Central'


########## initializing triggers

wpp = {'1':'VVVLoose','2':'VVLoose', '4':'VLoose', '8':'Loose', '16':'Medium','32':'Tight','64':'VTight','128':'VVTight'}

'''
sf_MuonTrig = SF.SFs()
sf_MuonTrig.ScaleFactor("{0:s}{1:s}".format(TriggerSF['dir'],TriggerSF['fileMuon']))
sf_EleTrig = SF.SFs()
sf_EleTrig.ScaleFactor("{0:s}{1:s}".format(TriggerSF['dir'],TriggerSF['fileElectron']))

sf_MuonId = SF.SFs()
sf_MuonId.ScaleFactor("{0:s}{1:s}".format(LeptonSF['dir'],LeptonSF['fileMuon0p2']))
sf_ElectronId = SF.SFs()
sf_ElectronId.ScaleFactor("{0:s}{1:s}".format(LeptonSF['dir'],LeptonSF['fileElectron0p15']))
'''

wpp = 'Medium'
'''
if str(args.bruteworkingPoint=='16') : wpp = 'Medium'
if str(args.bruteworkingPoint=='32') : wpp = 'Tight'
if str(args.bruteworkingPoint=='64') : wpp = 'VTight'
if str(args.bruteworkingPoint=='128') : wpp = 'VVTight'
'''


tauSFTool = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSjet',wpp)
testool = TauESTool(campaign[args.year],'DeepTau2017v2p1VSjet', TESSF['dir'])
festool = TauESTool(campaign[args.year],'DeepTau2017v2p1VSjet')

#antiEleSFToolVVL = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','VVLoose')
#antiMuSFToolVL  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','VLoose')
antiEleSFToolVL = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','VLoose')
antiMuSFToolVL  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','VLoose')

antiEleSFToolT = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','Tight')
antiMuSFToolT  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','Tight')




# use this utility class to screen out duplicate events
DD = dupeDetector()

# open an output file
#fin = 'FakeRates_{0:s}_{1:s}_nbtag_precut.root'.format(str(args.year),str(args.region))
fin = 'FakeRates_test.root'
fOut = TFile(fin, 'recreate' )

# create histograms
hList = ['e_et','t_et','m_mt','t_mt','t1_tt','t2_tt', 'e_em', 'm_em']
hList = ['e_et','t_et','m_mt','t_mt','t1_tt','t2_tt', 'e_em', 'm_em', 'm_ll','e_ll','t_ll']
hModes = ['0','1','10','11']

hBase, hTight = {}, {}
hBaseMode, hTightMode = {}, {}
hBasePrompt, hTightPrompt = {}, {}
hBasePromptMode, hTightPromptMode = {}, {}
hBasenoPrompt, hTightnoPrompt = {}, {}
hBasenoPromptMode, hTightnoPromptMode = {}, {}

'''
groups = ['ZZ','WJets','Rare','Top','DY', 'WWIncl', 'WZincl']
groups = ['Other','Top','DY','WZ','ZZ']

groups = ['Other','ZZ','ggZH','WH','qqZH'] ##accroding to _paper.csv
'''
nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}

groups = []
groupss = []

groupss.append(str(args.gType))
groups.append(str(args.gType))

#if 'data' in str(args.gType) : 
#    groups = ['Reducible','fakes','f1', 'f2','data']
#    groupss = ['Reducible','fakes','f1', 'f2','data']


for group in groupss :
    nickNames[group] = []
print groups, groupss, nickNames


WP=['16','32','64','128']

#nBins = 9
#Bins = [0,10,15,20,25,30,35,40,50,100]

nBins = 5
Bins = [0,10,20,30,40,100]

for h in hList :
    hName = "{0:s}Base".format(h)
    hBase[h] = TH1D(hName,hName,nBins, array('d',Bins))
    
    hTight[h] = {}
    for wp in WP : 
	hName = "{0:s}_{1:s}Tight".format(h,wp)
	hTight[h][wp] = TH1D(hName,hName,nBins, array('d',Bins))
 

print hList

#groupss = ['data','Other','ZZ','ggZH','WH','qqZH']

for group in groupss :
    hBaseMode[group], hTightMode[group] = {}, {}

    for h in hList :
        hBaseMode[group][h], hTightMode[group][h] = {}, {}

        for m in hModes :
	    hName = "{0:s}_{1:s}_{2:s}Mode_Base".format(group,h,m)
	    hBaseMode[group][h][m] = TH1D(hName,hName,nBins,array('d',Bins))

	    hTightMode[group][h][m] = {}

            for wp in WP : 
	        hName = "{0:s}_{1:s}_{2:s}_{3:s}Mode_Tight".format(group,h,m,wp)
		hTightMode[group][h][m][wp] = TH1D(hName,hName,nBins,array('d',Bins))

isTight1=False
isTight2=False
for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    if '#' in vals[0] : continue
    if 'data' in vals[0] :
	for era in [str(args.year)] :
	#for period in ['SingleMuon', 'EGamma', 'MuonEG'] :
	    for dataset in ['data'] :
                if islocal :   inFileRoot = '../data/condor/{0:s}//data_{1:s}/data_{1:s}.root'.format(args.selection,era)
		else : inFileRoot = 'data_{0:s}.root'.format(era)
		#inFileRoot = './data/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}_{3:s}.root'.format(args.selection,dataset,era, period)
		print("Opening {0:s}".format(inFileRoot)) 
		inFile = TFile.Open(inFileRoot)
		inFile.cd()
		inTree = inFile.Get("Events")
		nentries = inTree.GetEntries()
		for i, e in enumerate(inTree) :
	 
		    #if i > 1000 : continue
                    if i % 5000 ==0: print i, ' from ', nentries
		    cat = cats[e.cat]
		    if e.pt_1<10 : continue
		    if e.pt_2<10 : continue
		    if e.pt_3<10 : continue
		    if e.pt_4<10 : continue

                    try :
			metpt = e.met
			metphi = e.metphi
		        nbtag = getattr(e, 'nbtag_nom', None)
	 	        njets = getattr(e, 'njets_nom', None)

		    except AttributeError :
			met = e.met
			metphi = e.metphi
			njets = e.njets
			nbtag = e.nbtag


		    # impose any common selection criteria here
		    # include only same sign events 
		    if e.isTrig_1 == 0 : continue  
		    if e.q_1*e.q_2 > 0. : continue
		    if args.region == 'SS' and  e.q_3*e.q_4 < 0. : continue
		    if args.region == 'OS' and  e.q_3*e.q_4 > 0. : continue
		    if args.region == 'SS'and nbtag > 0 : continue
		    if args.region == 'OS'and nbtag < 1 : continue
		    
		    #if abs(e.dZ_3) > 0.05 or abs(e.dZ_4) > 0.05 : continue
		    if cat[:2] == 'mm' and  (e.iso_1 > iso_mu or e.iso_2 > iso_mu) : continue
		    if cat[:2] == 'mm' :
			if  (e.isGlobal_1 < 1 and e.isTracker_1 < 1) or e.mediumId_1 < 1 : continue
			if  (e.isGlobal_2 < 1 and e.isTracker_2 < 1) or e.mediumId_2 < 1 : continue
		    if cat[:2] == 'ee' and  (e.iso_1 > iso_el or e.iso_2 > iso_el) : continue
		    if cat[:2] == 'ee' and  (e.Electron_mvaFall17V2noIso_WP90_1 < 1 or e.Electron_mvaFall17V2noIso_WP90_2 <1) : continue

                    '''
		    if e.isTrig_1 != 0: 

			if e.isTrig_1 == -1 and e.isTrig_2 == 0: 
			#if e.isTrig_1 == -1 : 
			    if cat[:2] == 'mm' and e.pt_2 < 29 : continue
			    if cat[:2] == 'ee' and era == '2016' and e.pt_2 < 29 : continue
			    if cat[:2] == 'ee' and era != '2016' and e.pt_2 < 37 : continue

			# both fired the trigger _isTrig_2 = 1
			
			if e.isTrig_2 == 1 : 
			    if cat[:2] == 'mm' and e.pt_1 < 29 and e.pt_2 < 29: continue
			    if cat[:2] == 'ee' and era == '2016' and e.pt_1 <  29 and  e.pt_2 < 29 : continue
			    if cat[:2] == 'ee' and era != '2016' and e.pt_1 < 37 and e.pt_2 < 37 : continue
		
		    if e.isDoubleTrig!=0 and e.isTrig_1 == 0 : #the DoubleLepton trigger was fired but not the SingleLepton

			if cat[:2] == 'mm' and (e.pt_1 < 19 or e.pt_2 < 10): continue
			if cat[:2] == 'ee' and (e.pt_1 < 25 or e.pt_2 < 14): continue

                    '''

		    # skip duplicate events
		    if DD.checkEvent(e,cat) : continue 

		    et.SetPtEtaPhiM(e.pt_3,e.eta_3,e.phi_3,0.000511)
		    ptMiss.SetPtEtaPhiM(metpt,0.,metphi,0.)
		    eMET = et + ptMiss

		    preCut =  eMET.Mt() < 40. 
		    mut.SetPtEtaPhiM(e.pt_3,e.eta_3,e.phi_3,0.102)
		    muMET = mut + ptMiss
		    preCutt =  muMET.Mt() < 40. 

		    if cat[2:] == 'et' :

			if e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0 : isTight1 = True
			if e.idDeepTau2017v2p1VSjet_4 >= wp  and e.idDeepTau2017v2p1VSe_4 >= et_tau_vse  and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu : isTight2= True

			# apply transverse mass cut on electron-MET system
                        if tights or  isTight2:
			    if preCutOff or preCut : 
				hBase['e_et'].Fill(e.pt_3)
				hBase['e_ll'].Fill(e.pt_3)

			    for wp in WP : 
				if e.Electron_mvaFall17V2noIso_WP90_3 >0  and  e.iso_3 < iso_el : 
				    hTight['e_et'][wp].Fill(e.pt_3)
				    hTight['e_ll'][wp].Fill(e.pt_3)

                        if tights or  isTight1:
			    hBase['t_et'].Fill(e.pt_4)
			    hBase['t_ll'].Fill(e.pt_4)
			    if e.decayMode_4 != -1 : 
				hBaseMode['data']['t_et'][str(e.decayMode_4)].Fill(e.pt_4)
				hBaseMode['data']['t_ll'][str(e.decayMode_4)].Fill(e.pt_4)

			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_4 >= wp  and e.idDeepTau2017v2p1VSe_4 >= et_tau_vse  and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu : 
				hTight['t_et'][wp].Fill(e.pt_4)
				hTight['t_ll'][wp].Fill(e.pt_4)
				if e.decayMode_4 != -1 : 
				    hTightMode['data']['t_et'][str(e.decayMode_4)][wp].Fill(e.pt_4)
				    hTightMode['data']['t_ll'][str(e.decayMode_4)][wp].Fill(e.pt_4)
			    
		    if cat[2:] == 'mt' :

			if e.iso_3 < iso_mu and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) and e.mediumId_3 > 0: isTight1 = True
			if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse : isTight2= True


			# apply transverse mass cut on muon-MET system
			if preCutOff or preCutt and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) : 
                        #if tights or  isTight2:
			    if preCutOff or preCutt :
				hBase['m_mt'].Fill(e.pt_3)
				hBase['m_ll'].Fill(e.pt_3)

			    for wp in WP :
				 
				if e.iso_3 < iso_mu and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) and e.mediumId_3 > 0 : 
				    hTight['m_mt'][wp].Fill(e.pt_3)
				    hTight['m_ll'][wp].Fill(e.pt_3)

                        if tights or  isTight1:
			    hBase['t_mt'].Fill(e.pt_4)
			    hBase['t_ll'].Fill(e.pt_4)
			    if e.decayMode_4 != -1 : 
				hBaseMode['data']['t_mt'][str(e.decayMode_4)].Fill(e.pt_4)
				hBaseMode['data']['t_ll'][str(e.decayMode_4)].Fill(e.pt_4)

			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse:
				hTight['t_mt'][wp].Fill(e.pt_4)
				hTight['t_ll'][wp].Fill(e.pt_4)
				if e.decayMode_4 != -1 : 
				    hTightMode['data']['t_mt'][str(e.decayMode_4)][wp].Fill(e.pt_4)
				    hTightMode['data']['t_ll'][str(e.decayMode_4)][wp].Fill(e.pt_4)

		    if cat[2:] == 'tt' :
			#H_LT = e.pt_3 + e.pt_4
			#if not preCutOff and H_LT < args.LTcut : continue
			if e.idDeepTau2017v2p1VSjet_3 >= wp and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse: isTight1= True
			if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse: isTight2= True

			if tights or isTight2 : 
			    hBase['t1_tt'].Fill(e.pt_3)
			    if e.decayMode_3 != -1 : 
				hBaseMode['data']['t1_tt'][str(e.decayMode_3)].Fill(e.pt_3)
			    for wp in WP : 
				if e.idDeepTau2017v2p1VSjet_3 >= wp and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse:     
				    hTight['t1_tt'][wp].Fill(e.pt_3)
				    if e.decayMode_3 != -1 : 
					hTightMode['data']['t1_tt'][str(e.decayMode_3)][wp].Fill(e.pt_3)


			if tights or  isTight1 : 
			    hBase['t2_tt'].Fill(e.pt_4)
			    if e.decayMode_4 != -1 : 
				hBaseMode['data']['t2_tt'][str(e.decayMode_4)].Fill(e.pt_4)

			    for wp in WP : 
				if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse :
				    hTight['t2_tt'][wp].Fill(e.pt_4)
				    if e.decayMode_4 != -1 : 
					hTightMode['data']['t2_tt'][str(e.decayMode_4)][wp].Fill(e.pt_4)


		    if cat[2:] == 'em' :

			if e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0 : isTight1 = True
			if e.iso_4 < iso_mu and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0) and e.mediumId_4 > 0: isTight2 = True

			mut.SetPtEtaPhiM(e.pt_4,e.eta_4,e.phi_4,0.102)
			muMET = mut + ptMiss
			preCutt =  muMET.Mt() < 40.
                        if tights or  isTight2 :
			    if preCutOff or preCut : 
				hBase['e_em'].Fill(e.pt_3)
				hBase['e_ll'].Fill(e.pt_3)
			    for wp in WP : 
				if e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0: 
				    hTight['e_em'][wp].Fill(e.pt_3)
				    hTight['e_ll'][wp].Fill(e.pt_3)

			if preCutOff or preCutt and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0): 
			#if tights or  isTight1:
			    if preCutOff or preCutt :
				hBase['m_em'].Fill(e.pt_4)
				hBase['m_ll'].Fill(e.pt_4)

			    for wp in WP : 
				if e.iso_4 < iso_mu and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0) and e.mediumId_4 > 0 : 
				    hTight['m_em'][wp].Fill(e.pt_4)
				    hTight['m_ll'][wp].Fill(e.pt_4)

		    
		inFile.Close()

	DD.printSummary()

#do the Overflow
#for h in hList :
#    OverFlow(hBase[h])
#    for wp in WP : OverFlow(hTight[h][wp])



Pblumi = 1000.


WNJetsXsecs = [40322.3]  #LO for 0-jet
DYNJetsXsecs = [4738.53]  #LO  for 0-jet

WJets_kfactor = 1.166
DY_kfactor = 1.137

WIncl_xsec = 52760*WJets_kfactor ##LO *kfactor inclusive
DYIcl_xsec = 6077.22 ##NNLO inclusive


WxGenweightsArr = []
DYxGenweightsArr = []

print ' Will use the ' ,args.inFileName
for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    if '#' in vals[0] : continue
    if vals[0][0] == "W" and  "JetsToLNu" in vals[0][2:] and 'TWJ' not in vals[0]:
        WNJetsXsecs.append(float(vals[2]))
        filein = '{1:s}_{2:s}.root'.format(args.selection,vals[0],era)
        fIn = TFile.Open(filein,"READ")
        WxGenweightsArr.append(fIn.Get("hWeights").GetSumOfWeights())
        #DYxGenweightsArr.append(fIn.Get("DY"+str(i)+"genWeights").GetSumOfWeights())


    if vals[0][:2] == "DY" and "JetsToLL" in vals[0][3:] and 'M10to50' not in vals[0] and 'TWJ' not in vals[0]:
        DYNJetsXsecs.append(float(vals[2]))
        filein = '{1:s}_{2:s}.root'.format(args.selection,vals[0],era)
        fIn = TFile.Open(filein,"READ")
        DYxGenweightsArr.append(fIn.Get("hWeights").GetSumOfWeights())
        #DYxGenweightsArr.append(fIn.Get("DY"+str(i)+"genWeights").GetSumOfWeights())



WIncl_only = True
DYIncl_only = True

for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    if 'data' in vals[0]: continue
    if '#' in vals[0] : continue
    nickName = vals[0]
    group = vals[1]
    if 'Signal' not in group and 'data' not in group: nickNames[group].append(nickName)
    #xsec[nickName] = float(vals[2])
    if 'DY1' in nickName or 'DY2' in nickName or 'DY3' in nickName or 'DY4' in nickName : 
        DYIncl_only = False
        print 'using DY+Njet samples'
    if 'W1' in nickName or 'W2' in nickName or 'W3' in nickName or 'W4' in nickName : 
        WIncl_only = False
        print 'using W+Njet samples'
    if '*' in vals[2] : 
        value1, value2 = map(float, vals[2].split("*"))
        xsec[nickName] = float(value1*value2)
    elif '+' in vals[2] : 
        value1, value2 = map(float, vals[2].split("+"))
        xsec[nickName] = float(value1+value2)
    else : xsec[nickName] = float(str(vals[2]))

    if '+' in vals[4] : 
	value1, value2 = map(float, vals[4].split("+"))
	totalWeight[nickName] = float(value1+value2)
    else : totalWeight[nickName] = float(vals[4])

    if islocal :    filein = '../MC/condor/{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.selection,vals[0],era)
    else : filein = '{1:s}_{2:s}.root'.format(args.selection,vals[0],era)
    fIn = TFile.Open(filein,"READ")
    #totalWeight[nickName] = float(fIn.Get("hWeights").GetSumOfWeights())
    sampleWeight[nickName]= Pblumi*weights['lumi']*xsec[nickName]/totalWeight[nickName]

    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

    #print("{0:100s}  & {1:10.3f} & {2:11.1f} & {3:10.6f}\\\\\\hline".format(
    #     str(vals[6]),xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))
   

print 'done with that============================'


for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i)
    if search(nickNames, nn) and not search (nickNames, 'M10'):
    #if nn in nickName and 'M10' not in nickName:
        sampleWeight[nn] = Pblumi*weights['lumi']/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + DYxGenweightsArr[i-1]/(xsec[nn]*DY_kfactor))
        #print 'DY', totalWeight['DYJetsToLL']/xsec['DYJetsToLL'], DYxGenweightsArr[i-1], 'xsec', xsec[nn], 'weight ? ', sampleWeight[nn]

for i in range(1,5) :
    nn = 'W{0:d}JetsToLNu'.format(i)
    if search(nickNames, nn) : 
    #if nn in nickName  and 'TW' not in nickName: 
        sampleWeight[nn] = Pblumi*weights['lumi']/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + WxGenweightsArr[i-1]/(xsec[nn]*WJets_kfactor))
        #else: sampleWeight[nn] = Pblumi*weights['lumi']/(totalWeight['WJetsToLNuext']/xsec['WJetsToLNuext'] + WNJetsXsecs[i-1]/(xsec[nn]*WJets_kfactor))


print 'NickNames===========================>', nickNames
# create histograms


for group in groups :
    hBasePrompt[group], hTightPrompt[group] = {}, {}
    hBasePromptMode[group], hTightPromptMode[group] = {}, {}
    hBasenoPrompt[group], hTightnoPrompt[group] = {}, {}
    hBasenoPromptMode[group], hTightnoPromptMode[group] = {}, {}

    for h in hList :
	hName = "{0:s}_{1:s}BasePrompt".format(group,h)
	hBasePrompt[group][h] = TH1D(hName,hName,nBins,array('d',Bins))
	hName = "{0:s}_{1:s}BasenoPrompt".format(group,h)
	hBasenoPrompt[group][h] = TH1D(hName,hName,nBins,array('d',Bins))

	hTightPrompt[group][h], hTightnoPrompt[group][h] = {}, {}
        hBasePromptMode[group][h], hTightPromptMode[group][h] = {}, {}
        hBasenoPromptMode[group][h], hTightnoPromptMode[group][h] = {}, {}

        for wp in WP : 
	    print 'creating', group, h, hName
	    hName = "{0:s}_{1:s}_{2:s}TightnoPrompt".format(group,h,wp)
	    hTightnoPrompt[group][h][wp] = TH1D(hName,hName,nBins,array('d',Bins))
	    hName = "{0:s}_{1:s}_{2:s}TightPrompt".format(group,h,wp)
	    hTightPrompt[group][h][wp] = TH1D(hName,hName,nBins,array('d',Bins))

        for m in hModes :
	    hName = "{0:s}_{1:s}_{2:s}Mode_BasePrompt".format(group,h,m)
	    hBasePromptMode[group][h][m] = TH1D(hName,hName,nBins,array('d',Bins))
	    hName = "{0:s}_{1:s}_{2:s}Mode_BasenoPrompt".format(group,h,m)
	    hBasenoPromptMode[group][h][m] = TH1D(hName,hName,nBins,array('d',Bins))

	    hTightPromptMode[group][h][m] = {}
	    hTightnoPromptMode[group][h][m] = {}

            for wp in WP : 
	        hName = "{0:s}_{1:s}_{2:s}_{3:s}Mode_TightPrompt".format(group,h,m,wp)
		hTightPromptMode[group][h][m][wp] = TH1D(hName,hName,nBins,array('d',Bins))
	        hName = "{0:s}_{1:s}_{2:s}_{3:s}Mode_TightnoPrompt".format(group,h,m,wp)
		hTightnoPromptMode[group][h][m][wp] = TH1D(hName,hName,nBins,array('d',Bins))



for group in groups :

    for nickName in nickNames[group] :
	inFileName = '{1:s}_{2:s}.root'.format(args.selection,nickName,str(args.year))
	print("Opening {0:s}".format(inFileName)) 
	inFile = TFile.Open(inFileName)
	inFile.cd()
	tree_ = "Events"

	if systematic in scaleSyst and systematic != 'Central' : tree_ = systematic
	inTree = inFile.Get(tree_)

	nentries = inTree.GetEntries()
	print ''
        print 'will work with', tree_, ' and ', nentries, inTree.GetName(), systematic
	if nentries == 0 : continue


	if 'DY' in nickName : isDY = True
	if 'JetsToLNu' in nickName and 'TW' not in nickName : isW =  True
	
	nEvents, totalWeight = 0, 0.
	DYJets = ('DYJetsToLL' in nickName and 'M10' not in nickName)
	WJets  = ('WJetsToLNu' in nickName and 'TW' not in nickName)

	sWeight = sampleWeight[nickName]

		
	for i, e in enumerate(inTree) :
	    
	    #if i > 1000 : continue

	    # impose any common selection criteria here
	    # include only same sign events 
	    cat = cats[e.cat]
	    trigw = 1.
	    weight=1.
	    lepton_sf = 1.

            if e.pt_1<10 : continue
            if e.pt_2<10 : continue
            if e.pt_3<10 : continue
            if e.pt_4<10 : continue

	    try :
		metpt = e.met
		metphi = e.metphi
		nbtag = getattr(e, 'nbtag_nom', None)
		njets = getattr(e, 'njets_nom', None)

	    except AttributeError :
		met = e.met
		metphi = e.metphi
		njets = e.njets
		nbtag = e.nbtag


	    if e.isTrig_1 == 0 : continue 
	    if e.q_1*e.q_2 > 0. : continue
            if args.region == 'SS' and  e.q_3*e.q_4 < 0. : continue
            if args.region == 'OS' and  e.q_3*e.q_4 > 0. : continue
	    if args.region == 'SS' and nbtag > 0 : continue
            if args.region == 'OS'and nbtag < 1 : continue

	    H_LT = e.pt_3 + e.pt_4
	    #if H_LT > args.LTcut : continue


	    if cat[:2] == 'mm' and  (e.iso_1 > iso_mu or e.iso_2 > iso_mu) : continue
	    if cat[:2] == 'mm' :
                if  (e.isGlobal_1 < 1 and e.isTracker_1 < 1) or e.mediumId_1 < 1 : continue
                if  (e.isGlobal_2 < 1 and e.isTracker_2 < 1) or e.mediumId_2 < 1 : continue
	    if cat[:2] == 'ee' and  (e.iso_1 > iso_el or e.iso_2 > iso_el) : continue
	    if cat[:2] == 'ee' and  (e.Electron_mvaFall17V2noIso_WP90_1 < 1 or e.Electron_mvaFall17V2noIso_WP90_2 <1) : continue


	    #if abs(e.dZ_3) > 0.05 or abs(e.dZ_4) > 0.05 : continue
            '''
            if e.isTrig_1 != 0: 

		if e.isTrig_1 == -1 and e.isTrig_2 == 0: 
		#if e.isTrig_1 == -1 : 
		    if cat[:2] == 'mm' and e.pt_2 < 29 : continue
		    if cat[:2] == 'ee' and era == '2016' and e.pt_2 < 29 : continue
		    if cat[:2] == 'ee' and era != '2016' and e.pt_2 < 37 : continue

		# both fired the trigger _isTrig_2 = 1
		
		if e.isTrig_2 == 1 : 
		    if cat[:2] == 'mm' and e.pt_1 < 29 and e.pt_2 < 29: continue
		    if cat[:2] == 'ee' and era == '2016' and e.pt_1 <  29 and  e.pt_2 < 29 : continue
		    if cat[:2] == 'ee' and era != '2016' and e.pt_1 < 37 and e.pt_2 < 37 : continue
	
	    if e.isDoubleTrig!=0 and e.isTrig_1 == 0 : #the DoubleLepton trigger was fired but not the SingleLepton

		if cat[:2] == 'mm' and (e.pt_1 < 19 or e.pt_2 < 10): continue
		if cat[:2] == 'ee' and (e.pt_1 < 25 or e.pt_2 < 14): continue
            '''

	    if 'data' not in group : 
                weight_pref = e.L1PreFiringWeight_Nom
                if 'prefireup' in systematic.lower() :  weight_pref = e.L1PreFiringWeight_Up
                if 'prefiredown' in systematic.lower() : weight_pref = e.L1PreFiringWeight_Down
		weight = e.weightPUtrue * e.Generator_weight *sWeight * weight_pref

            if systematic in jesSyst :  
		met = getattr(e, 'MET_T1_pt_{0:s}'.format(systematic), None)
		metphi = getattr(e, 'MET_T1_phi_{0:s}'.format(systematic), None)
		njets = getattr(e, 'njets_{0:s}'.format(systematic), None)
		jpt = getattr(e, 'jpt_{0:s}'.format(systematic), None)
		jeta = getattr(e, 'jeta_{0:s}'.format(systematic), None)
		jflavour = getattr(e, 'jflavour_{0:s}'.format(systematic), None)
		nbtag = getattr(e, 'nbtag_{0:s}'.format(systematic), None)


	    tauV3.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
	    tauV4.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)
	    metpt = e.met
	    metphi = e.metphi

	    MetV.SetPx(metpt * cos (metphi))
	    MetV.SetPy(metpt * sin (metphi))
	    met_x = metpt * cos(metphi)
	    met_y = metpt * sin(metphi)
	    metcor = metpt



            '''
	    if WJets and not WIncl_only: 
		if e.LHE_Njets > 0 : sWeight = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)]
                elif e.LHE_Njets == 0 : sWeight = sampleWeight['WJetsToLNu']
		#print 'will now be using ',sWeight, e.LHE_Njets, nickName
	    if DYJets and not DYIncl_only: 
		if e.LHE_Njets > 0 : sWeight = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
		elif e.LHE_Njets == 0  : sWeight = sampleWeight['DYJetsToLL']
		#print 'will now be using ',sWeight, e.LHE_Njets, nickName
	   #recoils 
            
	    njetsforrecoil = njets
	    if (isW)  : njetsforrecoil = njets + 1
	    if isW or isDY :
		boson = TLorentzVector()
		if cat[:2] == 'mm' :  
		    L1.SetPtEtaPhiM(e.pt_1_tr, e.eta_1_tr,e.phi_1_tr,muonMass)
		    L2.SetPtEtaPhiM(e.pt_2_tr, e.eta_2_tr,e.phi_2_tr,muonMass)
		    boson += L1
		    boson += L2

		if cat[:2] == 'ee' :  
		    L1.SetPtEtaPhiM(e.pt_1_tr, e.eta_1_tr,e.phi_1_tr,electronMass)
		    L2.SetPtEtaPhiM(e.pt_2_tr, e.eta_2_tr,e.phi_2_tr,electronMass)
		    boson += L1
		    boson += L2
		mett = recoilCorrector.CorrectByMeanResolution( met_x, met_y, boson.Px(), boson.Py(), boson.Px(), boson.Py(), int(njetsforrecoil))
		metcor = sqrt(mett[0]* mett[0] + mett[1]*mett[1])
		met_x = mett[0]
		met_y = mett[1]
              
            
	    #weight = e.weight * e.Generator_weight *sWeight
	    if 'data' not in group : 

		eff_trig_d_1, eff_trig_d_2 = 1.,1.
		eff_trig_mc_1, eff_trig_mc_2 = 1.,1.

		eff_id_d_1, eff_id_d_2, eff_id_d_3, eff_id_d_4 = 1.,1.,1.,1.
		eff_id_mc_1, eff_id_mc_2, eff_id_mc_3, eff_id_mc_4 = 1.,1.,1.,1.

		#leading firing the trigger
		if e.isTrig_1 == 1 and e.isTrig_2 == 0 : 

		    if cat[:2] == 'mm' :                
			eff_trig_d_1 =  sf_MuonTrig.get_EfficiencyData(e.pt_1,e.eta_1)
			eff_trig_mc_1 =  sf_MuonTrig.get_EfficiencyMC(e.pt_1,e.eta_1)

		    if cat[:2] == 'ee' :                 
			eff_trig_d_1 =  sf_EleTrig.get_EfficiencyData(e.pt_1,e.eta_1)
			eff_trig_mc_1 =  sf_EleTrig.get_EfficiencyMC(e.pt_1,e.eta_1)
		    if eff_trig_mc_1 !=0 :		trigw = float(eff_trig_d_1/eff_trig_mc_1)
		    else : continue

		#subleading firing the trigger
		if e.isTrig_1 == -1 and e.isTrig_2 == 0: 
		    if cat[:2] == 'mm' :                 
			eff_trig_d_2 =  sf_MuonTrig.get_EfficiencyData(e.pt_2,e.eta_2)
			eff_trig_mc_2 =  sf_MuonTrig.get_EfficiencyMC(e.pt_2,e.eta_2)

		    if cat[:2] == 'ee' :                 
			eff_trig_d_2 =  sf_EleTrig.get_EfficiencyData(e.pt_2,e.eta_2)
			eff_trig_mc_2 =  sf_EleTrig.get_EfficiencyMC(e.pt_2,e.eta_2)

		    if eff_trig_mc_2 !=0 :		trigw = float(eff_trig_d_2/eff_trig_mc_2)
		    else : continue


		#both firing the trigger
		if e.isTrig_1 == 1 and e.isTrig_2 == 1 : 
		    if cat[:2] == 'mm' :                 
			eff_trig_d_1 =  sf_MuonTrig.get_EfficiencyData(e.pt_1,e.eta_1)
			eff_trig_mc_1 = sf_MuonTrig.get_EfficiencyMC(e.pt_1,e.eta_1)
			eff_trig_d_2 =  sf_MuonTrig.get_EfficiencyData(e.pt_2,e.eta_2)
			eff_trig_mc_2 = sf_MuonTrig.get_EfficiencyMC(e.pt_2,e.eta_2)

		    if cat[:2] == 'ee' :                 
			eff_trig_d_1 =  sf_EleTrig.get_EfficiencyData(e.pt_1,e.eta_1)
			eff_trig_mc_1 =  sf_EleTrig.get_EfficiencyMC(e.pt_1,e.eta_1)
			eff_trig_d_2 =  sf_EleTrig.get_EfficiencyData(e.pt_2,e.eta_2)
			eff_trig_mc_2 =  sf_EleTrig.get_EfficiencyMC(e.pt_2,e.eta_2)

		    #print '===================>>>>>>>>>>>>>', eff_trig_d_1, eff_trig_mc_1, eff_trig_d_2, eff_trig_mc_2, e.pt_2, e.eta_2, 'Trigerrred ????', e.isTrig_1, e.isTrig_2
		    if eff_trig_mc_1 != 0 and eff_trig_mc_2 == 0  : 	trigw = float(eff_trig_d_1/eff_trig_mc_1)
		    elif eff_trig_mc_1 == 0 and eff_trig_mc_2 != 0  : trigw = float(eff_trig_d_2/eff_trig_mc_2)
		    elif eff_trig_mc_1 == 0 and eff_trig_mc_2 == 0  : continue 
		    else : 	trigw = float(1- (1-eff_trig_d_1/eff_trig_mc_1) * (1-eff_trig_d_2/eff_trig_mc_2))


		#lepton SFs
		if cat[:2] == 'mm' :                 
			eff_id_d_1 =  sf_MuonId.get_EfficiencyData(e.pt_1,e.eta_1)
			eff_id_mc_1 = sf_MuonId.get_EfficiencyMC(e.pt_1,e.eta_1)

			eff_id_d_2 =  sf_MuonId.get_EfficiencyData(e.pt_2,e.eta_2)
			eff_id_mc_2 = sf_MuonId.get_EfficiencyMC(e.pt_2,e.eta_2)

		if cat[:2] == 'ee' :                 
			eff_id_d_1 =  sf_ElectronId.get_EfficiencyData(e.pt_1,e.eta_1)
			eff_id_mc_1 = sf_ElectronId.get_EfficiencyMC(e.pt_1,e.eta_1)

			eff_id_d_2 =  sf_ElectronId.get_EfficiencyData(e.pt_2,e.eta_2)
			eff_id_mc_2 = sf_ElectronId.get_EfficiencyMC(e.pt_2,e.eta_2)

		if cat[2:] == 'mt' :
			eff_id_d_3 =  sf_MuonId.get_EfficiencyData(e.pt_3,e.eta_3)
			eff_id_mc_3 = sf_MuonId.get_EfficiencyMC(e.pt_3,e.eta_3)

		if cat[2:] == 'et' :
			eff_id_d_3 =  sf_ElectronId.get_EfficiencyData(e.pt_3,e.eta_3)
			eff_id_mc_3 = sf_ElectronId.get_EfficiencyMC(e.pt_3,e.eta_3)

		if cat[2:] == 'em' :               
			eff_id_d_3 =  sf_ElectronId.get_EfficiencyData(e.pt_3,e.eta_3)
			eff_id_mc_3 = sf_ElectronId.get_EfficiencyMC(e.pt_3,e.eta_3)
			eff_id_d_4 =  sf_MuonId.get_EfficiencyData(e.pt_4,e.eta_4)
			eff_id_mc_4 = sf_MuonId.get_EfficiencyMC(e.pt_4,e.eta_4)


		leptons_sf = float (eff_id_d_1/eff_id_mc_1 * eff_id_d_2/eff_id_mc_2 * eff_id_d_3/eff_id_mc_3 * eff_id_d_4/eff_id_mc_4)


		weight *= leptons_sf * trigw
		#weight *= trigw
                '''

	    et.SetPtEtaPhiM(e.pt_3,e.eta_3,e.phi_3,0.000511)
	    ptMiss.SetPtEtaPhiM(metpt,0.,metphi,0.)
	    #ptMiss.SetPtEtaPhiM(e.met,0.,e.metphi,0.)
	    eMET = et + ptMiss
	    preCut =  eMET.Mt() < 40.  

	    mut.SetPtEtaPhiM(e.pt_3,e.eta_3,e.phi_3,0.102)
	    muMET = mut + ptMiss
	    preCutt =  muMET.Mt() < 40.  

            weightTID =1.
            if group != 'data' and (cat[2:] == 'et' or cat[2:]  == 'mt' or cat[2:]  == 'tt') :

                # leptons faking taus // muon->tau
                if  cat[2:] == 'et' :

		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  weightTID *= antiEleSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

                if  cat[2:] == 'mt' :

		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  weightTID *= antiMuSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)

		
                if  cat[2:] == 'tt' :
		    #muon faking _3 tau

		    if e.gen_match_3 == 2 or e.gen_match_3 == 4 : weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 : weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

		    if e.gen_match_3 == 1 or e.gen_match_3 == 3 : weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3)
		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 : weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

		if cat[2:] == 'tt' :
                    if e.gen_match_3 == 5 : 
			weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3)

                        if 'Up' in systematic :
                            if 'pt20to25' in systematic and  e.pt_3 > 20 and  e.pt_3 < 25 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Up')
                            if 'pt25to30' in systematic and  e.pt_3 > 25 and  e.pt_3 < 30 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Up')
                            if 'pt30to35' in systematic and  e.pt_3 > 30 and  e.pt_3 < 35 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Up')
                            if 'pt35to40' in systematic and  e.pt_3 > 35 and  e.pt_3 < 40 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Up')
                            if 'ptgt40' in systematic and  e.pt_3 > 40:
			        weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Up')


                        #print 'tesSTOOL', testool.getTES(e.pt_3, e.decayMode_3, e.gen_match_3)


                if  cat[2:] == 'tt'  or cat[2:] == 'mt' or cat[2:] == 'et' :
		    if e.gen_match_4 == 5 : 
			weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4)
                        if 'Up' in systematic :
                            if 'pt20to25' in systematic and  e.pt_4 > 20 and  e.pt_4 < 25 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Up')
                            if 'pt25to30' in systematic and  e.pt_4 > 25 and  e.pt_4 < 30 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Up')
                            if 'pt30to35' in systematic and  e.pt_4 > 30 and  e.pt_4 < 35 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Up')
                            if 'pt35to40' in systematic and  e.pt_4 > 35 and  e.pt_4 < 40 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Up')
                            if 'ptgt40' in systematic and  e.pt_4 > 40:
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Up')

                        if 'Down' in systematic :
                            if 'pt20to25' in systematic and  e.pt_4 > 20 and  e.pt_4 < 25 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Down')
                            if 'pt25to30' in systematic and  e.pt_4 > 25 and  e.pt_4 < 30 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Down')
                            if 'pt30to35' in systematic and  e.pt_4 > 30 and  e.pt_4 < 35 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Down')
                            if 'pt35to40' in systematic and  e.pt_4 > 35 and  e.pt_4 < 40 : 
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Down')
                            if 'ptgt40' in systematic and  e.pt_4 > 40:
			        weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Down')


                weight *= weightTID



	    if cat[2:] == 'et' :
		if e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0 : isTight1 = True
		if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= et_tau_vse: isTight2= True

                if tights or  isTight2:
		    #if e.gen_match_3 == 1 or e.gen_match_3 == 15 :
		    if e.gen_match_3 == 15 :
			if preCutOff or preCut : 
			    hBasePrompt[group]['e_et'].Fill(e.pt_3,weight)
			    hBasePrompt[group]['e_ll'].Fill(e.pt_3,weight)

			if e.Electron_mvaFall17V2noIso_WP90_3 >0  and  e.iso_3 < iso_el : 
			    for wp in WP : 	    
				hTightPrompt[group]['e_et'][wp].Fill(e.pt_3,weight)
				hTightPrompt[group]['e_ll'][wp].Fill(e.pt_3,weight)

		    #if  e.gen_match_3 != 15 and  e.gen_match_3 != -1: #meaning all leptons faking tau
		    else : 
		    #if not(e.gen_match_3 != 0 and e.gen_match_3 != 3 and e.gen_match_3 != 4 and e.gen_match_3 != 5):
			if preCutOff or preCut : 
			    hBasenoPrompt[group]['e_et'].Fill(e.pt_3,weight)
			    hBasenoPrompt[group]['e_ll'].Fill(e.pt_3,weight)

			if e.Electron_mvaFall17V2noIso_WP90_3 >0  and  e.iso_3 < iso_el : 
			    for wp in WP :  
				hTightnoPrompt[group]['e_et'][wp].Fill(e.pt_3,weight)
				hTightnoPrompt[group]['e_ll'][wp].Fill(e.pt_3,weight)

                if tights or  isTight1 :
		    #if e.gen_match_4 == 5 :
		    if e.gen_match_4 != 0 and e.gen_match_4 != -1: #we consider only  jets faking taus (lepton faking taus are taken from other studies)

			hBasePrompt[group]['t_et'].Fill(e.pt_4,weight)
			hBasePrompt[group]['t_ll'].Fill(e.pt_4,weight)
			if e.decayMode_4 != -1 : 
			    hBasePromptMode[group]['t_et'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			    hBasePromptMode[group]['t_ll'][str(e.decayMode_4)].Fill(e.pt_4,weight)

			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= et_tau_vse: 
				hTightPrompt[group]['t_et'][wp].Fill(e.pt_4,weight)
				hTightPrompt[group]['t_ll'][wp].Fill(e.pt_4,weight)
				if e.decayMode_4 != -1 : 
				    hTightPromptMode[group]['t_et'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)
				    hTightPromptMode[group]['t_ll'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)


		    #if e.gen_match_4 == 0 :
		    else : 
			hBasenoPrompt[group]['t_et'].Fill(e.pt_4,weight)
			hBasenoPrompt[group]['t_ll'].Fill(e.pt_4,weight)
			if e.decayMode_4 != -1 : 
			    hBasenoPromptMode[group]['t_et'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			    hBasenoPromptMode[group]['t_ll'][str(e.decayMode_4)].Fill(e.pt_4,weight)

			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= et_tau_vse: 
				hTightnoPrompt[group]['t_et'][wp].Fill(e.pt_4,weight)
				hTightnoPrompt[group]['t_ll'][wp].Fill(e.pt_4,weight)
				if e.decayMode_4 != -1 : 
				    hTightnoPromptMode[group]['t_et'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)
				    hTightnoPromptMode[group]['t_ll'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)


	    if cat[2:] == 'mt' :
		if e.iso_3 < iso_mu and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) and e.mediumId_3 > 0: isTight1 = True
	        if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse : isTight2= True

                if tights or  isTight2:
		    #if e.gen_match_3 == 1 or e.gen_match_3 == 15:
		    if e.gen_match_3 == 15:
		    #if e.gen_match_3 != 0 and e.gen_match_3 != 3 and e.gen_match_3 != 4 and e.gen_match_3 != 5  : #subtracting only the tau-matched

			#if preCutOff or preCutt and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) : hBasePrompt[group]['m_mt'].Fill(e.pt_3,weight)
			#if preCutOff or preCutt and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) : 
			if preCutOff or preCutt : 
			    hBasePrompt[group]['m_mt'].Fill(e.pt_3,weight)
			    hBasePrompt[group]['m_ll'].Fill(e.pt_3,weight)

			if e.iso_3 < iso_mu and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) and e.mediumId_3 > 0: 
			    for wp in WP : 
				hTightPrompt[group]['m_mt'][wp].Fill(e.pt_3,weight)
				hTightPrompt[group]['m_ll'][wp].Fill(e.pt_3,weight)


		    else : 
		    #if not (e.gen_match_3 != 0 and e.gen_match_3 != 3 and e.gen_match_3 != 4 and e.gen_match_3 != 5)  : #subtracting only the tau-matched

			#if preCutOff or preCutt and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) : hBasenoPrompt[group]['m_mt'].Fill(e.pt_3,weight)
			#if preCutOff or preCutt and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) : 
			if preCutOff or preCutt  : 
			    hBasenoPrompt[group]['m_mt'].Fill(e.pt_3,weight)
			    hBasenoPrompt[group]['m_ll'].Fill(e.pt_3,weight)

			if  e.iso_3 < iso_mu and  (e.isGlobal_3 > 0 or e.isTracker_3 > 0) and e.mediumId_3 > 0: 
			    for wp in WP : 
				hTightnoPrompt[group]['m_mt'][wp].Fill(e.pt_3,weight)
				hTightnoPrompt[group]['m_ll'][wp].Fill(e.pt_3,weight)


                if tights or  isTight1 :

		    if e.gen_match_4 != 0 and e.gen_match_4 != -1 : ## ==5 previously

			hBasePrompt[group]['t_mt'].Fill(e.pt_4,weight)
			hBasePrompt[group]['t_ll'].Fill(e.pt_4,weight)
			if e.decayMode_4 != -1 : 
			    hBasePromptMode[group]['t_mt'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			    hBasePromptMode[group]['t_ll'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse :
				    hTightPrompt[group]['t_mt'][wp].Fill(e.pt_4,weight)
				    hTightPrompt[group]['t_ll'][wp].Fill(e.pt_4,weight)
				    if e.decayMode_4 != -1 : 
					hTightPromptMode[group]['t_mt'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)
					hTightPromptMode[group]['t_ll'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)

		    else :
			#if e.gen_match_4 == 0 :
			hBasenoPrompt[group]['t_mt'].Fill(e.pt_4,weight)
			hBasenoPrompt[group]['t_ll'].Fill(e.pt_4,weight)
			if e.decayMode_4 != -1 : 
			    hBasenoPromptMode[group]['t_mt'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			    hBasenoPromptMode[group]['t_ll'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_4 >= wp and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse :
				    hTightnoPrompt[group]['t_mt'][wp].Fill(e.pt_4,weight)
				    hTightnoPrompt[group]['t_ll'][wp].Fill(e.pt_4,weight)
				    if e.decayMode_4 != -1 : 
					hTightnoPromptMode[group]['t_mt'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)
					hTightnoPromptMode[group]['t_ll'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)



	    if cat[2:] == 'tt':
		if e.idDeepTau2017v2p1VSjet_3 >= wp and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse: isTight1= True
		if e.idDeepTau2017v2p1VSjet_4 >=wp and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse : isTight2= True

                if tights or  isTight2:
		    if e.gen_match_3 != 0 and e.gen_match_3 != -1:
			hBasePrompt[group]['t1_tt'].Fill(e.pt_3,weight)
			if e.decayMode_3 != -1 : hBasePromptMode[group]['t1_tt'][str(e.decayMode_3)].Fill(e.pt_3,weight)
			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_3 >= wp and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse: 
				hTightPrompt[group]['t1_tt'][wp].Fill(e.pt_3,weight)
				if e.decayMode_3 != -1 : hTightPromptMode[group]['t1_tt'][str(e.decayMode_3)][wp].Fill(e.pt_3,weight)

		    if e.gen_match_3 == 0 :
			hBasenoPrompt[group]['t1_tt'].Fill(e.pt_3,weight)
			if e.decayMode_3 != -1 : hBasenoPromptMode[group]['t1_tt'][str(e.decayMode_3)].Fill(e.pt_3,weight)

			for wp in WP : 
			    if e.idDeepTau2017v2p1VSjet_3 >= wp and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse: 
				hTightnoPrompt[group]['t1_tt'][wp].Fill(e.pt_3,weight)
				if e.decayMode_3 != -1 : hTightnoPromptMode[group]['t1_tt'][str(e.decayMode_3)][wp].Fill(e.pt_3,weight)

                if tights or  isTight1:
		    if e.gen_match_4 != 0 and e.gen_match_4 != -1:

			hBasePrompt[group]['t2_tt'].Fill(e.pt_4,weight)
			if e.decayMode_4 != -1 : hBasePromptMode[group]['t2_tt'][str(e.decayMode_4)].Fill(e.pt_4,weight)
			for wp in WP : 
		            if e.idDeepTau2017v2p1VSjet_4 >=wp and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse : 
				hTightPrompt[group]['t2_tt'][wp].Fill(e.pt_4,weight)
				if e.decayMode_4 != -1 : hTightPromptMode[group]['t2_tt'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)

		    if e.gen_match_4 == 0  :
			hBasenoPrompt[group]['t2_tt'].Fill(e.pt_4,weight)
			if e.decayMode_4 != -1 : hBasenoPromptMode[group]['t2_tt'][str(e.decayMode_4)].Fill(e.pt_4,weight)

			for wp in WP : 
		            if e.idDeepTau2017v2p1VSjet_4 >=wp and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse : 
				hTightnoPrompt[group]['t2_tt'][wp].Fill(e.pt_4,weight)
				if e.decayMode_4 != -1 : hTightnoPromptMode[group]['t2_tt'][str(e.decayMode_4)][wp].Fill(e.pt_4,weight)


	    if cat[2:] == 'em' : 
		if e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0 : isTight1 = True
		if e.iso_4 < iso_mu and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0) and e.mediumId_4 > 0: isTight2 = True

	        mut.SetPtEtaPhiM(e.pt_4,e.eta_4,e.phi_4,0.102)
	        muMET = mut + ptMiss
	        preCutt =  muMET.Mt() < 40.  

                if tights or  isTight2:
		    #if e.gen_match_3 == 15 :
		    #if e.gen_match_3 != 0 and e.gen_match_3 !=-1 :
		    #if e.gen_match_3 == 1 or e.gen_match_3 == 15 :
		    if e.gen_match_3 == 15 :
			if preCutOff or preCut : 
			    hBasePrompt[group]['e_em'].Fill(e.pt_3,weight)
			    hBasePrompt[group]['e_ll'].Fill(e.pt_3,weight)
			for wp in WP : 
			    if e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0 : 
				hTightPrompt[group]['e_em'][wp].Fill(e.pt_3,weight)
				hTightPrompt[group]['e_ll'][wp].Fill(e.pt_3,weight)
		    else :
		    #if not (e.gen_match_3 != 0 and e.gen_match_3 != 3 and e.gen_match_3 != 4 and e.gen_match_3 != 5) and e.gen_match_3 != -1:
			if preCutOff or preCut   : 
			    hBasenoPrompt[group]['e_em'].Fill(e.pt_3,weight)
			    hBasenoPrompt[group]['e_ll'].Fill(e.pt_3,weight)
			for wp in WP : 
			    if  (e.iso_3 < iso_el and  e.Electron_mvaFall17V2noIso_WP90_3 > 0 ): 
				hTightnoPrompt[group]['e_em'][wp].Fill(e.pt_3,weight)
				hTightnoPrompt[group]['e_ll'][wp].Fill(e.pt_3,weight)

                if tights or  isTight1:
		    #if e.gen_match_4 != 0 and e.gen_match_4!=-1:
		    #if e.gen_match_4 != 0 and e.gen_match_4 != 3 and e.gen_match_4 != 4 and e.gen_match_4 != 5:
		    #if e.gen_match_4 == 1 or e.gen_match_4 == 15 :
		    if e.gen_match_4 == 15 :

			#if preCutOff or preCutt and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0): 
			if preCutOff or preCutt : 
			    hBasePrompt[group]['m_em'].Fill(e.pt_4,weight)
			    hBasePrompt[group]['m_ll'].Fill(e.pt_4,weight)

			for wp in WP : 
			    if e.iso_4 < iso_mu and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0) and e.mediumId_4 > 0: 
				hTightPrompt[group]['m_em'][wp].Fill(e.pt_4,weight)
				hTightPrompt[group]['m_ll'][wp].Fill(e.pt_4,weight)

		    else:
		    #if not(e.gen_match_4 != 0 and e.gen_match_4 != 3 and e.gen_match_4 != 4 and e.gen_match_4 != 5) and e.gen_match_4 != -1:
			#if preCutOff or preCutt and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0): 
			if preCutOff or preCutt : 
			    hBasenoPrompt[group]['m_em'].Fill(e.pt_4,weight)
			    hBasenoPrompt[group]['m_ll'].Fill(e.pt_4,weight)
			for wp in WP : 
			    if  (e.iso_4 < iso_mu and  (e.isGlobal_4 > 0 or e.isTracker_4 > 0) and e.mediumId_4 > 0): 
				hTightnoPrompt[group]['m_em'][wp].Fill(e.pt_4,weight)
				hTightnoPrompt[group]['m_ll'][wp].Fill(e.pt_4,weight)



            nEvents+=1
     
	print("{0:30s} {1:7d} {2:10.6f} {3:5d} {4:8.3f}".format(nickName,nentries,sampleWeight[nickName],nEvents,totalWeight))
	inFile.Close()



fOut.cd()
for h in hList :
    OverFlow(hBase[h])
    hBase[h].Write()
    for wp in WP :
        OverFlow(hTight[h][wp])
        hTight[h][wp].Write()



for group in groupss:
    for h in hList :
        
	try :
	    if group !='data' : 
		OverFlow(hBasePrompt[group][h]) 
		hBasePrompt[group][h].Write()
		OverFlow(hBasenoPrompt[group][h]) 
		hBasenoPrompt[group][h].Write()
		for wp in WP : 
		    OverFlow(hTightPrompt[group][h][wp]) 
		    hTightPrompt[group][h][wp].Write()
		    OverFlow(hTightnoPrompt[group][h][wp]) 
		    hTightnoPrompt[group][h][wp].Write()

	except AttributeError : print 'sorry for that', group, h
        for m in hModes :
            try: 
		OverFlow(hBaseMode[group][h][m]) 
		hBaseMode[group][h][m].Write()
		if group !='data' : 
		    OverFlow(hBasePromptMode[group][h][m]) 
		    hBasePromptMode[group][h][m].Write()
		    OverFlow(hBasenoPromptMode[group][h][m]) 
		    hBasenoPromptMode[group][h][m].Write()

                for wp in WP : 
		    OverFlow(hTightMode[group][h][m][wp]) 
		    hTightMode[group][h][m][wp].Write()
		    if group !='data' : 
			OverFlow(hTightPromptMode[group][h][m][wp]) 
			hTightPromptMode[group][h][m][wp].Write()
			OverFlow(hTightPromptMode[group][h][m][wp]) 
			hTightPromptMode[group][h][m][wp].Write()
			OverFlow(hTightnoPromptMode[group][h][m][wp]) 
			hTightnoPromptMode[group][h][m][wp].Write()
	    except AttributeError : print 'sorry for that', group, h, m
    
fOut.Close()

print 'all done now!'


exit()

    

