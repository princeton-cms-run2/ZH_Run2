#
# read MC file root files and histogram by group 
#

#import CMS_lumi
#import tdrstyle
import ROOT
from ROOT import gSystem, gStyle, gROOT, kTRUE, TMatrixD
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, TLegend, TAxis, THStack, TGraphAsymmErrors, vector, gInterpreter
from ROOT import RooWorkspace as WS
gROOT.SetBatch(True) # don't pop up any plots
gStyle.SetOptStat(0) # don't show any stats
from math import sqrt, sin, cos, pi, tan, acos, atan2,log
from array import array
#import math
import os
import os.path
import sys
#import ScaleFactor as SF
sys.path.append('./TauPOG')
from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool
#import fakeFactor2


weights_muToTauFR={''}
weights_elToTauFR={''}
weights_muTotauES={''}
weights_elTotauES={''}
weights_tauTotauES={''}
weights_muES={''}

weights_muES = {'eta0to1p2' : 0.4, 'eta1p2to2p1' : 0.9, 'etagt2p1' : 2.7 }
weights_electronES = {'eta0to1p2' : 1, 'eta1p2to2p1' : 1, 'etagt2p1' : 2 }


def catToNumber(cat) :
    number = { 'eeet':1, 'eemt':2, 'eett':3, 'eeem':4, 'mmet':5, 'mmmt':6, 'mmtt':7, 'mmem':8, 'et':9, 'mt':10, 'tt':11 }
    return number[cat]

def numberToCat(number) :
    cat = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem', 9:'et', 10:'mt', 11:'tt' }
    return cat[number]

def search(values, searchFor):
    for k in values:
        for v in values[k]:
            if searchFor ==v:
                return True
    return False

def runSVFit(entry,tau1, tau2, METV, channel) :
		  
    measuredMETx = METV.Pt()*cos(METV.Phi())
    measuredMETy = METV.Pt()*sin(METV.Phi())

    #define MET covariance
    covMET = TMatrixD(2,2)
    covMET[0][0] = entry.metcov00
    covMET[1][0] = entry.metcov10
    covMET[0][1] = entry.metcov01
    covMET[1][1] = entry.metcov11


    #self.kUndefinedDecayType, self.kTauToHadDecay, self.kTauToElecDecay, self.kTauToMuDecay = 0, 1, 2, 3
    if channel == 'et' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToElecDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.000511) 
    elif channel == 'mt' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToMuDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.106) 
    elif channel == 'tt' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToHadDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), tau1.M())
		    
    if channel != 'em' :
	measTau2 = ROOT.MeasuredTauLepton(kTauToHadDecay, tau2.Pt(), tau2.Eta(), tau2.Phi(), tau2.M())

    if channel == 'em' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToElecDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.000511)
	measTau2 = ROOT.MeasuredTauLepton(kTauToMuDecay, tau2.Pt(), tau2.Eta(), tau2.Phi(), 0.106)

    VectorOfTaus = ROOT.std.vector('MeasuredTauLepton')
    instance = VectorOfTaus()
    instance.push_back(measTau1)
    instance.push_back(measTau2)

    FMTT = ROOT.FastMTT()
    FMTT.run(instance, measuredMETx, measuredMETy, covMET)
    ttP4 = FMTT.getBestP4()
    return ttP4.M(), ttP4.Mt() 


def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./MCsamples_2017_small.csv',help="File to be analyzed.")
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    parser.add_argument("-l","--LTcut",default=0.,type=float,help="H_LTcut")
    parser.add_argument("-s","--sign",default='OS',help="Opposite or same sign (OS or SS).")
    parser.add_argument("-a","--analysis",default='ZH',help="Select ZH or AZH")
    parser.add_argument("--MConly",action='store_true',help="no data driven bkg") 
    parser.add_argument("-r", "--redoFit",default='no',help="redo FastMTT and adjust MET after to Tau ES corrections")
    parser.add_argument("-w", "--workingPoint",type=int, default=16, help="working point for fakes 16 (M), 32(T), 64(VT), 128(VVT)")
    parser.add_argument("-b", "--doBTAG",type=str, default='yes', help="do BTAG or simply apply nbtag criterion")
    parser.add_argument("-j", "--inSystematics",type=str, default='',help='systematic variation')
    parser.add_argument("-e", "--extraTag",type=str, default='noL',help='extra tag; wL, noL wrt to fakes method')
    parser.add_argument("-g", "--genTag",type=str, default='v4',help='which fakesFactor scheme will be used')
    parser.add_argument("-i", "--isLocal",type=str, default=0,help='local or condor')
    parser.add_argument("-t", "--gType",type=str, default='',help='type : data, Signal, Other')
    parser.add_argument("-x", "--subRange",type=int, default=0,help='run on a subrange of events')
    
    return parser.parse_args()

class dupeDetector() :
    
    def __init__(self):
        self.nCalls = 0 
        self.runEventList = []
        self.DuplicatedEvents = []

    def checkEvent(self,entry,cat) :
        self.nCalls += 1 
        #runEvent = "{0:d}:{1:d}:{2:d}:{3:s}".format(entry.lumi,entry.run,entry.evt,cat)
        runEvent = "{0:d}:{1:d}:{2:d}".format(entry.lumi,entry.run,entry.evt)
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

def PtoEta( Px, Py, Pz) :

   P = sqrt(Px*Px+Py*Py+Pz*Pz);
   if P> 0 : 
       cosQ = Pz/P;
       Q = acos(cosQ);
       Eta = - log(tan(0.5*Q));
       return Eta
   else: return -99

def PtoPhi( Px, Py) : return atan2(Py,Px)


def PtoPt( Px, Py) : return sqrt(Px*Px+Py*Py)


def dPhiFrom2P( Px1, Py1, Px2, Py2) :
   prod = Px1*Px2 + Py1*Py2;
   mod1 = sqrt(Px1*Px1+Py1*Py1);
   mod2 = sqrt(Px2*Px2+Py2*Py2);
   cosDPhi = prod/(mod1*mod2);
   return acos(cosDPhi)


def DRobj(eta1,phi1,eta2,phi2) :
    dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
    return sqrt(dPhi**2 + (eta2-eta1)**2)

def DPhiobj(phi1,phi2) :
    dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
    return dPhi

def deltaEta(Px1, Py1, Pz1, Px2, Py2, Pz2):

  eta1 = PtoEta(Px1,Py1,Pz1)
  eta2 = PtoEta(Px2,Py2,Pz2)

  dEta = eta1 - eta2

  return dEta



doCorrectTES=False

nbins=7
Bins=[0,50,70,90,110,130,150,290]
       
#50,70,90,110,130,150,170,210,250,290a  nbins, array('d',Bins))


args = getArgs()
era=str(args.year)
extratag=str(args.extraTag)
#cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}
dataDriven = not args.MConly

dataDriven = True



Pblumi = 1000.
tauID_w = 1.

# Tau Decay types
kUndefinedDecayType, kTauToHadDecay, kTauToElecDecay, kTauToMuDecay = 0, 1, 2, 3   

gInterpreter.ProcessLine(".include .")
#for baseName in ['./SVFit/MeasuredTauLepton','./SVFit/svFitAuxFunctions','./SVFit/FastMTT', './HTT-utilities/RecoilCorrections/src/MEtSys', './HTT-utilities/RecoilCorrections/src/RecoilCorrector'] : 
for baseName in ['./SVFit/MeasuredTauLepton','./SVFit/svFitAuxFunctions','./SVFit/FastMTT'] : 
    if os.path.isfile("{0:s}_cc.so".format(baseName)) :
	gInterpreter.ProcessLine(".L {0:s}_cc.so".format(baseName))
    else :
	gInterpreter.ProcessLine(".L {0:s}.cc++".format(baseName))   
	# .L is not just for .so files, also .cc

print 'compiled it====================================================================='

weights= {''}
campaign = {2016:'2016Legacy', 2017:'2017ReReco', 2018:'2018ReReco'}


scaleSyst = ["Central"]

scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']

for i, sys in enumerate(scale) :
    scaleSyst.append(sys+'Up')
    scaleSyst.append(sys+'Down')


#listsyst=['njets', 'nbtag', 'jpt', 'jeta', 'jflavour','MET_T1_pt', 'MET_T1_phi', 'MET_pt', 'MET_phi', 'MET_T1Smear_pt', 'MET_T1Smear_phi']

jes=['jesAbsolute', 'jesAbsolute_{0:s}'.format(str(era)), 'jesBBEC1', 'jesBBEC1_{0:s}'.format(str(era)), 'jesEC2', 'jesEC2_{0:s}'.format(str(era)), 'jesFlavorQCD', 'jesHF', 'jesHF_{0:s}'.format(str(era)), 'jesRelativeBal', 'jesRelativeSample_{0:s}'.format(str(era)), 'jesHEMIssue', 'jesTotal', 'jer']

jesSyst=[]
for i, sys in enumerate(jes) :
    jesSyst.append(sys+'Up')
    jesSyst.append(sys+'Down')
#LHEScaleWeight :                                                   *
#*         | Float_t LHE scale variation weights (w_var / w_nominal); [0] is muR=0.5 muF=0.5 ; [1] is muR=0.5 muF=1 ; [2] is muR=0.5 muF=2 ; [3] is muR=1 muF=0.5 ; [4] is muR=1 muF=1 ; [5] is muR=1 muF=2 ; [6] is muR=2 muF=0.5 ; [7] is muR=2 muF=1 ; [8] is muR=2 muF=2 *
#low_pt -> LHEScaleWeights[]
#high_pt -> LHEScaleWeights[]
otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered', 'scale_lowpt', 'scale_highpt','lep_scale'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')


#jesSyst hold the jes systematic  - we need njets, nbtag, nflavor, jpt

sysall = scaleSyst+jesSyst+OtherSyst

print 'systematics', sysall

if str(args.inSystematics) not in sysall : 
    print 'the input ', args.inSystematics, ' systematic does not exist, choose on from:', sysall
    exit() 

systematic=str(args.inSystematics)
#systematic='jerUp'a

dobtag = str(args.doBTAG.lower()) == 'yes' or str(args.doBTAG) == '1' 
#if 'ZH' in str(args.gType) or 'HWW' in str(args.gType) :  dobtag=False

if str(args.gType) !='data' and dobtag :

    gInterpreter.ProcessLine('.L BTagCalibrationStandalone.cpp+') 
    calib = ROOT.BTagCalibration('csvv1', 'DeepCSV_{0:s}.csv'.format(era))
    # making a std::vector<std::string>> in python is a bit awkward, 
    # but works with root (needed to load other sys types):
    v_sys = getattr(ROOT, 'vector<string>')()
    #v_sys.push_back('up')
    #v_sys.push_back('down')


    # make a reader instance and load the sf data
    reader_b = ROOT.BTagCalibrationReader(
        1,             # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
	"central",     # central systematic type
	v_sys,         # vector of other sys. types
    )    


    reader_b.load(
	calib, 
	0,         # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
	#"iterativefit"      # measurement type
	"incl"      # measurement type
    )

    reader_b.load(
	calib, 
	1,         # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
	#"iterativefit"      # measurement type
	"incl"      # measurement type
    )

    reader_b.load(
	calib, 
	2,         # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
	#"iterativefit"      # measurement type
	"incl"      # measurement type
    )

tt_tau_vse = 4
tt_tau_vsmu = 1

et_tau_vse = 32
et_tau_vsmu = 1

mt_tau_vse = 4
mt_tau_vsmu = 8



if era == '2016' : 
    weights = {'lumi':35.92, 'tauID_w' :0.87, 'tauES_DM0' : -0.6, 'tauES_DM1' : -0.5,'tauES_DM10' : 0.0, 'mutauES_DM0' : -0.2, 'mutauES_DM1' : 1.5, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 9.5}
    weights_muTotauES = {'DM0' :0., 'DM1' : -0.5, 'DM10' : 0, 'DM11' :0}
    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_eta-dm_DeepTau2017v2p1VSe_2016Legacy.root'}
    FESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileFES' : 'TauFES_eta-dm_DeepTau2017v2p1VSe_2016Legacy.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2016.root'}


if era == '2017' : 
    weights = {'lumi':41.53, 'tauID_w' :0.89, 'tauES_DM0' : 0.7, 'tauES_DM1' : -0.2,'tauES_DM10' : 0.1, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.3, 'eltauES_DM1' : 3.6}

    weights_muTotauES = {'DM0' :-0.2, 'DM1' : -0.8, 'DM10' : 0, 'DM11' :0}
    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_DeepTau2017v2p1VSjet_2017ReReco.root'}
    FESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileFES' : 'TauFES_eta-dm_DeepTau2017v2p1VSe_2017ReReco.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2017.root'}

if era == '2018' : 
    weights = {'lumi':59.74, 'tauID_w' :0.90, 'tauES_DM0' : -1.3, 'tauES_DM1' : -0.5,'tauES_DM10' : -1.2, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 0.0}
    
    weights_muTotauES = {'DM0' :-0.2, 'DM1' : -1., 'DM10' : 0, 'DM11' :0}
    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_DeepTau2017v2p1VSjet_2018ReReco.root'}
    FESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileFES' : 'TauFES_eta-dm_DeepTau2017v2p1VSe_2018ReReco.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2018.root'}


'''
if era == '2016' : recoilCorrector  = ROOT.RecoilCorrector("./Type1_PFMET_Run2016BtoH.root");
if era == '2017' : recoilCorrector  = ROOT.RecoilCorrector("./Type1_PFMET_2017.root");
if era == '2018' : recoilCorrector  = ROOT.RecoilCorrector("./TypeI-PFMet_Run2018.root");
'''

if 'data' not in str(args.gType) : 
    finWS=("{0:s}{1:s}".format(WorkSpace['dir'],WorkSpace['fileWS']))
    fInws=TFile(finWS, 'read') 
    fInws.cd()


    #ROOT.gROOT.LoadMacro("CrystalBallEfficiency.cxx+")
    wspace = WS.RooWorkspace("w")
    wspace=fInws.Get("w")


# use this utility class to screen out duplicate events
DD = {}
for cat in cats.values() :
    DD[cat] = dupeDetector()

# dictionary where the group is the key
hMC = {}
hMCFM = {}

hm_sv_new = {}
hm_sv_new_FM = {}
hm_sv_new_FMext = {}
hmt_sv_new = {}
hmt_sv_new_FM = {}


hm_sv_new_jA = {}
hm_sv_new_jB = {}
hm_sv_new_jC = {}
hm_sv_new_jBC = {}

# m_sv_new_FMjall is the main variable to be used for m_sv
hm_sv_new_FMjall = {}
hm_sv_new_FMjallv2 = {}

hm_sv_new_lep_FWDH_htt125= {}
hm_sv_new_lep_PTV_0_75_htt125 = {}
hm_sv_new_lep_PTV_75_150_htt125 = {}
hm_sv_new_lep_PTV_150_250_0J_htt125 = {}
hm_sv_new_lep_PTV_150_250_GE1J_htt125 = {}
hm_sv_new_lep_PTV_GT250_htt125 = {}

# pT <75, 0,1, >1 jets
hm_sv_new_FMjA = {}


# 75<pT <150, 0,1, >1 jets
hm_sv_new_FMjB = {}

hm_sv_new_FMjBC = {}


# 150<pT <250, 0,1, >1 jets
hm_sv_new_FMjC = {}

hw_fm_new = {}
hH_LT= {}
hH_LT_FM= {}
hCutFlow = {}
hCutFlowN = {}
hCutFlowFM = {}
hCutFlowPerGroup = {}
hCutFlowPerGroupFM = {}
WCounter = {}


isW = False
isDY = False
muonMass = 0.106
electronMass = 0.000511
		
MetV = TLorentzVector()
tauV3 = TLorentzVector()
tauV4 = TLorentzVector()
tauV3uncor = TLorentzVector()
tauV4uncor = TLorentzVector()
tauV = TLorentzVector()
L1 = TLorentzVector()
L2 = TLorentzVector()
L1.SetXYZM(0,0,0,0)
L2.SetXYZM(0,0,0,0)
L1uncor = TLorentzVector()
L2uncor = TLorentzVector()
L1uncor.SetXYZM(0,0,0,0)
L2uncor.SetXYZM(0,0,0,0)
L1uncorMC = TLorentzVector()
L2uncorMC = TLorentzVector()
L1uncorMC.SetXYZM(0,0,0,0)
L2uncorMC.SetXYZM(0,0,0,0)
'''
L1g = TLorentzVector()
L2g = TLorentzVector()
L1g.SetXYZM(0,0,0,0)
L2g.SetXYZM(0,0,0,0)
'''
MetV.SetXYZM(0,0,0,0)
tauV3.SetXYZM(0,0,0,0)
tauV4.SetXYZM(0,0,0,0)
tauV3uncor.SetXYZM(0,0,0,0)
tauV4uncor.SetXYZM(0,0,0,0)
tauV.SetXYZM(0,0,0,0)

# dictionary where the nickName is the key
nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}

groups = ['Reducible','fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2']
groups = ['Reducible','fakes','f1', 'f2']
ngroups = ['Reducible', 'fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','ZH','ggZH', 'WH','Other','ZZ','data']
ngroups = ['Reducible', 'fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','Other','ZZ','ZH']


groups = []
ngroups = []


ngroups.append(str(args.gType))
groups.append(str(args.gType))

ngroups.insert(0,'Reducible')
groups.insert(0,'Reducible')

if str(args.sign) == 'SS' : 
    ngroups.insert(0,'SSR')
    groups.insert(0,'SSR')

if 'data' in str(args.gType) : 
    groups = ['SSR','Reducible','fakes','f1', 'f2','data']
    ngroups = ['SSR', 'Reducible','fakes','f1', 'f2','data']

for group in ngroups :
    nickNames[group] = []
print groups, ngroups, nickNames



# make a first pass to get the weights

'''
WJets_kfactor = 1.166
DY_kfactor = 1.137

WNJetsXsecs = [40322.3]  #LO for 0-jet
DYNJetsXsecs = [4738.53]  #LO  for 0-jet

WIncl_xsec = 52760*WJets_kfactor ##LO *kfactor inclusive
DYIcl_xsec = 6077.22 ##NNLO inclusive


WxGenweightsArr = []
DYxGenweightsArr = []
'''


islocal=False
if str(args.isLocal) == '1' or str(args.isLocal) =='yes' : islocal=True



'''
print ' Will use the ' ,args.inFileName ,' in local mode ? ', islocal
for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    if '#' in vals[0] : continue
    if vals[0][0] == "W" and  "JetsToLNu" in vals[0][2:] and 'TWJ' not in vals[0]:
        WNJetsXsecs.append(float(vals[2]))
        #filein = '../MC/condor/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
        filein = '{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
        if islocal : filein = '../MC/condor/{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
        fIn = TFile.Open(filein,"READ")
        WxGenweightsArr.append(fIn.Get("hWeights").GetSumOfWeights())


    if vals[0][:2] == "DY" and "JetsToLL" in vals[0][3:] and 'M10to50' not in vals[0] and 'TWJ' not in vals[0]:
        DYNJetsXsecs.append(float(vals[2]))
        #filein = '../MC/condor/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
        filein = '{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
        if islocal : filein = '../MC/condor//{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
        fIn = TFile.Open(filein,"READ")
        DYxGenweightsArr.append(fIn.Get("hWeights").GetSumOfWeights())

WIncl_only = True
DYIncl_only = True
'''

for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    if '#' in vals[0] : continue
    nickName = vals[0]
    group = vals[1]
    nickNames[group].append(nickName)
    if '*' in vals[2] : 
        value1, value2 = map(float, vals[2].split("*"))
        xsec[nickName] = float(value1*value2)
    #elif '+' in vals[2] : 
    #    value1, value2 = map(float, vals[2].split("+"))
    #    xsec[nickName] = float(value1+value2)
    else : xsec[nickName] = float(str(vals[2]))


    #if str(args.sign=='SS') and 'data' not in nickName : nickNames[group]='VR'
    if nickName == 'ZHToTauTau' : 
        xsec[nickName] = float(0.0627)
    if nickName == 'HZJ_HToWW' : 
        xsec[nickName] = float(0.163)

    #totalWeight[nickName] = float(vals[4])
    if islocal :    filein = '../MC/condor/{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
    else : filein = '{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
    if 'data' not in filein : 
        
        #if '+' in vals[4] : 
	#    value1, value2 = map(float, vals[4].split("+"))
	#    totalWeight[nickName] = float(value1+value2)
	#else : 
	#totalWeight[nickName] = float(vals[4])
	fIn = TFile.Open(filein,"READ")
	totalWeight[nickName] = float(fIn.Get("hWeights").GetSumOfWeights())



        if nickName == 'ZHToTauTau' : totalWeight[nickName] *= float(3*0.033658)
        if nickName == 'HZJ_HToWW' : totalWeight[nickName] *= float(3*0.033658)
        print '----------------======================================================', totalWeight[nickName]
	sampleWeight[nickName]= Pblumi*weights['lumi']*xsec[nickName]/totalWeight[nickName]
    else : 
        #nickName = 'data_{0:s}'.format(era)
        totalWeight[nickName] = 1.
        sampleWeight[nickName] = 1.
    

    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

    #print("{0:100s}  & {1:10.3f} & {2:11.1f} & {3:10.6f}\\\\\\hline".format(
    #     str(vals[6]),xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))


'''
    if 'W1' in nickName or 'W2' in nickName or 'W3' in nickName or 'W4' in nickName : WIncl_only = False
    if 'DY1' in nickName or 'DY2' in nickName or 'DY3' in nickName or 'DY4' in nickName :  DYIncl_only = False


for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i)
    if search(nickNames, nn) :
        sampleWeight[nn] = Pblumi*weights['lumi']/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + DYxGenweightsArr[i-1]/(xsec[nn]*DY_kfactor))
        #print 'DY', totalWeight['DYJetsToLL']/xsec['DYJetsToLL'], DYxGenweightsArr[i-1], 'xsec', xsec[nn], 'weight ? ', sampleWeight[nn]

for i in range(1,5) :
    nn = 'W{0:d}JetsToLNu'.format(i)
    if search(nickNames, nn) : 
        sampleWeight[nn] = Pblumi*weights['lumi']/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + WxGenweightsArr[i-1]/(xsec[nn]*WJets_kfactor))
        #else: sampleWeight[nn] = Pblumi*weights['lumi']/(totalWeight['WJetsToLNuext']/xsec['WJetsToLNuext'] + WNJetsXsecs[i-1]/(xsec[nn]*WJets_kfactor))

'''

outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut))
if args.MConly :
    print("args.MConly is TRUE")
    outFileName = outFileName.replace('.root','_MC.root') 

    
if args.redoFit.lower() == 'no' : outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_{3:s}noSV'.format(args.year,args.sign,int(args.LTcut), str(args.workingPoint))
if args.redoFit.lower() != 'no' : outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_{3:s}SV'.format(args.year,args.sign,int(args.LTcut), str(args.workingPoint))


#args.redoFit='yes'

WP = args.workingPoint
vertag = str(args.genTag)
WPSR= 16
#if args.workingPoint == args.bruteworkingPoint : WPSR = WP

SubRedMC=False
if ( 'ZZ' in str(args.gType) or 'Other' in str(args.gType)) and 'OSS' in str(args.sign): SubRedMC = True
if 'data' in str(args.gType) or   SubRedMC:
    import fakeFactor2
    FF = fakeFactor2.fakeFactor2(args.year,WP)
    #import fakeFactor
    #FF = fakeFactor.fakeFactor(args.year,WP,extratag, vertag,systematic)

import EWKWeights
if  str(args.gType) == 'ZH' or  str(args.gType) == 'HWW':
    EWK = EWKWeights.EWKWeights()



plotSettings = { # [nBins,xMin,xMax,units]
        "m_sv":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "met":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"],
        "pt_3":[10,0,200,"[Gev]","P_{T}(#tau_{3})"],
        "pt_4":[10,0,200,"[Gev]","P_{T}(#tau_{4})"]


}

wpp = 'Medium'
if str(args.workingPoint=='16') : wpp = 'Medium'
if str(args.workingPoint=='32') : wpp = 'Tight'
if str(args.workingPoint=='64') : wpp = 'VTight'
if str(args.workingPoint=='128') : wpp = 'VVTight'

tauSFTool = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSjet',wpp)
testool = TauESTool(campaign[args.year],'DeepTau2017v2p1VSjet', TESSF['dir'])
festool = TauFESTool(campaign[args.year],'DeepTau2017v2p1VSe', FESSF['dir'])

#antiEleSFToolVVL = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','VVLoose')
#antiMuSFToolVL  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','VLoose')
antiEleSFToolVL = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','VLoose')
antiMuSFToolVL  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','VLoose')

antiEleSFToolT = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','Tight')
antiMuSFToolT  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','Tight')




cols = len(cats.items()[0:8])
icut=10 ########last filled bin from first round of ntuples
hLabels=[]
rows, cols,nicks = (8, 500,200) 
#hLabels = [[0]*cols]*rows 

hLabels.append('All')
hLabels.append('inJSON')
hLabels.append('METfilter')
hLabels.append('Trigger')
hLabels.append('LeptonCount')
hLabels.append('GoogLeptons')
hLabels.append('LeptonPairs')
hLabels.append('foundZ')
hLabels.append('GoodTauPair')
#hLabels.append('TightTauPair') #bin 10

hLabels.append(str(args.sign)) #bin 11
hLabels.append('goodIso_Id')
hLabels.append('nbtag=0')
hLabels.append('btagSF')
hLabels.append('TriggerSF')
hLabels.append('LeptonSF')
hLabels.append('TrackingSF')
hLabels.append('TauID')

WCounter = [[[0 for k in xrange(cols)] for j in xrange(rows)] for i in xrange(nicks)]


#for icat, cat in cats.items()[0:8] :

for icat, cat in cats.items()[0:8] :
    hCutFlow[cat] = {}
    hCutFlowN[cat] = {}
    hCutFlowFM[cat] = {}

ffout='testZH_{0:s}_{1:s}.root'.format(extratag,vertag)
if vertag== '' : ffout='testZH_{0:s}.root'.format(extratag)



isSignal = False
for group in groups :

    if 'ZH' in group or 'WH' in group  or 'HWW' in group : isSignal = True
    for inick, nickName in enumerate(nickNames[group]) :
        #if group == 'data':
	#    #inFileName = './data/{0:s}/data_{1:s}/{2:s}.root'.format(args.analysis,era,nickName)
	#    inFileName = './data/{0:s}//data_{1:s}/{2:s}.root'.format(args.analysis,era,nickName)
        for icat, cat in cats.items()[0:8] :
	    #setting up the CutFlow histogram
	    hCutFlow[cat][nickName] = {}
	    hCutFlowN[cat][nickName] = {}
	    hCutFlowFM[cat][nickName] = {}
	    hCutFlowN[cat][nickName] = TH1D("hCutFlow_"+nickName+"_"+cat,"CutFlow",20,-0.5,19.5)
	    hCutFlowFM[cat][nickName] = TH1D("hCutFlowFM_"+nickName+"_"+cat,"CutFlow",20,-0.5,19.5)

	    #if group != 'data' :
	    inFileName = '{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
	    if islocal : 
                if group != 'data' : inFileName = '../MC/condor/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
                else : inFileName = '../data/condor/{0:s}/data_{2:s}/data_{2:s}.root'.format(args.analysis,nickName,era)

	    inFile = TFile.Open(inFileName)
	    inFile.cd()

	    print '========================================> will use this one',inFileName, inick, nickName, cat, inick, nicks
	    if group != 'data' :
		hCutFlow[cat][nickName] = inFile.Get("hCutFlowWeighted_{0:s}".format(cat))
	    else :
		hCutFlow[cat][nickName] = inFile.Get("hCutFlow_{0:s}".format(cat))
            
	    for i in range(1,10) :
 		#WCounter[i-1][icat-1][inick] = float(hCutFlow[cat][nickName].GetBinContent(i))
                hCutFlowN[cat][nickName].SetBinContent(i,WCounter[i-1][icat-1][inick])
		#print i, hCutFlow[cat][nickName].GetBinContent(i), hCutFlow[cat][nickName].GetXaxis().GetBinLabel(i), cat, ' <===>', WCounter[i-1][icat-1][inick], nickName
            
	    inFile.Close()




for ig, group in enumerate(groups) :

    hMC[group] = {}
    hMCFM[group] = {}
    hm_sv_new[group] = {}
    hm_sv_new_FM[group] = {}
    hm_sv_new_FMext[group] = {}

    hm_sv_new_jA[group] = {}
    hm_sv_new_jB[group] = {}
    hm_sv_new_jC[group] = {}
    hm_sv_new_jBC[group] = {}

    hm_sv_new_FMjA[group] = {}
    hm_sv_new_FMjall[group] = {}
    hm_sv_new_FMjallv2[group] = {}

    hm_sv_new_FMjB[group] = {}
    hm_sv_new_FMjBC[group] = {}



    hm_sv_new_FMjC[group] = {}



    hmt_sv_new[group] = {}
    hmt_sv_new_FM[group] = {}



    hw_fm_new[group] = {}
    hH_LT[group] = {}
    hH_LT_FM[group] = {}
    hCutFlowPerGroup[group] = {}
    hCutFlowPerGroupFM[group] = {}


    hm_sv_new_lep_FWDH_htt125[group] = {}
    hm_sv_new_lep_PTV_0_75_htt125[group] = {}
    hm_sv_new_lep_PTV_75_150_htt125[group] = {}
    hm_sv_new_lep_PTV_150_250_0J_htt125[group] = {}
    hm_sv_new_lep_PTV_150_250_GE1J_htt125[group] = {}
    hm_sv_new_lep_PTV_GT250_htt125[group] = {}
   

    for icat, cat in cats.items()[0:8] :
        hMC[group][cat] = {}
        hMCFM[group][cat] = {}

        hName = 'h{0:s}_{1:s}'.format(group,cat)

        hH_LT[group][cat] = TH1D(hName+'_H_LT',hName+'_H_LT',10,0,200)
        hH_LT[group][cat].SetDefaultSumw2()
        hH_LT_FM[group][cat] = TH1D(hName+'_H_LT_FM',hName+'_H_LT',10,0,200)
        hH_LT_FM[group][cat].SetDefaultSumw2()

        hCutFlowPerGroup[group][cat] = {}
        hCutFlowPerGroupFM[group][cat] = {}
        hCutFlowPerGroup[group][cat] = TH1D("hCutFlowPerGroup_"+group+"_"+cat,"PerGroupCutFlow",20,-0.5,19.5)
        hCutFlowPerGroupFM[group][cat] = TH1D("hCutFlowPerGroupFM_"+group+"_"+cat,"PerGroupCutFlowFM",20,-0.5,19.5)

	hw_fm_new[group][cat] = TH1D(hName+'_w_fm_new',hName+'_w_fm_new',3,0.5,3.5)
	hw_fm_new[group][cat].SetDefaultSumw2()

	hm_sv_new[group][cat] = {}
	hm_sv_new_FM[group][cat] = {}
	hm_sv_new_FMext[group][cat] = {}

	#hm_sv_newsum_zpt[group][cat] = {}
	#hm_sv_newsum_zpt_FM[group][cat] = {}

	hm_sv_new_jA[group][cat] = {}
	hm_sv_new_jB[group][cat] = {}
	hm_sv_new_jC[group][cat] = {}
	hm_sv_new_jBC[group][cat] = {}

	hm_sv_new_FMjA[group][cat] = {}
	hm_sv_new_FMjall[group][cat] = {}
	hm_sv_new_FMjallv2[group][cat] = {}

	hm_sv_new_FMjB[group][cat] = {}
	hm_sv_new_FMjBC[group][cat] = {}

	hm_sv_new_FMjC[group][cat] = {}

	hmt_sv_new[group][cat] = {}
	hmt_sv_new_FM[group][cat] = {}


	hm_sv_new_lep_FWDH_htt125[group][cat] = {}
	hm_sv_new_lep_PTV_0_75_htt125[group][cat] = {}
	hm_sv_new_lep_PTV_75_150_htt125[group][cat] = {}
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat] = {}
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat] = {}
	hm_sv_new_lep_PTV_GT250_htt125[group][cat] = {}


	hName = 'h{0:s}_{1:s}_m_sv_new'.format(group,cat)
	hm_sv_new[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
        print '===================================================================', nbins, Bins
	hm_sv_new[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM'.format(group,cat)
	hm_sv_new_FM[group][cat] = TH1D(hName, hName, nbins, array('d',Bins))
	hm_sv_new_FM[group][cat].SetDefaultSumw2()
        #print 'take this example', hm_sv_new[group][cat].GetName(), 

	hName = 'h{0:s}_{1:s}_m_sv_new_FMext'.format(group,cat)
	hm_sv_new_FMext[group][cat] = TH1D(hName, hName, 20,0,400)  
	hm_sv_new_FMext[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_jA'.format(group,cat)
	hm_sv_new_jA[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_jB'.format(group,cat)
	hm_sv_new_jB[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_jC'.format(group,cat)
	hm_sv_new_jC[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_jC[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_jBC'.format(group,cat)
	hm_sv_new_jBC[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_jBC[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_m_sv_new_FMjA'.format(group,cat)
	hm_sv_new_FMjA[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_FMjA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjB'.format(group,cat)
	hm_sv_new_FMjB[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_FMjB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjC'.format(group,cat)
	hm_sv_new_FMjC[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_FMjC[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_FMjBC'.format(group,cat)
	hm_sv_new_FMjBC[group][cat] = TH1D(hName ,hName, nbins, array('d',Bins))
	hm_sv_new_FMjBC[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_m_sv_new_FMjall'.format(group,cat)
	hm_sv_new_FMjall[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_FMjall[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_FMjallv2'.format(group,cat)
	hm_sv_new_FMjallv2[group][cat] = TH1D(hName ,hName, 14,0,14)
	hm_sv_new_FMjallv2[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_mt_sv_new'.format(group,cat)
	hmt_sv_new[group][cat] = TH1D(hName, hName, nbins, array('d',Bins))
	hmt_sv_new[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_mt_sv_new_FM'.format(group,cat)
	hmt_sv_new_FM[group][cat] = TH1D(hName,hName, nbins, array('d',Bins))
	hmt_sv_new_FM[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_lep_FWDH_htt125'.format(group,cat)
	hm_sv_new_lep_FWDH_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_FWDH_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_0_75_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_0_75_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_0_75_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_75_150_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_75_150_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_75_150_htt125[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_lep_PTV_150_250_0J_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_150_250_GE1J_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_GT250_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_GT250_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_GT250_htt125[group][cat].SetDefaultSumw2()


        for plotVar in plotSettings:
            hMC[group][cat][plotVar] = {}
            hMCFM[group][cat][plotVar] = {}
            nBins = plotSettings[plotVar][0]
            xMin = plotSettings[plotVar][1]
            xMax = plotSettings[plotVar][2]
            units = plotSettings[plotVar][3]
            lTitle = plotSettings[plotVar][4]
            hName = 'h{0:s}_{1:s}_{2:s}'.format(group,cat,plotVar)
            
            binwidth = (xMax - xMin)/nBins
            hMC[group][cat][plotVar] = TH1D(hName,hName,nBins,xMin,xMax)
            hMC[group][cat][plotVar].SetDefaultSumw2()

            hName = 'h{0:s}_{1:s}_{2:s}_FM'.format(group,cat,plotVar)
            hMCFM[group][cat][plotVar] = TH1D(hName,hName,nBins,xMin,xMax)
            hMCFM[group][cat][plotVar].SetDefaultSumw2()
            hMCFM[group][cat][plotVar].GetXaxis().SetTitle(lTitle + ' ' + units)
            #if 'GeV' in units : hMCFM[group][cat][plotVar].GetYaxis().SetTitle("Events / "+str(binwidth)+" {0:s}".format(units))
            #if 'GeV' not in units : hMCFM[group][cat][plotVar].GetYaxis().SetTitle("Events / "+str(binwidth))

            #print '=======', nBins, xMin, xMax, hMC[group][cat][plotVar].GetName(), hMC[group][cat][plotVar].GetTitle()

	print("\nInstantiating TH1D {0:s}".format(hName))
	print("      Nickname                 Entries    Wt/Evt  Ngood   Tot Wt")
    
    for inick, nickName in enumerate(nickNames[group]) :

        if 'DY' in nickName : isDY = True
	if 'JetsToLNu' in nickName and 'TW' not in nickName : isW = True
        #print 'names are====================>', hMC[group][cat][plotVar].GetName()

        isData = False 
        doJME = False
        if str(args.inSystematics) != 'none' : doJME = False
        inFileName = '{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
        if islocal : inFileName = '../MC/condor/{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
        print 'THIS IS IT', inFileName
	#cf = os.path.isfile('{0:s}'.format(inFileName))
	#if not cf : continue
        if group == 'data' :
            isData = True
            #varSystematics=['', 'nom']
            inFileName = 'data_{1:s}.root'.format(args.analysis,era,nickName)
            if islocal : inFileName = '../data/condor/{0:s}/data_{1:s}/data_{1:s}.root'.format(args.analysis,era,nickName)
	    print 'for data will use ',inFileName
        try :

            inFile = TFile.Open(inFileName)
            inFile.cd()


            tree_ = "Events"

            if systematic in scaleSyst and systematic != 'Central' : tree_ = systematic
            #if doCorrectTES : tree_ = "Events"

            if group == 'data' : tree_ = "Events"
	    inTree = inFile.Get(tree_)

	    #inTree = getattr(inFile, tree_, None)
            nentries = inTree.GetEntries()
            print 'will work with', tree_, ' and ', nentries, inTree.GetName(), systematic

        except AttributeError :
            print("  Failure on file {0:s}".format(inFileName))
            exit()

        nEvents, totalWeight = 0, 0.
	sWeight = 0.
        DYJets = ('DYJetsToLL' in nickName and 'M10' not in nickName)
	WJets  = ('WJetsToLNu' in nickName and 'TW' not in nickName)
        sWeight = sampleWeight[nickName]
	print '========================================> start looping on events now',inFileName, inick, nickName, sWeight

	mu_iso = 0.15
	el_iso = 0.15
	mu_eta = 2.4
	el_eta = 2.5

        chunck = int(args.subRange)
        step=25000

        if chunck > 0 :
            print 'Will run for',  (chunck-1)*step,'---> to ', (chunck)*step,' events now....'
        else :     print 'Will run for 0',  '---> to ', inTree.GetEntries(), ' events now....'
        printOn=False
        printDebug=False
        lumiss=['509','1315','779','248','63','69']
        if printOn : 
            print 'cat \t lumi \t run \t  event  \t pt_1 \t pt_2 \t pt_3 \t pt_4 \t  met  \t  nbtag \t  btag_w \t pu_w \t gen_w \t prefire_w \t HTXS \t mll'

        for i, e in enumerate(inTree) :

            inTree.GetEntry(i)
            #if str(e.lumi) in lumiss : printDebug = True
            if chunck > 0 :
		if i <   (chunck-1)*step: continue
		if i >=  (chunck)*step: continue

            iCut=icut
 
            hGroup = group

            trigw = 1.
	    weight=1.
            weightCF = 1.
	    weightFM=1.
            weightTID = 1.
	    ww = 1.
            btag_sf = 1.
            lepton_sf = 1.
            cat = cats[e.cat]
            icat = catToNumber(cat)
            tight1 = True
            tight2 = True
            tight3 = True
            tight4 = True
            isfakemc1 = False
            isfakemc2 = False
	    p3 = e.pt_3
	    p4 = e.pt_4

	    if cat[2:] == 'em'  : continue
        
	    #if ('ZZTo4' in inFileName or 'ZH' in inFileName) and  i > 2000 : continue
	    #if hGroup != 'data' and i > 1000:continue
            if i % 5000 ==0: print i, 'from ', nentries
            #if i > 10000 : break
            try : 

                met = e.met
                metphi = e.metphi

                if doCorrectTES : 
                    met = e.metNoTauES
                    metphi = e.metphiNoTauES

		njets = getattr(e, 'njets_nom', None)
		jpt = getattr(e, 'jpt_nom', None)
		jeta = getattr(e, 'jeta_nom', None)
		jflavour = getattr(e, 'jflavour_nom', None)
		nbtagM = getattr(e, 'nbtagM_nom', None)
		nbtagL = getattr(e, 'nbtagL_nom', None)
		jCSV = getattr(e, 'btagDeep_nom', None)
		jCSV = getattr(e, 'btagDeep', None)
                


            except AttributeError :
                print 'WARNING!!! some problem with reading braches!'
                exit()
                met = e.metNoTauES
                metphi = e.metphiNoTauES
                njets = e.njets
                jpt = e.jpt
                jeta = e.jeta
                jflavour = e.jflavour
                nbtagM = e.nbtagM
                nbtagL = e.nbtagL
                jCSV = e.btagDeep


            if systematic in jesSyst and group != 'data' :  
		met = getattr(e, 'MET_T1_pt_{0:s}'.format(systematic), None)
		metphi = getattr(e, 'MET_T1_phi_{0:s}'.format(systematic), None)
		njets = getattr(e, 'njets_{0:s}'.format(systematic), None)
		jpt = getattr(e, 'jpt_{0:s}'.format(systematic), None)
		jeta = getattr(e, 'jeta_{0:s}'.format(systematic), None)
		jflavour = getattr(e, 'jflavour_{0:s}'.format(systematic), None)
		jCSV = getattr(e, 'btagDeep_{0:s}'.format(systematic), None)
		nbtagL = getattr(e, 'nbtagL_{0:s}'.format(systematic), None)
		nbtagM = getattr(e, 'nbtagM_{0:s}'.format(systematic), None)

            if 'scale_met_unclusteredUp' in systematic : 
                met  = e.MET_pt_UnclUp
                metphi  = e.MET_phi_UnclUp
            if 'scale_met_unclusteredDown' in systematic : 
                met  = e.MET_pt_UnclDown
                metphi  = e.MET_phi_UnclDown
            #print 'compare', met, e.metNoTauES, njets, e.njets, 'jpt', jpt[0], e.jpt[0]


            #if e.isTrig_1 == 0 and e.isDoubleTrig==0 : continue  
            if printDebug:
		if e.isTrig_1 == 0 : print 'failed trigger', cat, e.lumi, e.run, e.evt, e.isTrig_1, e.whichTriggerWord, e.whichTriggerWordSubL
		if e.q_1*e.q_2 > 0 : print 'failed q_1*q_2', cat, e.lumi, e.run, e.evt, e.q_1*e.q_2
		if args.sign == 'SS':
		   if e.q_3*e.q_4 < 0. : continue
		else :
		    if e.q_3*e.q_4 > 0. : print 'failed q_3*q_4', cat, e.lumi, e.run, e.evt, e.q_3*e.q_4
            
            if e.isTrig_1 == 0 : continue  
            if e.q_1*e.q_2 > 0 : continue
            if args.sign == 'SS':
               if e.q_3*e.q_4 < 0. : continue
            else :
                if e.q_3*e.q_4 > 0. : continue

            '''
            if WJets and not WIncl_only: 
                if e.LHE_Njets > 0 : sWeight = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)]
                elif e.LHE_Njets == 0 : 
                   if search(nickName, 'WJetsToLNu') : sWeight = sampleWeight['WJetsToLNu']
                   #else :   sWeight = sampleWeight['WJetsToLNuext']
                #print 'will now be using ',sWeight, e.LHE_Njets, nickName
            if DYJets and not DYIncl_only: 
                if e.LHE_Njets > 0 : sWeight = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
                elif e.LHE_Njets ==0 : sWeight = sampleWeight['DYJetsToLL']
                #print 'will now be using ',sWeight, e.LHE_Njets, nickName
            '''
            if group != 'data' :
		# the pu weight is the e.weight in the ntuples
		#print 'weights', group, nickName, e.Generator_weight, e.weight, i
                weight_pref = e.L1PreFiringWeight_Nom

                if 'prefireup' in systematic.lower() :  
                    try : weight_pref = e.L1PreFiringWeight_Up
                    except AttributeError : weight_pref = 1.

                if 'prefiredown' in systematic.lower() : 
                    try : weight_pref = e.L1PreFiringWeight_Down ## <------- This will change to _Down
                    except AttributeError : weight_pref = 1.
                #if e.evt == 2496649 : print 'first', e.weightPUtrue ,  e.Generator_weight , sWeight,  weight_pref
		weight = e.weightPUtrue * e.Generator_weight *sWeight * weight_pref
		weightFM = e.weightPUtrue * e.Generator_weight *sWeight * weight_pref


            weightCF = weight
            if i == 0 : print 'sample info ', e.weightPUtrue, e.Generator_weight, sWeight, 'for ', group, nickName, inTree.GetEntries()
       
            #weight=1.
            #if e.weightPUtrue ==-1 : e.weightPUtrue==1 

            #####sign
            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)


            ##############good ISO

            isSS = nbtagM==0 and nbtagL<2 and str(args.sign) == 'SS'
            isSR = nbtagM==0 and nbtagL<2 and str(args.sign) == 'OS'
            #isSR = nbtagM==0 and str(args.sign) == 'OS'
            isLSR = nbtagM==0 and nbtagL<2 and str(args.sign) == 'OSS'

            if printDebug :
		if cat[:2] == 'mm' :  
			if (e.iso_1 > mu_iso or e.iso_2 > mu_iso) : print 'failed mu_iso', cat, e.lumi, e.run, e.iso_1, e.iso_2
			if (abs(e.eta_1) > mu_eta or abs(e.eta_2) > mu_eta) : print 'failed mu_eta', cat, e.lumi, e.run, e.eta_1, e.eta_2
			if (e.mediumId_1 < 1 or e.mediumId_2 < 1) : print 'failed mu_Id', cat, e.lumi, e.run, e.mediumId_1, e.mediumId_2
			if (e.isGlobal_1 < 1 and e.isTracker_1 < 1) : print 'failed eGl_1 and isTrack_1', cat, e.lumi, e.run, e.isGlobal_1, e.isTracker_1
			if (e.isGlobal_2 < 1 and e.isTracker_2 < 1) : print 'failed eGl_2 and isTrack_2', cat, e.lumi, e.run, e.isGlobal_2, e.isTracker_2

	    if cat[:2] == 'mm' :  
                    if (e.iso_1 > mu_iso or e.iso_2 > mu_iso) : continue
                    if (abs(e.eta_1) > mu_eta or abs(e.eta_2) > mu_eta) : continue
                    if (e.mediumId_1 < 1 or e.mediumId_2 < 1) : continue
                    if (e.isGlobal_1 < 1 and e.isTracker_1 < 1) : continue
                    if (e.isGlobal_2 < 1 and e.isTracker_2 < 1) : continue

	    if cat[:2] == 'ee' :
                if e.iso_1 > el_iso or e.iso_2 > el_iso : continue
                if (abs(e.eta_1) > el_eta or abs(e.eta_2) > el_eta) : continue
	        if e.Electron_mvaFall17V2noIso_WP90_1 < 1 or e.Electron_mvaFall17V2noIso_WP90_2 < 1 : continue


            # and now tauWP cuts
	    if cat[2:] == 'em'  :
                if abs(e.eta_3) > el_eta : tight1 = False
	        if e.Electron_mvaFall17V2noIso_WP90_3 < 1 : tight1 = False
	        if e.iso_3 > el_iso  : tight1 = False

                if e.isGlobal_4 < 1 and e.isTracker_4 < 1  : tight2 = False
                if e.iso_4 > mu_iso : tight2 = False
                if e.mediumId_4  <1 : tight2 = False
                if abs(e.eta_4) > mu_eta : tight2 = False


		#if nickName == 'ZHToTauTau' and (e.evt % 100 == 0) :
		#    print("Event={0:8d} em iso_3={1:.3f} iso_4={2:.3f} WP90={3}".format(e.evt,e.iso_3,e.iso_4, e.Electron_mvaFall17V2noIso_WP90_3))
 
            if not tight1 or not tight2 : 
                if printDebug : print 'failed tight1 or tight2', cat, e.lumi, e.run, tight1, tight2
                continue

	    if cat[2:] == 'mt':
                if isSR and (e.isGlobal_3 < 1 and e.isTracker_3 < 1) : 
                    if printDebug : print 'failed isGl_3 and isTrack', cat, e.lumi, e.run, e.isGlobal_3, e.isTracker_3
                    tight3 = False
                if isSR and e.iso_3 > mu_iso  : 
                    if printDebug : print 'failed iso_3', cat, e.lumi, e.run, e.iso_3
                    tight3 = False
                if e.mediumId_3  <1 : 
                    if printDebug : print 'failed mID_3', cat, e.lumi, e.run, e.mediumId_3
                    tight3 = False
                if abs(e.eta_3) > mu_eta : 
                    if printDebug : print 'failed eta_3', cat, e.lumi, e.run, e.eta_3
                    tight3 = False

	    if (cat[2:] == 'et') :
                if e.Electron_mvaFall17V2noIso_WP90_3 < 1 : 
                    
                    if printDebug : print 'failed tight3 mva', cat, e.lumi, e.run, e.Electron_mvaFall17V2noIso_WP90_3
                    tight3 = False
                if isSR and e.iso_3 > el_iso : 
                    if printDebug : print 'failed iso_3', cat, e.lumi, e.run, e.iso_3
                    tight3 = False
                if abs(e.eta_3) > el_eta : 
                    if printDebug : print 'failed eta_3', cat, e.lumi, e.run, e.eta_3
                    tight3 = False

            
            ###############################################
            #               VSjet    VSmu     VSel
            # et           M (16)   VL (1)   T (32)
            # mt           M (16)   T (8)    VL (4)
            # tt           M (16)   VL (1)   VL (4)
            #
            # Tau_idDeepTau2017v2p1VSe	UChar_t	byDeepTau2017v2p1VSe  (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
            #Tau_idDeepTau2017v2p1VSjet	UChar_t	byDeepTau2017v2p1VSjet (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
            #Tau_idDeepTau2017v2p1VSmu	UChar_t	byDeepTau2017v2p1VSmu  (deepTau2017v2p1): bitmask 1 = VLoose, 2 = Loose, 4 = Medium, 8 = Tight
            #WPSR = 60  
	    if cat[2:] == 'tt' :
                    if isSR : 
			tight3 = e.idDeepTau2017v2p1VSjet_3 >=WPSR and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse
			tight4 = e.idDeepTau2017v2p1VSjet_4 >=WPSR and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse 
			#tight3 = e.idDeepTau2017v2p1VSjet_3 ==31 and e.idDeepTau2017v2p1VSmu_3 >= 1 and  e.idDeepTau2017v2p1VSe_3 >=7
			#tight4 = e.idDeepTau2017v2p1VSjet_4 ==31 and e.idDeepTau2017v2p1VSmu_4 >= 1 and  e.idDeepTau2017v2p1VSe_4 >=7 
                    if isSS : 
			#tight1 = e.idDeepTau2017v2p1VSjet_3 >0 and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse and e.idDeepTau2017v2p1VSjet_3 < WPSR+1
			#tight2 = e.idDeepTau2017v2p1VSjet_4 >0 and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse and e.idDeepTau2017v2p1VSjet_4 < WPSR+1
			tight3 = e.idDeepTau2017v2p1VSjet_3 >0  and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse
			tight4 = e.idDeepTau2017v2p1VSjet_4 >0 and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse 

			#tight3 = e.idDeepTau2017v2p1VSjet_3 >0
			#tight4 = e.idDeepTau2017v2p1VSjet_4 >0 

	    if cat[2:] == 'mt' : 
                if isSR : tight4 = e.idDeepTau2017v2p1VSjet_4 >=  WPSR and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse
                if isSS : tight4 = e.idDeepTau2017v2p1VSjet_4 >0 and  e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse

                #if isSS : tight4 = e.idDeepTau2017v2p1VSjet_4 ==1 
	    if cat[2:] == 'et' : 
                if isSR : tight4  = e.idDeepTau2017v2p1VSjet_4 >= WPSR and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= et_tau_vse
                if isSS : tight4  = e.idDeepTau2017v2p1VSjet_4 >0   and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= et_tau_vse

                #if isSS : tight4  = e.idDeepTau2017v2p1VSjet_4 ==1  
	    if cat[2:] == 'tt' :
	        if e.decayMode_3 == 5 or e.decayMode_3 == 6  : 
                    if printDebug : print 'failed decayMode ', cat, e.lumi, e.run, e.decayMode_4
                    continue
	        if e.decayMode_4 == 5 or e.decayMode_4 == 6  : 
                    if printDebug : print 'failed decayMode ', cat, e.lumi, e.run, e.decayMode_4
                    continue

	    if cat[2:] == 'mt' or cat[2:] == 'et' : 
	        if e.decayMode_4 == 5 or e.decayMode_4 == 6  : 
                    if printDebug : print 'failed decayMode ', cat, e.lumi, e.run, e.decayMode_4
                    continue

            if printDebug and isSR and (not tight3 or not tight4): print 'failed tight3 or tight4', cat, e.lumi, e.run, e.pt_1, e.pt_2, e.pt_3, e.pt_4, e.mll, e.m_sv, 'tight3', tight3, 'VSjet', e.idDeepTau2017v2p1VSjet_3, 'VSmu', e.idDeepTau2017v2p1VSmu_3, 'VSe', e.idDeepTau2017v2p1VSe_3, 'tight4', tight4, 'VSjet', e.idDeepTau2017v2p1VSjet_4, 'VSmu', e.idDeepTau2017v2p1VSmu_4, 'VSe', e.idDeepTau2017v2p1VSe_4

            '''
	    if cat[2:] == 'tt' :
                    tight1 = e.idDeepTau2017v2p1VSjet_3 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_3 > 0 and  e.idDeepTau2017v2p1VSe_3 > 3
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_4 > 0 and  e.idDeepTau2017v2p1VSe_4 > 3 
                    #print  e.idDeepTau2017v2p1VSjet_3 & 16, e.idDeepTau2017v2p1VSjet_3 & 8 , e.idDeepTau2017v2p1VSjet_3 & 64
	    if cat[2:] == 'mt' : tight2 = e.idDeepTau2017v2p1VSjet_4 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_4 > 7 and  e.idDeepTau2017v2p1VSe_4 > 3
	    if cat[2:] == 'et' : tight2  = e.idDeepTau2017v2p1VSjet_4 > WPSR-1 and e.idDeepTau2017v2p1VSmu_4 > 0 and  e.idDeepTau2017v2p1VSe_4 > 31
            '''
            #added this
	    isL3L = False
	    isL4L = False

	    if  isLSR :
		if group == 'Other' or group =='ZZ' :
                    
		    dm3=e.decayMode_3
		    dm4=e.decayMode_4
                    #Flavour of genParticle for MC matching to status==1 electrons or photons: 1 = prompt electron (including gamma*->mu mu), 15 = electron from prompt tau, 22 = prompt photon (likely conversion), 5 = electron from b, 4 = electron from c, 3 = electron from light or unknown, 0 = unmatched
                    if cat[2:]=='mt' :
                        if tight3 and (e.gen_match_3 == 15  or e.gen_match_3 ==1)  : isL3L = True
                        #if tight3 and (e.gen_match_3 != 15  )  : isL3L = True
                        #if tight3 and (e.gen_match_3 == 15  )  : isL3L = True
                        if tight4 and e.gen_match_4 != 0  : isL4L = True
                        #if tight3 and (e.gen_match_3 != 15 and e.gen_match_3 !=1 )  : isL3L = True

                    if cat[2:]=='et' :
                        if tight3 and (e.gen_match_3 == 15  or e.gen_match_3 ==1)  : isL3L = True
                        #if tight3 and (e.gen_match_3 == 15  )  : isL3L = True
                        if tight4 and e.gen_match_4 != 0  : isL4L = True
                        #if tight3 and (e.gen_match_3 != 15 and e.gen_match_3 !=1 )  : isL3L = True

                    if cat[2:]=='tt' :
                        if tight3 and e.gen_match_3 != 0  : isL3L = True
                        if tight4 and e.gen_match_4 != 0  : isL4L = True
                        #if tight3 and e.gen_match_3 == 0  : isL3L = True


		    #print cat, tight3, e.gen_match_3, tight4, e.gen_match_4
		    if isL3L or isL4L :
                        if weight< 0. : weight=0
			hGroup='Reducible'
                        fW1, fW2, fW0 = FF.getFakeWeightsvspTvsDM(cat[2:], e.pt_3, e.pt_4, WP, dm3, dm4)

			if isL3L and not isL4L :
			    weight *=-fW1

			if isL4L and not isL3L :
			    weight *=-fW2

			if isL3L and  isL4L :
			    weight *=fW0
                        #print group, hGroup, isL3L, isL4L, fW1, fW2, fW0, nbtag
                    

            #if not isSS and not isSR : continue

            if group!='data' and hGroup!='Reducible' and  isLSR : continue
 
            if group != 'data' :
                if  isSR or isLSR :
                    if not tight1 or not tight2 : continue
                    if not tight3 or not tight4 : continue

                #if  isLSR :
                #    if not tight1 or not tight2 : continue


            if isSS : 
                if  (not tight1 or not tight2) : continue
                if  (not tight3 or not tight4) : continue

            if not dataDriven and (not tight1 or not tight2) : continue
            if not dataDriven and (not tight3 or not tight4) : continue


            #if cat[2:] =='tt' : print e.idDeepTau2017v2p1VSjet_3, WPSR , e.idDeepTau2017v2p1VSmu_3, tt_tau_vsmu, e.idDeepTau2017v2p1VSe_3, tt_tau_vse, tight1, tight2


            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
	    hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
	    hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)


            ######### nbtag
	    if e.mll > 106 or e.mll<76: 
                if printDebug : print 'failed mll cut', cat, e.lumi, e.run, e.evt, e.mll
                continue
	    #try :
	    #if nbtag > 0 and str(args.sign) == 'OS': continue #commented this
	    if nbtagM > 0 or nbtagL>1: 
	    #if nbtagM > 0 : 
		if printDebug: print 'failed btag cut', cat, e.lumi, e.run, e.evt, nbtagL, nbtagM
                continue #commented this
	    #except TypeError :


            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

            ########### Trigger
            ################### Trigger SF
 
            

            #if group == 'data' :
            
            if DD[cat].checkEvent(e,cat) : 
		if printDebug: print 'failed DD check', cat, e.lumi, e.run, e.evt, e.mll
                continue 

            if isSS : hGroup = 'SSR'


            ##### btag
            if group != 'data' and dobtag:
		nj= njets
		if nj > 0 :
		    #for ib in range(0, int(nj)) :
                    #    print nj, ib, e.jeta[ib], e.jpt[ib], i, cat
		    for ib in range(0, int(nj)) :
                        try : 
                            #print 'njets', nj, ib, reader_b.eval_auto_bounds( 'central', 0,    abs(jeta[ib]), jpt[ib], jCSV[ib]),  reader_b.eval_auto_bounds( 'central', 1,    abs(jeta[ib]), jpt[ib], jCSV[ib]), reader_b.eval_auto_bounds( 'central', 2,    abs(jeta[ib]), jpt[ib], jCSV[ib]), 'eta:', abs(jeta[ib]), 'pt:', jpt[ib], 'dCSV:', jCSV[ib], 'flavour:', abs(jflavour[ib]), e.lumi, e.run, e.evt
			    if abs(jflavour[ib]) == 5 : 
				btag_sf *= reader_b.eval_auto_bounds( 'central', 0,    abs(jeta[ib]), jpt[ib], jCSV[ib])
			    elif abs(jflavour[ib]) == 4 : 
				#btag_sf *= reader_c.eval_auto_bounds( 'central', 1,    abs(jeta[ib]), jpt[ib])
				btag_sf *= reader_b.eval_auto_bounds( 'central', 1,    abs(jeta[ib]), jpt[ib], jCSV[ib])
			    #if abs(jflavour[ib]) < 4 or abs(jflavour[ib]) == 21 :
			    else:
				#btag_sf *= reader_light.eval_auto_bounds( 'central', 2,    abs(jeta[ib]), jpt[ib])
				if abs(jflavour[ib]) != 0 and  abs(jflavour[ib]) != 5 and  abs(jflavour[ib]) != 4 : btag_sf *= reader_b.eval_auto_bounds( 'central', 2,    abs(jeta[ib]), jpt[ib], jCSV[ib])
                                
                            #print '---------------------', ib, nj, btag_sf

                        except IndexError : btag_sf *= 1.
              
		weight *= btag_sf
	   	weightFM *= btag_sf


            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

            ########### tauID
            tauV3uncor.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
            tauV4uncor.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)

            if group !='data' and doCorrectTES :
                tauV3uncor.SetPtEtaPhiM(e.pt_uncor_3, e.eta_3, e.phi_3, e.m_uncor_3)
                tauV4uncor.SetPtEtaPhiM(e.pt_uncor_4, e.eta_4, e.phi_4, e.m_uncor_4)

            tauV3.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
            tauV4.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)

            if not doCorrectTES : 
                tauV3uncor = tauV3
                tauV4uncor = tauV4

	    MetV.SetPx(met * cos (metphi))
	    MetV.SetPy(met * sin (metphi))
	    met_x = met * cos(metphi)
	    met_y = met * sin(metphi)
	    #metcor = met

            mass = 0.0005
            if cat[:2] == 'mm' : mass = .105
            L1.SetPtEtaPhiM(e.pt_1, e.eta_1,e.phi_1,mass)
            L2.SetPtEtaPhiM(e.pt_2, e.eta_2,e.phi_2,mass)
	    L1uncor.SetPtEtaPhiM(e.pt_1, e.eta_1,e.phi_1,mass)
	    L2uncor.SetPtEtaPhiM(e.pt_2, e.eta_2,e.phi_2,mass)
	    #L1uncorMC.SetPtEtaPhiM(e.pt_1_tr, e.eta_1_tr,e.phi_1_tr,e.m_1_tr)
	    #L2uncorMC.SetPtEtaPhiM(e.pt_2_tr, e.eta_2_tr,e.phi_2_tr,e.m_2_tr)

            if group !='data' and doCorrectTES:
		L1uncor.SetPtEtaPhiM(e.pt_uncor_1, e.eta_1,e.phi_1,mass)
		L2uncor.SetPtEtaPhiM(e.pt_uncor_2, e.eta_2,e.phi_2,mass)

            if not doCorrectTES : 
                L1uncor=L1
                L2uncor=L2

            isDM0_3, isDM1_3, isDM10_3, isDM11_3 = False, False, False, False
            isDM0_4, isDM1_4, isDM10_4, isDM11_4 = False, False, False, False
	    cor3, cor4= 1, 1
	    cor3Up, cor3Down, cor4Up, cor4Down = 1, 1, 1, 1
	    cor1, cor2 = 1., 1.



            #if doCorrectTES and group != 'data' and (cat[2:] == 'et' or cat[2:]  == 'mt' or cat[2:]  == 'tt') :
            if doCorrectTES and group != 'data' and (cat[2:] == 'et' or cat[2:]  == 'mt' or cat[2:]  == 'tt') :

                
		if cat[2:] == 'tt':
                    dm3 = e.decayMode_3
		    dmm3='DM{0:d}'.format(dm3)

		    isDM0_3 =  '1prong' in systematic and 'zero' not in systematic and dm3 == 0
		    isDM1_3 =  '1prong' in systematic and 'zero' in systematic and dm3 == 1
		    isDM10_3 =  '3prong' in systematic and 'zero' not in systematic and dm3 == 10
		    isDM11_3 =  '3prong' in systematic and 'zero' in systematic and dm3 == 11


                    if dm3 != 0 and dm3 != 1 and dm3!=10 and dm3!=11 : 
              
                        if printDebug: print 'failed dm3 ', cat, e.lumi, e.run, e.evt, dm3
                        continue 

		    if e.gen_match_3 == 5 : 
			cor3Down, cor3, cor3Up = testool.getTES(e.pt_uncor_3,e.decayMode_3,e.gen_match_3, unc='All')

		    if e.gen_match_3 == 2 or e.gen_match_3 == 4 : 
			cor3= 1 + weights_muTotauES[dmm3]*0.01
			cor3Up = cor3
			cor3Down = cor3

		    if e.gen_match_3 == 1 or e.gen_match_3 == 3 : 
			cor3 = festool.getFES(e.eta_3,e.decayMode_3,e.gen_match_3) #no need to consider Up/Down as we have prong systematic that is about gen_match=5
			cor3Up = cor3
			cor3Down = cor3

		if cat[2:] == 'et' or cat[2:] == 'mt' or cat[2:] == 'tt':

                    dm4 = e.decayMode_4
		    dmm4='DM{0:d}'.format(dm4)

		    isDM0_4 =  '1prong' in systematic and 'zero' not in systematic and dm4 == 0
		    isDM1_4 =  '1prong' in systematic and 'zero' in systematic and dm4 == 1
		    isDM10_4 =  '3prong' in systematic and 'zero' not in systematic and dm4 == 10
		    isDM11_4 =  '3prong' in systematic and 'zero' in systematic and dm4 == 11

                    if dm4 != 0 and dm4 != 1 and dm4!=10 and dm4!=11 : 
                        if printDebug: print 'failed dm4 ', cat, e.lumi, e.run, e.evt, dm4
                        continue
		   
		    if e.gen_match_4 == 5 : 
			cor4Down, cor4, cor4Up = testool.getTES(e.pt_uncor_4,e.decayMode_4,e.gen_match_4, unc='All')

		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 : 
			cor4=1+ weights_muTotauES[dmm4]*0.01
                        cor4Up = cor4
                        cor4Down = cor4

		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 : 
			cor4 = festool.getFES(e.eta_4,e.decayMode_4,e.gen_match_4)
                        cor4Up = cor4
                        cor4Down = cor4


                
		isp1 =  isDM0_3 or isDM1_3 or isDM10_3 or isDM11_3 
		if isDM0_3 or isDM1_3 or isDM10_3 or isDM11_3 :
		    if 'Up' in systematic : 
			cor3 = cor3Up
		    if 'Down' in systematic : 
			cor3 = cor3Down
                    #print '-------------------->3', cor3, cor3Up, cor4Down, cat, e.evt

		isp2 =  isDM0_4 or isDM1_4 or isDM10_4 or isDM11_4 
		if isDM0_4 or isDM1_4 or isDM10_4 or isDM11_4 :
		    if 'Up' in systematic : 
			cor4 = cor4Up
		    if 'Down' in systematic : 
			cor4 = cor4Down
                    #print '-------------------->4', cor4, cor4Up, cor4Down, cat, e.evt
                
                #oldMET = MetV.Pt()
                #oldMETV = MetV
		MetV +=( tauV3uncor + tauV4uncor - (tauV3uncor*cor3 + tauV4uncor*cor4))
                tauV3uncor *= cor3
                tauV4uncor *= cor4
                #e.pt_3 = tauV3uncor.Pt()
                #e.pt_4 = tauV4uncor.Pt()
                #e.phi_3 = tauV3uncor.Phi()
                #e.phi_4 = tauV4uncor.Phi()

                #if cat =='mmmt':
                #print e.evt, cat, 'TAUSS', p3, tauV3uncor.Pt(), e.pt_uncor_3, 'pt3_un/cor', e.pt_uncor_3/tauV3uncor.Pt(), p3/tauV3uncor.Pt(), p4, tauV4uncor.Pt(), e.pt_uncor_4, 'pt4_un/cor', e.pt_uncor_4/tauV4uncor.Pt(), p4/tauV4uncor.Pt(), 'e.met', e.met, 'noES', e.metNoTauES, 'new met', MetV.Pt(), 'gmatch', e.gen_match_3, 'dm3', e.decayMode_3, 'gm4', e.gen_match_4, 'dm4', e.decayMode_4, systematic, 'COR3', cor3, cor3Up, cor3Down, 'COR4', cor4, cor4Up, cor4Down, isp1, isp2
                #parint e.evt, cat, isp1,  e.gen_match_3, e.decayMode_3, isp2, e.gen_match_4, e.decayMode_4, 'DM3...', isDM0_3, isDM1_3, isDM10_3 , isDM11_3 , 'DM4...', isDM0_4 , isDM1_4 , isDM10_4 , isDM11_4
                if 'scale_m' in systematic : 
                    sign = 1
                    if 'Down' in systematic : sign = -1
	            #if cat[:2] == 'mm' or cat[2:] == 'mt':  
	            if cat[:2] == 'mm' :  

                        cor1= 1.
                        cor2= 1.
			if  'scale_m_etalt1p2' in systematic  :
			    if abs(e.eta_1) < 1.2 : cor1 = 1 + sign*weights_muES['eta0to1p2']*0.01
			    if abs(e.eta_2) < 1.2 : cor2 = 1 + sign*weights_muES['eta0to1p2']*0.01

			if  'scale_m_eta1p2to2p1' in systematic : 
			    if abs(e.eta_1) > 1.2 and abs(e.eta_1) < 2.1 : cor1 = 1+ sign * weights_muES['eta1p2to2p1']*0.01
			    if abs(e.eta_2) > 1.2 and abs(e.eta_2) < 2.1 : cor2 = 1+ sign * weights_muES['eta1p2to2p1']*0.01

			if  'scale_m_etagt2p1' in systematic :
			    if abs(e.eta_1) > 2.1 : cor1 = 1+ sign * weights_muES['etagt2p1']*0.01
			    if abs(e.eta_2) > 2.1 : cor2 = 1+ sign * weights_muES['etagt2p1']*0.01

                    
	            if cat[2:] == 'mt':  
			cor3 = 1.

			if  'scale_m_etalt1p2' in systematic  :
			    if abs(e.eta_3) < 1.2 : cor3 = 1 + sign*weights_muES['eta0to1p2']*0.01

			if  'scale_m_eta1p2to2p1' in systematic : 
			    if abs(e.eta_3) > 1.2 and abs(e.eta_3) < 2.1 : cor3 = 1+ sign * weights_muES['eta1p2to2p1']*0.01

			if  'scale_m_etagt2p1' in systematic :
			    if abs(e.eta_3) > 2.1 : cor3 = 1+ sign * weights_muES['etagt2p1']*0.01


		    MetV +=( L1uncor + L2uncor  + tauV3uncor -(L1uncor*cor1 + L2uncor*cor2 + tauV3uncor*cor3))
		    L1uncor *=cor1
		    L2uncor *=cor2

		    #e.pt_1 = L1uncor.Pt()
		    #e.pt_2 = L2uncor.Pt()
		    #e.phi_1 = L1uncor.Phi()
		    #e.phi_2 = L2uncor.Phi()
		    tauV3uncor *=cor3
		    #e.pt_3 = tauV3uncor.Pt()
		    #e.phi_3 = tauV3uncor.Phi()

                if 'scale_e' in systematic : 
                    sign = 1
                    if 'Down' in systematic : sign = -1
	            if cat[:2] == 'ee' :  
			cor1, cor2 = 1., 1.
                        if  abs(e.eta_1) < 1.2 : cor1 = 1 + sign*weights_electronES['eta0to1p2']*0.01
                        if  abs(e.eta_2) < 1.2 : cor2 = 1 + sign*weights_electronES['eta0to1p2']*0.01

                        if  abs(e.eta_1) > 1.2 and abs(e.eta_1) < 2.1 :   cor1=   1+ sign * weights_electronES['eta1p2to2p1']*0.01
                        if  abs(e.eta_2) > 1.2 and abs(e.eta_2) < 2.1 :   cor2=   1+ sign * weights_electronES['eta1p2to2p1']*0.01

                        if  abs(e.eta_1) > 2.1 : cor1 = 1+ sign * weights_electronES['etagt2p1']*0.01
                        if  abs(e.eta_2) > 2.1 : cor2 = 1+ sign * weights_electronES['etagt2p1']*0.01


	            if cat[2:] == 'et':  
			cor3 = 1.

                        if  abs(e.eta_3) < 1.2 : cor3 = 1 + sign* weights_electronES['eta0to1p2']*0.01
                        if  abs(e.eta_3) > 1.2 and abs(e.eta_3) < 2.1 :    cor3 =   1+ sign * weights_electronES['eta1p2to2p1']*0.01
                        if  abs(e.eta_3) > 2.1 : cor3 = 1+ sign * weights_electronES['etagt2p1']*0.01

		    MetV +=( L1uncor + L2uncor + tauV3uncor - (L1uncor*cor1 + L2uncor*cor2 + tauV3uncor*cor3))
		    L1uncor *=cor1
		    L2uncor *=cor2
		    #e.pt_1 = L1uncor.Pt()
		    #e.pt_2 = L2uncor.Pt()
		    #e.phi_1 = L1uncor.Phi()
		    #e.phi_2 = L2uncor.Phi()

		    tauV3uncor *=cor3
		    #e.pt_3 = tauV3uncor.Pt()
		    #e.phi_3 = tauV3uncor.Phi()


	       
                met = MetV.Pt()
                metphi = MetV.Phi()
                
            H_LT = tauV3uncor.Pt() + tauV4uncor.Pt()
            if cat[2:] == 'tt' and H_LT < 60 : 
                if printDebug: print 'failed H_LT cut ', cat, e.lumi, e.run, e.evt, H_LT
                continue

            trigw=1
            trigw1=1
            trigw2=1
            tracking_sf = 1.
            lepton_sf = 1.
             
            #L1uncor = L1
            #L2uncor = L2
            #tauV3uncor=tauV3
            #tauV4uncor=tauV4

            #print e.evt, cat, 'TAUSS', p3, tauV3uncor.Pt(), e.pt_uncor_3, 'pt3_un/cor', e.pt_uncor_3/tauV3uncor.Pt(), p3/tauV3uncor.Pt(), p4, tauV4uncor.Pt(), e.pt_uncor_4, 'pt4_un/cor', e.pt_uncor_4/tauV4uncor.Pt(), p4/tauV4uncor.Pt(), 'e.met', e.met, 'noES', e.metNoTauES, 'new met', MetV.Pt(),  systematic
            
            if group != 'data' :
		if cat[:2] == 'mm' :      
		    trigw = 1.
		    
		    if e.isTrig_1==1 : 
			wspace.var("m_pt").setVal(L1uncor.Pt())
			wspace.var("m_eta").setVal(e.eta_1)
			trigw *=  wspace.function("m_trg_ic_ratio").getVal()

		    if e.isTrig_1==-1 : 
			wspace.var("m_pt").setVal(L2uncor.Pt())
			wspace.var("m_eta").setVal(L2uncor.Pt())
			trigw *=  wspace.function("m_trg_ic_ratio").getVal()

		    if  e.isTrig_1==2 : 
			wspace.var("m_pt").setVal(L1uncor.Pt())
			wspace.var("m_eta").setVal(e.eta_1)
			trigw1 =  wspace.function("m_trg_ic_ratio").getVal()

			wspace.var("m_pt").setVal(L2uncor.Pt())
			wspace.var("m_eta").setVal(e.eta_2)
			trigw2 =  wspace.function("m_trg_ic_ratio").getVal()

			trigw = float( 1-(1-trigw1) * (1-trigw2))

		    wspace.var("m_pt").setVal(L1uncor.Pt())
		    wspace.var("m_eta").setVal(e.eta_1)
		    lepton_sf = wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf = wspace.function("m_trk_ratio").getVal()
		    wspace.var("m_pt").setVal(L2uncor.Pt())
		    wspace.var("m_eta").setVal(e.eta_2)
		    lepton_sf *= wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("m_trk_ratio").getVal()


		if cat[:2] == 'ee' :      
		    trigw = 1.
		    
		    if e.isTrig_1==1 : 
			wspace.var("e_pt").setVal(L1uncor.Pt())
			wspace.var("e_eta").setVal(e.eta_1)
			trigw *=  wspace.function("e_trg_ic_ratio").getVal()
                        #if e.evt == 2496649 : print 'it was trig', e.isTrig_1, e.pt_1, e.eta_1

		    if e.isTrig_1==-1 : 
			wspace.var("e_pt").setVal(L2uncor.Pt())
			wspace.var("e_eta").setVal(e.eta_2)
			trigw *=  wspace.function("e_trg_ic_ratio").getVal()
                        #if e.evt == 2496649 : print 'it was trig', e.isTrig_1, e.pt_2, e.eta_2

		    if e.isTrig_1==2 : 
			wspace.var("e_pt").setVal(L1uncor.Pt())
			wspace.var("e_eta").setVal(e.eta_1)
			trigw1 =  wspace.function("e_trg_ic_ratio").getVal()

			wspace.var("e_pt").setVal(L2uncor.Pt())
			wspace.var("e_eta").setVal(e.eta_2)
			trigw2 =  wspace.function("e_trg_ic_ratio").getVal()

			trigw = float( 1-(1-trigw1) * (1-trigw2))
                        #if e.evt == 2496649 : print 'it was trig', e.isTrig_1, e.pt_1, e.eta_1, e.pt_2, e.eta_2, trigw, (1-trigw1), (1-trigw2) ,  float( 1-(1-trigw1) * (1-trigw2))

		    wspace.var("e_pt").setVal(L1uncor.Pt())
		    wspace.var("e_eta").setVal(e.eta_1)
		    lepton_sf = wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf = wspace.function("e_trk_ratio").getVal()
		    wspace.var("e_pt").setVal(L2uncor.Pt())
		    wspace.var("e_eta").setVal(e.eta_2)
		    lepton_sf *= wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("e_trk_ratio").getVal()

		if cat[2:] =='et' : 
		    wspace.var("e_pt").setVal(tauV3uncor.Pt())
		    wspace.var("e_eta").setVal(tauV3uncor.Eta())
		    lepton_sf *= wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("e_trk_ratio").getVal()

		if cat[2:] =='mt' : 
		    wspace.var("m_pt").setVal(tauV3uncor.Pt())
		    wspace.var("m_eta").setVal(tauV3uncor.Eta())
		    lepton_sf *= wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("m_trk_ratio").getVal()

		if cat[2:] =='et' or cat[2:] =='mt' or cat[2:] =='tt': 
		    wspace.var("t_pt").setVal(tauV4uncor.Pt())
		    wspace.var("t_eta").setVal(tauV4uncor.Eta())

		if cat[2:] =='em' : 
		    wspace.var("e_pt").setVal(tauV3uncor.Pt())
		    wspace.var("e_eta").setVal(tauV3uncor.Eta())
		    lepton_sf *= wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("e_trk_ratio").getVal()
		    wspace.var("m_pt").setVal(tauV4uncor.Pt())
		    wspace.var("m_eta").setVal(tauV4uncor.Eta())
		    lepton_sf *= wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("m_trk_ratio").getVal()


		#if e.isDoubleTrig!=0 and e.isTrig_1 == 0 : trigw = 1
                if abs(trigw) > 2 : trigw = 1
                if abs(lepton_sf) > 2 : lepton_sf = 1
                if abs(tracking_sf) > 2 : tracking_sf = 1
		weight *= trigw 
		weightFM *= trigw 
                #if e.evt == 2496649 : print 'second', weight, trigw, lepton_sf, tracking_sf, cat, e.pt_1, e.pt_2, e.pt_3, e.pt_4
           


            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

        
	    if group != 'data' :
		weight *= lepton_sf
		weightFM *= lepton_sf

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

	    if group != 'data' :
		weight *= tracking_sf
		weightFM *= tracking_sf

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

            ##########

            fW1, fW2, fW0 = 0,0,0

	    #if group != 'data' :
            #    if  not tight1 or not tight2 : continue
               

	    if group == 'data' :
		if dataDriven :
		    dm3=e.decayMode_3
		    dm4=e.decayMode_4
                    #if dm1 < 0 or dm2 < 0 : print 'problem with data ? ', dm3, dm4, e.pt_3, e.pt_4
		    #fW1, fW2, fW0 = getFakeWeightsvspT(cat[2:], e.pt_3, e.pt_4, WP)
		    fW1, fW2, fW0 = FF.getFakeWeightsvspTvsDM(cat[2:], e.pt_3, e.pt_4, WP, dm3, dm4)
		    #fW1, fW2, fW0 = getFakeWeightsvspT(cat[2:], e.pt_3, e.pt_4, WP, dm3, dm4)

                    ## in VR we allow loose data only of btag>0, as the SS, btag==0 is the estimation region
                    #if not tight1 or not tight2 and (str(args.sign) == 'SS' and  nbtag==0) : continue  

                    if isSR: 
			if not tight3 and tight4 : 
			    ww = fW1          
			    hGroup = 'f1'
			    hGroup = 'Reducible'
			elif tight3 and not tight4 : 
			    ww = fW2
			    hGroup = 'f2'
			    hGroup = 'Reducible'
			elif not tight3 and not tight4 : 
			    ww = -fW0
			    hGroup = 'fakes'
			    hGroup = 'Reducible'
			else : 
			    hGroup = 'data'
                        '''
			if cat[2:] == 'mt' or cat[2:] == 'et' :#ignore the em channel 
                            if not tight3 : continue
                            if tight3 and not tight4 : ww=fW2

                        if tight3 and  tight4 : hGroup='data'
                        '''

                    if isSS:
                        if tight3 and tight4 :  hGroup = 'SSR' 

                    #print 'hGroup', hGroup, nbtag, cat

		else :
		    hGroup = 'data'
		    #print("group = data  cat={0:s} tight1={1} tight2={2} ww={3:f}".format(cat,tight1,tight2,ww))
                    #if not (tight3 and tight4) : continue

	
	    else : 
		#print("Good MC event: group={0:s} nickName={1:s} cat={2:s} gen_match_1={3:d} gen_match_2={4:d}".format(
		#    group,nickName,cat,e.gen_match_1,e.gen_match_2))
		if dataDriven :   # include only events with MC matching
                    extratag='noL'
		    if cat[2:] == 'em'  :
			if e.gen_match_3 != 15 and 'noL' in extratag : isfakemc1 = True
			if e.gen_match_3 != 15 and e.gen_match_3 !=1 and 'wL' in extratag : isfakemc1 = True
                        '''
			if  e.gen_match_3 == 0 : hGroup = 'jfl1'
			if  e.gen_match_3 == 1 : hGroup = 'lfl1'
			if  e.gen_match_3 == 3 : hGroup = 'ljfl1'
			if  e.gen_match_3 == 4 : hGroup = 'cfl1'
			if  e.gen_match_3 == 5 : hGroup = 'bfl1'
			if  e.gen_match_3 == 22 : hGroup = 'gfl1'
                        '''

			if e.gen_match_4 != 15  and 'noL' in extratag: isfakemc2 = True
			#if not e.gen_match_4 != 15 and e.gen_match_4 !=1  and 'wL' in extratag: isfakemc2 = True
			if not e.gen_match_4 != 15  and 'wL' in extratag: isfakemc2 = True
                        '''
			if  e.gen_match_4 == 0 : hGroup = 'jfl2'
			if  e.gen_match_3 == 1 : hGroup = 'lfl2'
			if  e.gen_match_4 == 3 : hGroup = 'ljfl2'
			if  e.gen_match_4 == 4 : hGroup = 'cfl2'
			if  e.gen_match_4 == 5 : hGroup = 'bfl2'
                        '''
			
		    if cat[2:] == 'et' or cat[2:] == 'mt' :
			if e.gen_match_3 != 15  and e.gen_match_3 !=1 and 'noL' in extratag: isfakemc1 = True
			#if e.gen_match_3 != 15 and e.gen_match_3 !=1  and 'wL' in extratag: isfakemc1 = True
			if e.gen_match_3 != 15   and 'wL' in extratag: isfakemc1 = True

                        '''
			if  e.gen_match_3 == 0 : hGroup = 'jfl1'
			if  e.gen_match_3 == 1 : hGroup = 'lfl1'
			if  e.gen_match_3 == 3 : hGroup = 'ljfl1'
			if  e.gen_match_3 == 4 : hGroup = 'cfl1'
			if  e.gen_match_3 == 5 : hGroup = 'bfl1'
			if  e.gen_match_3 == 22 : hGroup = 'gfl1'
                        '''

			if e.gen_match_4 == 0  :
                            isfakemc2 = True
                            #hGroup = 'jft2'

			
		    if cat[2:] == 'tt' :
			if e.gen_match_3 == 0  :
                            isfakemc1 = True
                            #hGroup = 'jft1'
			if e.gen_match_4 == 0  :
                            isfakemc2 = True
                            #hGroup = 'jft2'
		    
            weightFM=ww
            if  isSignal : 
                isfakemc1 = False
                isfakemc2 = False
            #if group != 'data' and group!='Signal' :
            #    if not isfakemc1 or not isfakemc2  : continue



            '''
	    if cat[:2] == 'mm' :  
		L1g.SetPtEtaPhiM(e.pt_1_tr, e.eta_1_tr,e.phi_1_tr,muonMass)
		L2g.SetPtEtaPhiM(e.pt_2_tr, e.eta_2_tr,e.phi_2_tr,muonMass)

		L1.SetPtEtaPhiM(e.pt_1, e.eta_1,e.phi_1,muonMass)
		L2.SetPtEtaPhiM(e.pt_2, e.eta_2,e.phi_2,muonMass)
	    if cat[:2] == 'ee' :  
		L1g.SetPtEtaPhiM(e.pt_1_tr, e.eta_1_tr,e.phi_1_tr,electronMass)
		L2g.SetPtEtaPhiM(e.pt_2_tr, e.eta_2_tr,e.phi_2_tr,electronMass)
		L1.SetPtEtaPhiM(e.pt_1, e.eta_1,e.phi_1,electronMass)
		L2.SetPtEtaPhiM(e.pt_2, e.eta_2,e.phi_2,electronMass)



            if group != 'data' and not isSignal:


	        # recoils
		njetsforrecoil = e.njets
		if (isW)  : njetsforrecoil = e.njets+1
                if isW or isDY :
		    boson = TLorentzVector()
		    if cat[:2] == 'mm' :  
			boson += L1g
			boson += L2g

		    if cat[:2] == 'ee' :  
			boson += L1g
			boson += L2g
                    mett = recoilCorrector.CorrectByMeanResolution( met_x, met_y, boson.Px(), boson.Py(), boson.Px(), boson.Py(), int(njetsforrecoil))
		    metcor = sqrt(mett[0]* mett[0] + mett[1]*mett[1])
		    met_x = mett[0]
		    met_y = mett[1]
		    MetVcor.SetPx(mett[0])
	      	    MetVcor.SetPy(mett[1])

            '''

		# leptons faking taus // muon->tau
            if group != 'data' and (cat[2:] == 'et' or cat[2:]  == 'mt' or cat[2:]  == 'tt') :
                varTID =''
                if 'tauid' in systematic  and 'Up' in systematic : varTID = 'Up'
                if 'tauid' in systematic  and 'Down' in systematic : varTID = 'Down'

                tau3pt20, tau3pt25, tau3pt30, tau3pt35, tau3pthigh = False, False, False, False, False
		if 'pt20to25' in systematic and  tauV3uncor.Pt() > 20 and  tauV3uncor.Pt() < 25 : tau3pt20 = True
		if 'pt25to30' in systematic and  tauV3uncor.Pt() > 25 and  tauV3uncor.Pt() < 30 : tau3pt25 = True
		if 'pt30to35' in systematic and  tauV3uncor.Pt() > 30 and  tauV3uncor.Pt() < 35 : tau3pt30 = True
		if 'pt35to40' in systematic and tauV3uncor.Pt() > 35 and  tauV3uncor.Pt() < 40 : tau3pt35 = True
		if 'ptgt40' in systematic and  tauV3uncor.Pt() > 40:  tau3pthigh = True

                tau4pt20, tau4pt25, tau4pt30, tau4pt35, tau4pthigh = False, False, False, False, False
		if 'pt20to25' in systematic and  tauV4uncor.Pt() > 20 and  tauV4uncor.Pt() < 25 : tau4pt20 = True
		if 'pt25to30' in systematic and  tauV4uncor.Pt() > 25 and  tauV4uncor.Pt() < 30 : tau4pt25 = True
		if 'pt30to35' in systematic and  tauV4uncor.Pt() > 30 and  tauV4uncor.Pt() < 35 : tau4pt30 = True
		if 'pt35to40' in systematic and  tauV4uncor.Pt() > 35 and  tauV4uncor.Pt() < 40 : tau4pt35 = True
		if 'ptgt40' in systematic and  tauV4uncor.Pt() > 40:  tau4pthigh = True
                
		if  cat[2:] == 'et' :
			
		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  
			if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) :  
			    weightTID *= antiEleSFToolT.getSFvsEta(e.eta_4,e.gen_match_4, unc=varTID)
                        else : 
			    weightTID *= antiEleSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)

		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  
			if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) :  
                            weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4, unc=varTID)
                        else : 
                            weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

		if  cat[2:] == 'mt' :


		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  
			if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) :  
                            weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4, unc=varTID)
                        else : 
                            weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  
			if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) : 
                            weightTID *= antiMuSFToolT.getSFvsEta(e.eta_4,e.gen_match_4, unc=varTID)
			else : 
                            weightTID *= antiMuSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)


		if  cat[2:] == 'tt' :

		    #muon faking _3 tau
		    if e.gen_match_3 == 2 or e.gen_match_3 == 4 : 
			if  (tau3pt20 or tau3pt25 or tau3pt30 or tau3pt35 or tau3pthigh) :  
                            weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3, unc=varTID)
                        else: 
                            weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3)

		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 : 
	                if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) : 
                            weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4, unc=varTID)
                        else : 
                            weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

		    if e.gen_match_3 == 1 or e.gen_match_3 == 3 : 
			if  (tau3pt20 or tau3pt25 or tau3pt30 or tau3pt35 or tau3pthigh) :  
			    weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3, unc=varTID)
                        else : 
			    weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3)

		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 : 
	                if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) : 
		            weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4, unc=varTID)
                        else : 
		            weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4)

		    if e.gen_match_3 == 5 : 
			if  (tau3pt20 or tau3pt25 or tau3pt30 or tau3pt35 or tau3pthigh) :  
			    weightTID *= tauSFTool.getSFvsPT(tauV3uncor.Pt(),e.gen_match_3, unc=varTID)
                        else : 
			    weightTID *= tauSFTool.getSFvsPT(tauV3uncor.Pt(),e.gen_match_3)


		if  cat[2:] == 'tt'  or cat[2:] == 'mt' or cat[2:] == 'et' :

		    if e.gen_match_4 == 5 : 
	                if  (tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh) : 
			    weightTID *= tauSFTool.getSFvsPT(tauV4uncor.Pt(),e.gen_match_4, unc=varTID)
                        else : 
			    weightTID *= tauSFTool.getSFvsPT(tauV4uncor.Pt(),e.gen_match_4)

		#if  cat[2:] and (e.gen_match_4 == 5 or e.gen_match_3 == 5 ) and (e.decayMode_3 ==11 or e.decayMode_4==1): 
		#    print e.evt, 'varTID:', varTID,  'w:', weight, 'wTID:', weightTID, 'pT_3:', e.pt_3, e.gen_match_3, 'pt_4', e.pt_4, e.gen_match_4



                #if e.evt == 2496649 : print 'third', weight, weightTID

                weight *= weightTID
                weightFM *= weightTID * ww

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)
            #####
            #if not tight1 or not tight2 : hGroup = 'fakes'

            if printDebug:
	        if not tight1 or not tight2: print 'failed tight1 or tight2 cut', cat, e.lumi, e.run, e.evt, tight1, tight2
            if not tight1 or not tight2 : continue

            #print cat, hGroup, group, isSS, hw_fm_new
	    if not tight3 and tight4: hw_fm_new[hGroup][cat].Fill(1,fW1 )
	    if tight3 and not tight4 : hw_fm_new[hGroup][cat].Fill(2,fW2 )
	    if not tight3 and not tight4: hw_fm_new[hGroup][cat].Fill(3,fW0)
            #if group!='data' and group!='fakes' and group !='f1' and group !='f2' and (not tight1 or not tight2) : print weightFM , hGroup, cat, tight1, tight2, i, e.evt, nickName, fW1, fW2, fW0, e.gen_match_3, e.gen_match_4
           
            #print 'made thus far', leptons_sf
            #args.redoFit.lower() == 'yes'
	    #fastMTTmass, fastMTTtransverseMass = -1, -1
	    #if args.redoFit.lower() == 'yes' or args.redoFit.lower() == 'true' or systematic in jesSyst or 'scale_met' in systematic : 

	    fastMTTmass, fastMTTtransverseMass = runSVFit(e,tauV3uncor, tauV4uncor, MetV, cat[2:]) 

            #print fastMTTmass, 'old', e.m_sv, 'e.met', e.met, 'T1', met, cat
            #else  : fastMTTmass, fastMTTtransverseMass = e.m_sv, e.mt_sv
            #fastMTTmass, fastMTTtransverseMass = e.m_sv, e.mt_sv
            #if e.m_sv >50 and e.m_sv < 70 and cat=='eemt':    print 'new', fastMTTmass, 'old', e.m_sv, fastMTTtransverseMass, e.mt_sv, cat, cat[2:] , args.redoFit.lower() , 'met', met,  e.met, 'evt', e.evt, 'weight', weight, e.weightPUtrue ,' gen',  e.Generator_weight, 'pref', weight_pref
            #if e.evt ==2496649 : print 'met', met,  e.met, 'evt', e.evt, 'weight', weight, e.weightPUtrue ,' gen', e.Generator_weight, 'pref', weight_pref

            ZPt = (L1uncor+L2uncor).Pt()
            #mll = (L1uncor+L2uncor).M()
            #print cat, mll, e.mll
            #ZPtMC = (L1uncorMC+L2uncorMC).Pt()
            #ZPt = ZPtMC
	    ewkweight = 1.
	    ewkweightUp = 1.
	    ewkweightDown = 1.
            
            aweight, ratio_nlo_up, ratio_nlo_down = 1. ,1., 1.

	    #if  nickName == 'ZHToTauTau' : 
            if group == 'ZH' or group == 'HWW' :  
                ewkweight = EWK.getEWKWeight(ZPt, "central")
                ewkweightUp = EWK.getEWKWeight(ZPt, "up")
                ewkweightDown = EWK.getEWKWeight(ZPt, "down")
                #print cat, ZPt, ZPtMC

                aweight = 0.001*3*(26.66 * ewkweight +0.31+0.11)
                ratio_nlo_up = (26.66 * ewkweightUp +0.31+0.11)/(26.66 * ewkweight +0.31+0.11)
                ratio_nlo_down = (26.66 * ewkweightDown +0.31+0.11)/(26.66 * ewkweight +0.31+0.11)

                #print 'for signal---------------------->', nickName, ewkweight, ewkweightUp, ewkweightDown , aweight, ratio_nlo_up, ratio_nlo_down
                if 'nloewkup' not in systematic.lower() and 'nloewkdown' not in  systematic.lower(): 
                    #print 'for signal---------------------->', nickName, ewkweight, ewkweightUp, ewkweightDown , 'aweight', aweight, 'weight nom', weight, 'weightX0.7612', weight*0.7612, 'weight Xaweight', weight*aweight
                    weight *= aweight 
                if 'nloewkup' in systematic.lower() : 
                    weight *=aweight * ratio_nlo_up
                if 'nloewkdown' in systematic.lower() : 
                    weight *=aweight * ratio_nlo_down


	    for plotVar in plotSettings:
                #weight=1
		#print plotVar
		val = getattr(e, plotVar, None)
                #print val, plotVar
                #if plotVar =='metvs' and group!='data': 
                #    pl = '(metpt_nom - met)/metpt_nom'
		#    #val = getattr(e, e.metpt_nom - e.met, None)
                #    #print 'for metvs', pl, e.metpt_nom - e.met
                #    val = e.metpt_nom - e.met
                #if plotVar =='metvs' and group=='data': val = 0.

                #weight=1
		if val is not None: 
                    try: 
			if hGroup != 'data' : 
			    if hGroup !='fakes' and hGroup !='f1' and hGroup != 'f2' and hGroup !='Reducible': 
				hMC[hGroup][cat][plotVar].Fill(val,weight)

                                #if (isfakemc1 or isfakemc2) :
                                #    if not tight1 or not tight2 :   print '---------------->', group, hGroup, weight, ww, isfacemc1, isfakemc2, istight1, istight2

				if not isfakemc1 and not isfakemc2 and tight3 and tight4: 
                                    hMCFM[hGroup][cat][plotVar].Fill(val,weight)

			    if hGroup =='fakes' or hGroup =='f1' or hGroup == 'f2' or hGroup=='Reducible':  
                                hMCFM[hGroup][cat][plotVar].Fill(val,ww)
                                #print '---------------->', hMCFM[hGroup][cat][plotVar].GetName(), hGroup, ww

			else : 
			    if tight3 and tight4 : 
				hMC[hGroup][cat][plotVar].Fill(val,1)
				hMCFM[hGroup][cat][plotVar].Fill(val,1)

                    except KeyError : continue

            #custom made variables

            tauV = tauV3 + tauV4
	    #print fastMTTmass, 'm now==================', ZPt, cat

            #new_jA,jB,jC : hold the ZpT<75, 75<ZpT<150, ZpT>150
            # jBC is filled for ZpT >75

            if fastMTTmass >290 and printDebug : print 'failed fastMTT 290 value', cat, e.lumi, e.run, fastMTTmass

            if fastMTTmass <290 : 
		if hGroup != 'data' : 


                    if 'SSR' in hGroup  and 'data' not in group : weight *=-1

		    if 'ZH' in group or 'HWW' in group: 

                        if 'lowpt' in systematic : 
                            if (e.HTXS_Higgs_cat >= 400 and e.HTXS_Higgs_cat< 405) or (e.HTXS_Higgs_cat >= 500 and e.HTXS_Higgs_cat< 505) :
                                if 'Up' in systematic : weight *= e.LHEScaleWeights[8]
                                if 'Down' in systematic : weight *= e.LHEScaleWeights[0]

                        if 'highpt' in systematic : 
                            if (e.HTXS_Higgs_cat == 405) or (e.HTXS_Higgs_cat == 505 ) :
                                if 'Up' in systematic : weight *= e.LHEScaleWeights[8]
                                if 'Down' in systematic : weight *= e.LHEScaleWeights[0]


		    if hGroup !='fakes' and hGroup !='f1' and hGroup != 'f2' and hGroup !='Reducible' : 

                        if 'ZH' in group or ' HWW' in group : 

			    if 'lep_scaleDown' in systematic : weight *= e.LHEScaleWeights[0]
			    if 'lep_scaleUp' in systematic : weight *= e.LHEScaleWeights[8]

                           
			hm_sv_new[hGroup][cat].Fill(fastMTTmass,weight )
			hmt_sv_new[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			hH_LT[hGroup][cat].Fill(H_LT,weight )

                        
                        iBin = hm_sv_new[hGroup][cat].FindBin(fastMTTmass)

                        
                        #print 'filling first ', cat, group, e.HTXS_Higgs_cat, iBin, weight, fastMTTmass, ZPt, isfakemc1, isfakemc2, e.gen_match_3, e.gen_match_4, tight1, tight2
                        iBin-=1
			if ZPt>75 and ZPt < 150 : iBin += 7
			if ZPt>150 : iBin += 14


			if not isfakemc1 and not isfakemc2 and tight3 and tight4: 
			    ## qq->ZH 400
			    ## qq -> WH 300
			    ## gg->ZH 500
			    ## gg ->WH 
			    if group =='ZH' or group =='HWW' : 
				if e.HTXS_Higgs_cat == 400 : hm_sv_new_lep_FWDH_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 401 : hm_sv_new_lep_PTV_0_75_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 402 : hm_sv_new_lep_PTV_75_150_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 403 : hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 404 : hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 405 : hm_sv_new_lep_PTV_GT250_htt125[group][cat].Fill(iBin,weight )

			    if group =='ggZH' or group == 'ggHWW': 

                                print 'filling', cat, group, e.HTXS_Higgs_cat, iBin, weight, fastMTTmass, ZPt
				if e.HTXS_Higgs_cat == 500 : hm_sv_new_lep_FWDH_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 501 : hm_sv_new_lep_PTV_0_75_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 502 : hm_sv_new_lep_PTV_75_150_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 503 : hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 504 : hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 505 : hm_sv_new_lep_PTV_GT250_htt125[group][cat].Fill(iBin,weight )

			    if group =='WH' : 
				if e.HTXS_Higgs_cat == 300 : hm_sv_new_lep_FWDH_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 301 : hm_sv_new_lep_PTV_0_75_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 302 : hm_sv_new_lep_PTV_75_150_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 303 : hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 304 : hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].Fill(iBin,weight )
				if e.HTXS_Higgs_cat == 305 : hm_sv_new_lep_PTV_GT250_htt125[group][cat].Fill(iBin,weight )

			    #hm_sv_new_FMjall[group][cat].Fill(iBin,weight)
			    #print fastMTTmass, 'old', e.m_sv, 'e.met', e.met, 'T1', met, cat, weight
                            #print 'check again', tight1, tight2, weight, group, hGroup

			    if ZPt < 75 : 
				hm_sv_new_jA[hGroup][cat].Fill(fastMTTmass,weight )

			    if ZPt>75 and ZPt < 150 : 
				hm_sv_new_jB[hGroup][cat].Fill(fastMTTmass,weight )
				hm_sv_new_jBC[hGroup][cat].Fill(fastMTTmass,weight )
				       
			    #if ZPt>150 and ZPt < 250 : 
			    if ZPt>150 :
				hm_sv_new_jC[hGroup][cat].Fill(fastMTTmass,weight )
				hm_sv_new_jBC[hGroup][cat].Fill(fastMTTmass,weight )

			    if printOn : 
				print '{0:s} \t {1:d} \t  {2:d}  \t {3:d}  \t {4:.3f} \t {5:.3f} \t {6:.3f} \t {7:.3f} \t {8:.3f} \t {9:.3f} \t {10:.3f}'.format(cat, e.lumi, e.run, e.evt, e.pt_1, e.pt_2, e.pt_3, e.pt_4, MetV.Pt(),  e.mll, fastMTTmass), weight, systematic

			    hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,weight )
			    hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			    hH_LT_FM[hGroup][cat].Fill(H_LT,weight )

			    iBin =hm_sv_new_FM[hGroup][cat].FindBin(fastMTTmass)
                            iBin-=1

			    if ZPt>75 and ZPt < 150 : iBin += 7
			    if ZPt>150 : iBin += 14

                             
                            #print 'first check here', cat, tight1, tight2, weight, ww, group, hGroup
                            hm_sv_new_FMjall[hGroup][cat].Fill(iBin,weight)
                            #hm_sv_new_FMjall[hGroup][cat].SetBinContent(iBin,hm_sv_new_FMjall[hGroup][cat].GetBinContent(iBin)+weight)
                            #hm_sv_new_FMjall[hGroup][cat].SetBinError(iBin, sqrt(abs(hm_sv_new_FMjall[hGroup][cat].GetBinError(iBin)**2 + weight**2)))

			    if ZPt < 75 : 
				hm_sv_new_FMjA[hGroup][cat].Fill(fastMTTmass,weight )

			    if ZPt>75 and ZPt < 150 : 
				hm_sv_new_FMjB[hGroup][cat].Fill(fastMTTmass,weight )
				hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )
				       
			    if ZPt > 150 : 
				hm_sv_new_FMjC[hGroup][cat].Fill(fastMTTmass,weight )
				hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )

		    if hGroup =='fakes' or hGroup =='f1' or hGroup == 'f2' or 'Reducible' in hGroup :  

                        if isData :   weight = ww

                        #print 'check event', tight1, tight2, tight3, tight4, weight, fW1, fW2, fW0, group, hGroup

			hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,weight )
			hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,weight )
			hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			hH_LT_FM[hGroup][cat].Fill(H_LT,weight )


                        iBin =hm_sv_new_FM[hGroup][cat].FindBin(fastMTTmass)
                        iBin-=1


			if ZPt>75 and ZPt < 150 : iBin += 7
			if ZPt>150 : iBin += 14

                        hm_sv_new_FMjall[hGroup][cat].Fill(iBin,weight)


			if ZPt < 75 : 
			    hm_sv_new_FMjA[hGroup][cat].Fill(fastMTTmass,weight )

			if ZPt>75 and ZPt < 150 : 
			    hm_sv_new_FMjB[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )
				   
			if ZPt > 150 : 
			    hm_sv_new_FMjC[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )


		else :  ##this is data
		    if tight3 and tight4 :

			if printOn : 
			    print '{0:s} \t {1:d} \t  {2:d}  \t {3:d}  \t {4:.3f} \t {5:.3f} \t {6:.3f} \t {7:.3f} \t {8:.3f} \t {9:.3f} \t {10:.3f}'.format(cat, e.lumi, e.run, e.evt, e.pt_1, e.pt_2, e.pt_3, e.pt_4, MetV.Pt(),  e.mll, fastMTTmass)
			    #if 'data' not in nickName : print '{0:s} \t {1:d} \t  {2:d}  \t {3:d}  \t {4:.3f} \t {5:.3f} \t {6:.3f} \t {7:.3f} \t {8:.3f} \t {9:.3f} \t {10:.3f} \t {11:.3f} \t {12:.3f}  \t {13:.3f}  \t {14:.3f} \t {15:.3f} \t{16:.3f}'.format(cat, e.lumi, e.run, e.evt, e.pt_1, e.pt_2, e.pt_3, e.pt_4, MetV.Pt(), nbtag, btag_sf, e.weightPUtrue, e.Generator_weight,  e.L1PreFiringWeight_Nom, e.HTXS_Higgs_cat, e.mll, weight)
	     
			hmt_sv_new[hGroup][cat].Fill(fastMTTtransverseMass,1)
			hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,1)

			hH_LT[hGroup][cat].Fill(H_LT,1)
			hH_LT_FM[hGroup][cat].Fill(H_LT,1)

			hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,1)
			hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,1)
			hm_sv_new[hGroup][cat].Fill(fastMTTmass,1)

                        iBin = hm_sv_new[hGroup][cat].FindBin(fastMTTmass)
                        iBin-=1

                        #print 'initial iBin', cat, iBin, fastMTTmass, ZPt
			if ZPt>75 and ZPt < 150 : 
                            #print 'should go in the second ZPt', iBin, iBin+7
                            iBin += 7
			if ZPt>150 : iBin += 14
                        
                        #print cat, iBin, fastMTTmass, ZPt
                        #print ''
                        hm_sv_new_FMjall[hGroup][cat].Fill(iBin,1)
                        #hm_sv_new_FMjall[hGroup][cat].SetBinContent(iBin,hm_sv_new_FMjall[hGroup][cat].GetBinContent(iBin)+1)
                        #hm_sv_new_FMjall[hGroup][cat].SetBinError(iBin, sqrt(abs(hm_sv_new_FMjall[hGroup][cat].GetBinError(iBin)**2 + 1)))

                        #print 'data filling', cat, iBin, hm_sv_new_FMjall[hGroup][cat].GetBinContent(iBin)

			if ZPt < 75 : 
			    hm_sv_new_jA[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjA[hGroup][cat].Fill(fastMTTmass,1 )

			if ZPt>75 and ZPt < 150 : 
			    hm_sv_new_jB[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjB[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,1)
				   
			if ZPt> 150 : 
			    hm_sv_new_jC[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjC[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,1 )

	    nEvents += 1

        
	print("{0:30s} {1:7d} {2:10.6f} {3:5d}".format(nickName,nentries,sampleWeight[nickName],nEvents))
        
        inFile.Close()

htest={}


ffout='testFile.root'
print("Opening {0:s} as output.".format(ffout))
fOut = TFile( ffout, 'recreate' )

fOut.cd()
for group in ngroups:
    for icat, cat in cats.items()[0:8] :
        
	for i in range(len(hLabels)) : 
	    hCutFlowPerGroup[group][cat].GetXaxis().SetBinLabel(i+1, hLabels[i])
	    hCutFlowPerGroupFM[group][cat].GetXaxis().SetBinLabel(i+1, hLabels[i])

	for inick,nickName in enumerate(nickNames[group]) :
	    #for i in range(1, hCutFlowN[cat][nickName].GetNbinsX()) : 
		#hCutFlowN[cat][nickName].SetBinContent(i, WCounter[i-1][icat-1][inick])

		#if 'DY' in nickName : print 'content now', i, hCutFlowN[cat][nickName].GetBinContent(i), 'for cat and nickName', cat, nickName, hCutFlowPerGroup[group][cat].GetXaxis().GetBinLabel(i), 'weight is ', weight 
	        #for i in range(len(hLabels)) :

	    for i in range(len(hLabels)) : 
		hCutFlowN[cat][nickName].GetXaxis().SetBinLabel(i+1, hLabels[i])
		hCutFlowFM[cat][nickName].GetXaxis().SetBinLabel(i+1, hLabels[i])
		hCutFlowPerGroup[group][cat].GetXaxis().SetBinLabel(i+1, hLabels[i])
		hCutFlowPerGroupFM[group][cat].GetXaxis().SetBinLabel(i+1, hLabels[i])

            #if  'data' not in nickName: 
                #hCutFlowN[cat][nickName].Scale(weight)

	    hCutFlowPerGroup[group][cat].Add(hCutFlowN[cat][nickName])
	    hCutFlowPerGroupFM[group][cat].Add(hCutFlowFM[cat][nickName])

	    hCutFlowN[cat][nickName].Write()
	    hCutFlowFM[cat][nickName].Write()
	
	hCutFlowPerGroup[group][cat].Write()
	hCutFlowPerGroupFM[group][cat].Write()


        htest = TH1D("hCutFlowAllGroup_"+cat,"AllGroupCutFlow",20,-0.5,19.5)
        if 'data' not in group and not isSignal : htest.Add(hCutFlowPerGroup[group][cat])
        
        #for syst in varSystematics : 
	#OverFlow(hm_sv_new[group][cat])
	#OverFlow(hmt_sv_new[group][cat])
	#OverFlow(hm_sv_new_FM[group][cat])
	OverFlow(hm_sv_new_FMext[group][cat])
	#OverFlow(hmt_sv_new_FM[group][cat])
	hm_sv_new[group][cat].Write()
	hmt_sv_new[group][cat].Write()
	hm_sv_new_FM[group][cat].Write()
	hm_sv_new_FMext[group][cat].Write()
	hmt_sv_new_FM[group][cat].Write()


        OverFlow(hH_LT[group][cat])
        OverFlow(hH_LT_FM[group][cat])

	hw_fm_new[hGroup][cat].Write()
        hH_LT[group][cat].Write()
        hH_LT_FM[group][cat].Write()



	OverFlow(hm_sv_new_jA[group][cat])
	OverFlow(hm_sv_new_jB[group][cat])
	OverFlow(hm_sv_new_jC[group][cat])

	OverFlow(hm_sv_new_FMjA[group][cat])
	OverFlow(hm_sv_new_FMjB[group][cat])
	OverFlow(hm_sv_new_FMjC[group][cat])
        

        hm_sv_new_jA[group][cat].Write()
        hm_sv_new_jB[group][cat].Write()
        hm_sv_new_jC[group][cat].Write()


 


        #hm_sv_new_FMjall : holds all of the ZpT  and has 21 bins
        #hm_sv_new_FMjallv2 : holds all of the ZpT  has 21 bins and joint B+C regions
        for i in range(1,hm_sv_new_FM[group][cat].GetNbinsX()+1) :
            '''
            hm_sv_new_FMjall[group][cat].SetBinContent(i,hm_sv_new_FMjA[group][cat].GetBinContent(i))
            hm_sv_new_FMjall[group][cat].SetBinContent(i+7,hm_sv_new_FMjB[group][cat].GetBinContent(i))
            hm_sv_new_FMjall[group][cat].SetBinContent(i+14,hm_sv_new_FMjC[group][cat].GetBinContent(i))

            hm_sv_new_FMjall[group][cat].SetBinError(i,hm_sv_new_FMjA[group][cat].GetBinError(i))
            hm_sv_new_FMjall[group][cat].SetBinError(i+7,hm_sv_new_FMjB[group][cat].GetBinError(i))
            hm_sv_new_FMjall[group][cat].SetBinError(i+14,hm_sv_new_FMjC[group][cat].GetBinError(i))
            '''
            #if group == 'Reducible' :
            #    print 'bin', i, hm_sv_new_FMjA[group][cat].GetBinContent(i), hm_sv_new_FMjA[group][cat].GetBinError(i), hm_sv_new_FMjA[group][cat].GetSumOfWeights(), hm_sv_new_FMjA[group][cat].GetSum(), hm_sv_new_FMjA[group][cat].GetEntries(), cat

            hm_sv_new_FMjallv2[group][cat].SetBinContent(i,hm_sv_new_FMjA[group][cat].GetBinContent(i))
            hm_sv_new_FMjallv2[group][cat].SetBinContent(i+7,hm_sv_new_FMjB[group][cat].GetBinContent(i))
            xx = hm_sv_new_FMjallv2[group][cat].GetBinContent(i+14)
            hm_sv_new_FMjallv2[group][cat].SetBinContent(i+7, xx+hm_sv_new_FMjC[group][cat].GetBinContent(i))

            hm_sv_new_FMjallv2[group][cat].SetBinError(i,hm_sv_new_FMjA[group][cat].GetBinError(i))
            hm_sv_new_FMjallv2[group][cat].SetBinError(i+7,sqrt(hm_sv_new_FMjB[group][cat].GetBinError(i)*hm_sv_new_FMjB[group][cat].GetBinError(i) + hm_sv_new_FMjC[group][cat].GetBinError(i)*hm_sv_new_FMjC[group][cat].GetBinError(i) ))



        hm_sv_new_FMjall[group][cat].Write()
        hm_sv_new_FMjallv2[group][cat].Write()

        hm_sv_new_FMjA[group][cat].Write()
        hm_sv_new_FMjB[group][cat].Write()
        hm_sv_new_FMjC[group][cat].Write()
        hm_sv_new_FMjBC[group][cat].Write()


	hm_sv_new_lep_FWDH_htt125[group][cat].Write()
	hm_sv_new_lep_PTV_0_75_htt125[group][cat].Write()
	hm_sv_new_lep_PTV_75_150_htt125[group][cat].Write()
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].Write()
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].Write()
	hm_sv_new_lep_PTV_GT250_htt125[group][cat].Write()

        for plotVar in plotSettings:
            OverFlow(hMC[group][cat][plotVar])
	    #if 'gen_match' not in plotVar and 'CutFlow' not in plotVar and 'iso' not in plotVar: 
            #    hMC[group][cat][plotVar].Rebin(2)
            #    hMCFM[group][cat][plotVar].Rebin(2)
            hMC[group][cat][plotVar].Write()
            OverFlow(hMCFM[group][cat][plotVar])
            hMCFM[group][cat][plotVar].Write()
    htest.Write()

fOut.Close()
for cat in cats.values():
    print("Duplicate summary for {0:s}".format(cat))
    DD[cat].printSummary()
    


