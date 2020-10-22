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
import fakeFactor 
import EWKWeights


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

def runSVFit(entry,tau1, tau2,  METV, channel) :
		  
    measuredMETx = METV.Pt()*cos(METV.Phi())
    measuredMETy = METV.Pt()*sin(METV.Phi())

    #define MET covariance
    covMET = TMatrixD(2,2)
    covMET[0][0] = entry.metcov00
    covMET[1][0] = entry.metcov10
    covMET[0][1] = entry.metcov01
    covMET[1][1] = entry.metcov11


    #self.kUndefinedDecayType, self.kTauToHadDecay,  self.kTauToElecDecay, self.kTauToMuDecay = 0, 1, 2, 3
    if channel == 'et' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToElecDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.000511) 
    elif channel == 'mt' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToMuDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.106) 
    elif channel == 'tt' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToHadDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), tau1.M())
		    
    if channel != 'em' :
	measTau2 = ROOT.MeasuredTauLepton(kTauToHadDecay, tau2.Pt(), tau2.Eta(), tau2.Phi(), tau2.M())

    if channel == 'em' :
	measTau1 = ROOT.MeasuredTauLepton(kTauToElecDecay,  tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.000511)
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
    parser.add_argument("-b", "--bruteworkingPoint",type=int, default=16, help="make working point for fakes 16 (M), 32(T), 64(VT), 128(VVT)")
    parser.add_argument("-j", "--inSystematics",type=str, default='',help='systematic variation')
    parser.add_argument("-e", "--extraTag",type=str, default='',help='extra tag; wL, noL wrt to fakes method')
    parser.add_argument("-g", "--genTag",type=str, default='v4',help='which fakesFactor scheme will be used')
    parser.add_argument("-i", "--isLocal",type=str, default=0,help='local or condor')
    parser.add_argument("-t", "--gType",type=str, default='',help='type : data, Signal, Other')
    
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

def PtoEta( Px,  Py,  Pz) :

   P = sqrt(Px*Px+Py*Py+Pz*Pz);
   if P> 0 : 
       cosQ = Pz/P;
       Q = acos(cosQ);
       Eta = - log(tan(0.5*Q));
       return Eta
   else: return -99

def PtoPhi( Px,  Py) : return atan2(Py,Px)


def PtoPt( Px,  Py) : return sqrt(Px*Px+Py*Py)


def dPhiFrom2P( Px1,  Py1, Px2,  Py2) :
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

def deltaEta(Px1, Py1, Pz1, Px2,  Py2,  Pz2):

  eta1 = PtoEta(Px1,Py1,Pz1)
  eta2 = PtoEta(Px2,Py2,Pz2)

  dEta = eta1 - eta2

  return dEta


def getFakeWeightsvspTvsDM(ic, pt1,pt2, WP, DM1, DM2,syst) :
    if ic == 'et' : 
        p1 = 'e_e'
        p2 = 't_et'

    if ic == 'mt' : 
        p1 = 'm_m'
        p2 = 't_mt'

    if ic == 'em' : 
        p1 = 'e_e'
        p2 = 'm_m'

    if ic == 'tt' : 
        p1 = 't1_tt'
        p2 = 't2_tt'

    #print 'the name will be', '{0:s}_{1:s}DM_vspT'.format(p1,str(DM1)), '{0:s}_{1:s}DM_vspT'.format(p2,str(DM2))
    filein = './FakesResult_{0:s}_SS_{1:s}WP_sys{2:s}.root'.format(str(args.year),str(WP),syst)
    #print 'filein------------------------->', filein
    fin = TFile.Open(filein,"READ")         
    h1 = fin.Get('{0:s}_vspT'.format(p1))
    h2 = fin.Get('{0:s}_vspT'.format(p2))

    if ic == 'et'or ic =='mt' : 
	h1 = fin.Get('{0:s}_vspT'.format(p1))
	h2 = fin.Get('{0:s}_DM{1:s}_vspT'.format(p2,str(DM2)))

    if ic == 'tt': 
	h1 = fin.Get('{0:s}_DM{1:s}_vspT'.format(p1,str(DM1)))
	h2 = fin.Get('{0:s}_DM{1:s}_vspT'.format(p2,str(DM2)))


    xB1 = 1
    xB2 = 1
    if pt1 < 100 : xB1 = h1.FindBin(pt1)
    if pt1 > 100 : xB1 = h1.GetNbinsX()

    if pt2 < 100 : xB2 = h2.FindBin(pt2)
    if pt2 > 100 : xB2 = h2.GetNbinsX()

    f1 = h1.GetBinContent(xB1)
    f2 = h1.GetBinContent(xB2)
    #print '===========>', pt1, pt2, f1, f2, xB1, xB2
    w1, w2, w0 =0. ,0. ,0.
    w1 = float(f1/(1.-f1))
    w2 = float(f2/(1.-f2))
    w0 = w1*w2
    #print '================= now reading fake rate for data', pt1, pt2 ,' to be', f1, f2, 'actual fW1 etc', w1, w2, w0, 'is this false??? ', ist1, ist2
    return w1, w2, w0


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
kUndefinedDecayType, kTauToHadDecay,  kTauToElecDecay, kTauToMuDecay = 0, 1, 2, 3   

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

otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered'] 
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
#systematic='jerUp'


if str(args.gType) !='data' :

    gInterpreter.ProcessLine('.L BTagCalibrationStandalone.cpp+') 
    calib = ROOT.BTagCalibration('csvv1', 'DeepCSV_{0:s}.csv'.format(era))
    # making a std::vector<std::string>> in python is a bit awkward, 
    # but works with root (needed to load other sys types):
    v_sys = getattr(ROOT, 'vector<string>')()
    #v_sys.push_back('up')
    #v_sys.push_back('down')



    # make a reader instance and load the sf data
    reader_b = ROOT.BTagCalibrationReader(
	3,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
	"central",      # central systematic type
	v_sys,          # vector of other sys. types
    )    


    reader_b.load(
	calib, 
	0,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
	"iterativefit"      # measurement type
    )

    reader_c = ROOT.BTagCalibrationReader(
	3,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
	"central",      # central systematic type
	v_sys,          # vector of other sys. types
    )    


    reader_c.load(
	calib, 
	1,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
	"iterativefit"      # measurement type
    )

    reader_light = ROOT.BTagCalibrationReader(
	3,              # 0 is for loose op, 1: medium, 2: tight, 3: discr. reshaping
	"central",      # central systematic type
	v_sys,          # vector of other sys. types
    )    


    reader_light.load(
	calib, 
	2,          # 0 is for b flavour, 1: FLAV_C, 2: FLAV_UDSG 
	"iterativefit"      # measurement type
    )



tt_tau_vse = 4
tt_tau_vsmu = 1

et_tau_vse = 32
et_tau_vsmu = 1

mt_tau_vse = 4
mt_tau_vsmu = 8



if era == '2016' : 
    weights = {'lumi':35.92, 'tauID_w' :0.87, 'tauES_DM0' : -0.6, 'tauES_DM1' : -0.5,'tauES_DM10' : 0.0, 'mutauES_DM0' : -0.2, 'mutauES_DM1' : 1.5, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 9.5}

    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_2016Legacy.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2016.root'}


if era == '2017' : 
    weights = {'lumi':41.53, 'tauID_w' :0.89, 'tauES_DM0' : 0.7, 'tauES_DM1' : -0.2,'tauES_DM10' : 0.1, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.3, 'eltauES_DM1' : 3.6}


    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_2017ReReco.root'}
    WorkSpace={'dir' : './', 'fileWS' : 'htt_scalefactors_legacy_2017.root'}

if era == '2018' : 
    weights = {'lumi':59.74, 'tauID_w' :0.90, 'tauES_DM0' : -1.3, 'tauES_DM1' : -0.5,'tauES_DM10' : -1.2, 'mutauES_DM0' : 0.0, 'mutauES_DM1' : 0.0, 'eltauES_DM0' : 0.0, 'eltauES_DM1' : 0.0}


    TESSF={'dir' : 'TauPOG/TauIDSFs/data/', 'fileTES' : 'TauES_dm_2018ReReco.root'}
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
hm_sv_new_jall = {}
hm_sv_new_FMjallv2 = {}
hm_sv_new_jall={}

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
tauV = TLorentzVector()
L1 = TLorentzVector()
L2 = TLorentzVector()
L1.SetXYZM(0,0,0,0)
L2.SetXYZM(0,0,0,0)
'''
L1g = TLorentzVector()
L2g = TLorentzVector()
L1g.SetXYZM(0,0,0,0)
L2g.SetXYZM(0,0,0,0)
'''
MetV.SetXYZM(0,0,0,0)
tauV3.SetXYZM(0,0,0,0)
tauV4.SetXYZM(0,0,0,0)
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



if 'data' in str(args.gType) : 
    groups = ['Reducible','fakes','f1', 'f2','data']
    ngroups = ['Reducible','fakes','f1', 'f2','data']

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
    elif '+' in vals[2] : 
        value1, value2 = map(float, vals[2].split("+"))
        xsec[nickName] = float(value1+value2)
    else : xsec[nickName] = float(str(vals[2]))


    if nickName == 'ZHToTauTau' : 
        xsec[nickName] = float(0.0627)

    #totalWeight[nickName] = float(vals[4])
    if islocal :    filein = '../MC/condor/{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
    else : filein = '{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
    if 'data' not in filein : 
	fIn = TFile.Open(filein,"READ")
	#totalWeight[nickName] = float(fIn.Get("hWeights").GetSumOfWeights())

        if '+' in vals[4] : 
	    value1, value2 = map(float, vals[4].split("+"))
	    totalWeight[nickName] = float(value1+value2)
	else : totalWeight[nickName] = float(vals[4])

        if nickName == 'ZHToTauTau' : totalWeight[nickName] *= float(3*0.033658)
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
if args.workingPoint == args.bruteworkingPoint : WPSR = WP
outFileName = outFileName +"_"+str(args.bruteworkingPoint)+"brute_"+str(args.inSystematics)

if 'data' in str(args.gType) :
    FF = fakeFactor.fakeFactor(args.year,WP,extratag, vertag,systematic)

if 'ZH'  in str(args.gType) :
    EWK = EWKWeights.EWKWeights()



plotSettings = { # [nBins,xMin,xMax,units]
        "m_sv":[20,0,400,"[Gev]","m(#tau#tau)(SV)"]}

wpp = 'Medium'
if str(args.bruteworkingPoint=='16') : wpp = 'Medium'
if str(args.bruteworkingPoint=='32') : wpp = 'Tight'
if str(args.bruteworkingPoint=='64') : wpp = 'VTight'
if str(args.bruteworkingPoint=='128') : wpp = 'VVTight'

tauSFTool = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSjet',wpp)
testool = TauESTool(campaign[args.year],'DeepTau2017v2p1VSjet', TESSF['dir'])
festool = TauESTool(campaign[args.year],'DeepTau2017v2p1VSjet')

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

    if 'ZH' in group or 'WH' in group  : isSignal = True
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


    hm_sv_new_jall[group]={}

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
	hm_sv_new_jall[group][cat] = {}

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
	hm_sv_new[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
        print '===================================================================', nbins, Bins
	hm_sv_new[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM'.format(group,cat)
	hm_sv_new_FM[group][cat] = TH1D(hName, hName,  nbins, array('d',Bins))
	hm_sv_new_FM[group][cat].SetDefaultSumw2()
        #print 'take this example', hm_sv_new[group][cat].GetName(), 

	hName = 'h{0:s}_{1:s}_m_sv_new_FMext'.format(group,cat)
	hm_sv_new_FMext[group][cat] = TH1D(hName, hName, 20,0,400)  
	hm_sv_new_FMext[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_jA'.format(group,cat)
	hm_sv_new_jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_jB'.format(group,cat)
	hm_sv_new_jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_jC'.format(group,cat)
	hm_sv_new_jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_jC[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_jBC'.format(group,cat)
	hm_sv_new_jBC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_jBC[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_m_sv_new_FMjA'.format(group,cat)
	hm_sv_new_FMjA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjB'.format(group,cat)
	hm_sv_new_FMjB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjC'.format(group,cat)
	hm_sv_new_FMjC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjC[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_FMjBC'.format(group,cat)
	hm_sv_new_FMjBC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjBC[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_m_sv_new_FMjall'.format(group,cat)
	hm_sv_new_FMjall[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_FMjall[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_FMjall[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_FMjallv2'.format(group,cat)
	hm_sv_new_FMjallv2[group][cat] = TH1D(hName ,hName, 14,0,14)
	hm_sv_new_FMjallv2[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_jall'.format(group,cat)
	hm_sv_new_jall[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_jall[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_mt_sv_new'.format(group,cat)
	hmt_sv_new[group][cat] = TH1D(hName, hName,  nbins, array('d',Bins))
	hmt_sv_new[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_mt_sv_new_FM'.format(group,cat)
	hmt_sv_new_FM[group][cat] = TH1D(hName,hName,  nbins, array('d',Bins))
	hmt_sv_new_FM[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_lep_FWDH_htt125'.format(group,cat)
	hm_sv_new_lep_FWDH_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_FWDH_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_FWDH_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_0_75_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_0_75_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_0_75_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_0_75_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_75_150_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_75_150_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_75_150_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_75_150_htt125[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_lep_PTV_150_250_0J_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_150_250_GE1J_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
	hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_lep_PTV_GT250_htt125'.format(group,cat)
	hm_sv_new_lep_PTV_GT250_htt125[group][cat] = TH1D(hName ,hName, 21,0,21)
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
            if 'GeV' in units : hMCFM[group][cat][plotVar].GetYaxis().SetTitle("Events / "+str(binwidth)+" {0:s}".format(units))
            if 'GeV' not in units : hMCFM[group][cat][plotVar].GetYaxis().SetTitle("Events / "+str(binwidth))

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

        for i, e in enumerate(inTree) :

            inTree.GetEntry(i)
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
            isfakemc1 = False
            isfakemc2 = False
        
	    #if ('ZZTo4' in inFileName or 'ZH' in inFileName) and  i > 2000 : continue
	    #if hGroup != 'data' and i > 1000:continue
            if i % 5000 ==0: print i, 'from ', nentries
            #if i > 10000 : break
            try : 
                met = e.met
                metphi = e.metphi
		#met = getattr(e, 'MET_T1Smear_pt', None)
		#metphi = getattr(e, 'MET_T1Smear_phi', None)

		njets = getattr(e, 'njets_nom', None)
		jpt = getattr(e, 'jpt_nom', None)
		jeta = getattr(e, 'jeta_nom', None)
		jflavour = getattr(e, 'jflavour_nom', None)
		nbtag = getattr(e, 'nbtag_nom', None)

            except AttributeError :
                met = e.met
                metphi = e.metphi
                njets = e.njets
                jpt = e.jpt
                jeta = e.jeta
                jflavour = e.jflavour
                nbtag = e.nbtag

            if 'scale_met_unclusteredUp' in systematic : 
                met  = e.MET_pt_UnclUp
                metphi  = e.MET_phi_UnclUp
            if 'scale_met_unclusteredDown' in systematic : 
                met  = e.MET_pt_UnclDown
                metphi  = e.MET_phi_UnclDown
            #print 'compare', met, e.metNoTauES, njets, e.njets, 'jpt', jpt[0], e.jpt[0]


            #if e.isTrig_1 == 0 and e.isDoubleTrig==0 : continue  
            if e.isTrig_1 == 0 : continue  
	    if e.q_1*e.q_2 > 0 : continue
            if args.sign == 'SS':
               if e.q_3*e.q_4 < 0. : continue
            else :
                if e.q_3*e.q_4 > 0. : continue

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

		weight = e.weightPUtrue * e.Generator_weight *sWeight * weight_pref
		weightFM = e.weightPUtrue * e.Generator_weight *sWeight * weight_pref

            weightCF = weight
            if i == 1 : print 'sample info ', e.weightPUtrue, e.Generator_weight, sWeight, 'for ', group, nickName, inTree.GetEntries()

            #weight=1.

            #####sign
            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)


            ##############good ISO


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
	        if e.Electron_mvaFall17V2noIso_WP90_3 < 1 or e.iso_3 > el_iso  : tight1 = False

                if e.isGlobal_4 < 1 and e.isTracker_4 < 1  : continue
                if e.iso_4 > mu_iso : tight2 = False
                if e.mediumId_4  <1 : tight2 = False
                if abs(e.eta_4) > mu_eta : tight2 = False


		#if nickName == 'ZHToTauTau' and (e.evt % 100 == 0) :
		#    print("Event={0:8d} em iso_3={1:.3f} iso_4={2:.3f} WP90={3}".format(e.evt,e.iso_3,e.iso_4, e.Electron_mvaFall17V2noIso_WP90_3))

	    if cat[2:] == 'mt':
                if e.isGlobal_3 < 1 and e.isTracker_3 < 1 : continue
                if e.iso_3 > mu_iso  : tight1 = False
                if e.mediumId_3  <1 : tight1 = False
                if abs(e.eta_3) > mu_eta : tight1 = False

	    if (cat[2:] == 'et') :
                if  e.Electron_mvaFall17V2noIso_WP90_3 < 1 or e.iso_3 > el_iso : tight1 = False
                if abs(e.eta_3) > el_eta : tight1 = False

            
            ###############################################
            #               VSjet    VSmu     VSel
            # et           M (16)   VL (1)   T (32)
            # mt           M (16)   T (8)    VL (4)
            # tt           M (16)   VL (1)   VL (4)
            #
            # Tau_idDeepTau2017v2p1VSe	UChar_t	byDeepTau2017v2p1VSe  (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
            #Tau_idDeepTau2017v2p1VSjet	UChar_t	byDeepTau2017v2p1VSjet (deepTau2017v2p1): bitmask 1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
            #Tau_idDeepTau2017v2p1VSmu	UChar_t	byDeepTau2017v2p1VSmu  (deepTau2017v2p1): bitmask 1 = VLoose, 2 = Loose, 4 = Medium, 8 = Tight

	    if cat[2:] == 'tt' :
                    tight1 = e.idDeepTau2017v2p1VSjet_3 >=  WPSR and e.idDeepTau2017v2p1VSmu_3 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_3 >= tt_tau_vse
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >=  WPSR and e.idDeepTau2017v2p1VSmu_4 >= tt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= tt_tau_vse 

	    if cat[2:] == 'mt' : tight2 = e.idDeepTau2017v2p1VSjet_4 >=  WPSR and e.idDeepTau2017v2p1VSmu_4 >= mt_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= mt_tau_vse
	    if cat[2:] == 'et' : tight2  = e.idDeepTau2017v2p1VSjet_4 >= WPSR and e.idDeepTau2017v2p1VSmu_4 >= et_tau_vsmu and  e.idDeepTau2017v2p1VSe_4 >= et_tau_vse

            '''
	    if cat[2:] == 'tt' :
                    tight1 = e.idDeepTau2017v2p1VSjet_3 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_3 > 0 and  e.idDeepTau2017v2p1VSe_3 > 3
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_4 > 0 and  e.idDeepTau2017v2p1VSe_4 > 3 
                    #print  e.idDeepTau2017v2p1VSjet_3 & 16,  e.idDeepTau2017v2p1VSjet_3 & 8 , e.idDeepTau2017v2p1VSjet_3 & 64
	    if cat[2:] == 'mt' : tight2 = e.idDeepTau2017v2p1VSjet_4 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_4 > 7 and  e.idDeepTau2017v2p1VSe_4 > 3
	    if cat[2:] == 'et' : tight2  = e.idDeepTau2017v2p1VSjet_4 > WPSR-1 and e.idDeepTau2017v2p1VSmu_4 > 0 and  e.idDeepTau2017v2p1VSe_4 > 31
            '''


            
            if group != 'data' :
                if not tight1 or not tight2 : continue

            if not dataDriven and (not tight1 or not tight2) : continue


            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)


            ########H_LT
            '''
            #if H_LT < args.LTcut : continue

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)
            '''
            ######### nbtag
	    #if e.mll > 100 or e.mll<80: continue
	    #try :
	    if nbtag > 0 : continue
	    #except TypeError :
	    #	if e.nbtag > 0 : continue

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

            ########### Trigger
            ################### Trigger SF
            
       
            if group == 'data' :
                if DD[cat].checkEvent(e,cat) : continue 
            btag=1

            if systematic in jesSyst and group != 'data' :  
		met = getattr(e, 'MET_T1_pt_{0:s}'.format(systematic), None)
		metphi = getattr(e, 'MET_T1_phi_{0:s}'.format(systematic), None)
		njets = getattr(e, 'njets_{0:s}'.format(systematic), None)
		jpt = getattr(e, 'jpt_{0:s}'.format(systematic), None)
		jeta = getattr(e, 'jeta_{0:s}'.format(systematic), None)
		jflavour = getattr(e, 'jflavour_{0:s}'.format(systematic), None)
		nbtag = getattr(e, 'nbtag_{0:s}'.format(systematic), None)


            ##### btag
            if group != 'data' :
		nj= njets
		if nj > 0 :
		    #for ib in range(0, int(nj)) :
                    #    print nj, ib, e.jeta[ib], e.jpt[ib], i, cat

		    for ib in range(0, int(nj)) :
                        try : 
			    flv = 0
			    if abs(jflavour[ib]) == 5 : 
				btag_sf *= reader_b.eval_auto_bounds( 'central',  0,     abs(jeta[ib]), jpt[ib])
			    if abs(jflavour[ib]) == 4 : 
				btag_sf *= reader_c.eval_auto_bounds( 'central',  1,     abs(jeta[ib]), jpt[ib])
			    if abs(jflavour[ib]) < 4 or abs(jflavour[ib]) == 21 :
				btag_sf *= reader_light.eval_auto_bounds( 'central',  2,     abs(jeta[ib]), jpt[ib])
                        except IndexError : btag_sf = 1.
		weight *= btag_sf
	   	weightFM *= btag_sf

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)



            trigw=1
            trigw1=1
            trigw2=1
            tracking_sf = 1.
            lepton_sf = 1.

            if group != 'data' :
		if cat[:2] == 'mm' :      
		    trigw = 1.
		    
		    if e.isTrig_1==1 : 
			wspace.var("m_pt").setVal(e.pt_1)
			wspace.var("m_eta").setVal(e.eta_1)
			trigw *=  wspace.function("m_trg_ic_ratio").getVal()

		    if e.isTrig_1==-1 : 
			wspace.var("m_pt").setVal(e.pt_2)
			wspace.var("m_eta").setVal(e.eta_2)
			trigw *=  wspace.function("m_trg_ic_ratio").getVal()

		    if  e.isTrig_1==2 : 
			wspace.var("m_pt").setVal(e.pt_1)
			wspace.var("m_eta").setVal(e.eta_1)
			trigw1 =  wspace.function("m_trg_ic_ratio").getVal()

			wspace.var("m_pt").setVal(e.pt_2)
			wspace.var("m_eta").setVal(e.eta_2)
			trigw2 =  wspace.function("m_trg_ic_ratio").getVal()

			trigw = float( 1-(1-trigw1) * (1-trigw2))

		    wspace.var("m_pt").setVal(e.pt_1)
		    wspace.var("m_eta").setVal(e.eta_1)
		    lepton_sf = wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf = wspace.function("m_trk_ratio").getVal()
		    wspace.var("m_pt").setVal(e.pt_2)
		    wspace.var("m_eta").setVal(e.eta_2)
		    lepton_sf *= wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("m_trk_ratio").getVal()


		if cat[:2] == 'ee' :      
		    trigw = 1.
		    
		    if e.isTrig_1==1 : 
			wspace.var("e_pt").setVal(e.pt_1)
			wspace.var("e_eta").setVal(e.eta_1)
			trigw *=  wspace.function("e_trg_ic_ratio").getVal()

		    if e.isTrig_1==-1 : 
			wspace.var("e_pt").setVal(e.pt_2)
			wspace.var("e_eta").setVal(e.eta_2)
			trigw *=  wspace.function("e_trg_ic_ratio").getVal()

		    if e.isTrig_1==2 : 
			wspace.var("e_pt").setVal(e.pt_1)
			wspace.var("e_eta").setVal(e.eta_1)
			trigw1 =  wspace.function("e_trg_ic_ratio").getVal()

			wspace.var("e_pt").setVal(e.pt_2)
			wspace.var("e_eta").setVal(e.eta_2)
			trigw2 =  wspace.function("e_trg_ic_ratio").getVal()

			trigw = float( 1-(1-trigw1) * (1-trigw2))

		    wspace.var("e_pt").setVal(e.pt_1)
		    wspace.var("e_eta").setVal(e.eta_1)
		    lepton_sf = wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf = wspace.function("e_trk_ratio").getVal()
		    wspace.var("e_pt").setVal(e.pt_2)
		    wspace.var("e_eta").setVal(e.eta_2)
		    lepton_sf *= wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("e_trk_ratio").getVal()

		if cat[2:] =='et' : 
		    wspace.var("e_pt").setVal(e.pt_3)
		    wspace.var("e_eta").setVal(e.eta_3)
		    lepton_sf *= wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("e_trk_ratio").getVal()

		if cat[2:] =='mt' : 
		    wspace.var("m_pt").setVal(e.pt_3)
		    wspace.var("m_eta").setVal(e.eta_3)
		    lepton_sf *= wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("m_trk_ratio").getVal()

		if cat[2:] =='et' or cat[2:] =='mt' or cat[2:] =='tt': 
		    wspace.var("t_pt").setVal(e.pt_4)
		    wspace.var("t_eta").setVal(e.eta_4)

		if cat[2:] =='em' : 
		    wspace.var("e_pt").setVal(e.pt_3)
		    wspace.var("e_eta").setVal(e.eta_3)
		    lepton_sf *= wspace.function("e_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("e_trk_ratio").getVal()
		    wspace.var("m_pt").setVal(e.pt_4)
		    wspace.var("m_eta").setVal(e.eta_4)
		    lepton_sf *= wspace.function("m_idiso_ic_ratio").getVal()
		    tracking_sf *= wspace.function("m_trk_ratio").getVal()


		#if e.isDoubleTrig!=0 and e.isTrig_1 == 0 : trigw = 1
		weight *= trigw 
		weightFM *= trigw 
           


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
		    if not tight1 and tight2 : 
                        ww = fW1          
                        hGroup = 'f1'
                        hGroup = 'Reducible'
                        #print 'found redu', ww, hGroup, tight1
		    elif tight1 and not tight2 : 
                        ww = fW2
                        hGroup = 'f2'
                        hGroup = 'Reducible'
		    elif not (tight1 or tight2) : 
                        ww = -fW0
                        hGroup = 'fakes'
                        hGroup = 'Reducible'
		    else :
			hGroup = 'data'
		else :
		    hGroup = 'data'
		    #print("group = data  cat={0:s} tight1={1} tight2={2} ww={3:f}".format(cat,tight1,tight2,ww))
		    if not (tight1 and tight2) : continue 
	
            '''
	    else : 
		#print("Good MC event: group={0:s} nickName={1:s} cat={2:s} gen_match_1={3:d} gen_match_2={4:d}".format(
		#    group,nickName,cat,e.gen_match_1,e.gen_match_2))
		if dataDriven :   # include only events with MC matching
		    if cat[2:] == 'em'  :
			if e.gen_match_3 != 15 and 'noL' in extratag : isfakemc1 = True
			if e.gen_match_3 != 15 and e.gen_match_3 !=1 and 'wL' in extratag : isfakemc1 = True
			if  e.gen_match_3 == 0 : hGroup = 'jfl1'
			if  e.gen_match_3 == 1 : hGroup = 'lfl1'
			if  e.gen_match_3 == 3 : hGroup = 'ljfl1'
			if  e.gen_match_3 == 4 : hGroup = 'cfl1'
			if  e.gen_match_3 == 5 : hGroup = 'bfl1'
			if  e.gen_match_3 == 22 : hGroup = 'gfl1'

			if e.gen_match_4 != 15  and 'noL' in extratag: isfakemc2 = True
			if not e.gen_match_4 != 15 and e.gen_match_4 !=1  and 'wL' in extratag: isfakemc2 = True
			if  e.gen_match_4 == 0 : hGroup = 'jfl2'
			if  e.gen_match_3 == 1 : hGroup = 'lfl2'
			if  e.gen_match_4 == 3 : hGroup = 'ljfl2'
			if  e.gen_match_4 == 4 : hGroup = 'cfl2'
			if  e.gen_match_4 == 5 : hGroup = 'bfl2'
			
		    if cat[2:] == 'et' or cat[2:] == 'mt' :
			if e.gen_match_3 != 15  and 'noL' in extratag: isfakemc1 = True
			if e.gen_match_3 != 15 and e.gen_match_3 !=1  and 'wL' in extratag: isfakemc1 = True

			if  e.gen_match_3 == 0 : hGroup = 'jfl1'
			if  e.gen_match_3 == 1 : hGroup = 'lfl1'
			if  e.gen_match_3 == 3 : hGroup = 'ljfl1'
			if  e.gen_match_3 == 4 : hGroup = 'cfl1'
			if  e.gen_match_3 == 5 : hGroup = 'bfl1'
			if  e.gen_match_3 == 22 : hGroup = 'gfl1'

			if e.gen_match_4 == 0  :
                            isfakemc2 = True
                            hGroup = 'jft2'

			
		    if cat[2:] == 'tt' :
			if e.gen_match_3 == 0  :
                            isfakemc1 = True
                            hGroup = 'jft1'
			if e.gen_match_4 == 0  :
                            isfakemc2 = True
                            hGroup = 'jft2'
            '''
		    
            weightFM=ww
           
            #if group != 'data' and group!='Signal' :
            #    if not isfakemc1 or not isfakemc2  : continue

            ########### tauID
            tauV3.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
            tauV4.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)


	    MetV.SetPx(met * cos (metphi))
	    MetV.SetPy(met * sin (metphi))
	    met_x = met * cos(metphi)
	    met_y = met * sin(metphi)
	    metcor = met


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
            if group != 'data' and (cat[2:] == 'et' or cat[2:]  == 'mt' or cat[2:]  == 'tt') :

                var=''
                if 'tauid' in systematic and 'Up' in systematic : var='Up'
                if 'tauid' in systematic and 'Down' in systematic : var='Down'

                tau3pt20, tau3pt25, tau3pt30, tau3pt35,  tau3pthigh = False, False, False, False, False
		if 'pt20to25' in systematic and  e.pt_3 > 20 and  e.pt_3 < 25 : tau3pt20 = True
		if 'pt25to30' in systematic and  e.pt_3 > 25 and  e.pt_3 < 30 : tau3pt25 = True
		if 'pt30to35' in systematic and  e.pt_3 > 30 and  e.pt_3 < 35 : tau3pt30 = True
		if 'pt35to40' in systematic and  e.pt_3 > 35 and  e.pt_3 < 40 : tau3pt35 = True
		if 'ptgt40' in systematic and  e.pt_3 > 40:  tau3pthigh = True

                tau4pt20, tau4pt25, tau4pt30, tau4pt35, tau4pthigh = False, False, False, False, False
		if 'pt20to25' in systematic and  e.pt_4 > 20 and  e.pt_4 < 25 : tau4pt20 = True
		if 'pt25to30' in systematic and  e.pt_4 > 25 and  e.pt_4 < 30 : tau4pt25 = True
		if 'pt30to35' in systematic and  e.pt_4 > 30 and  e.pt_4 < 35 : tau4pt30 = True
		if 'pt35to40' in systematic and  e.pt_4 > 35 and  e.pt_4 < 40 : tau4pt35 = True
		if 'ptgt40' in systematic and  e.pt_4 > 40:  tau4pthigh = True


                # leptons faking taus // muon->tau
                if  cat[2:] == 'et' :
                    
		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  weightTID *= antiEleSFToolT.getSFvsEta(e.eta_4,e.gen_match_4,var)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4,var)

                if  cat[2:] == 'mt' :

		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4,var)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  weightTID *= antiMuSFToolT.getSFvsEta(e.eta_4,e.gen_match_4,var)

		
                if  cat[2:] == 'tt' :
		    #muon faking _3 tau

		    if e.gen_match_3 == 2 or e.gen_match_3 == 4 : weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3,var)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 : weightTID *= antiMuSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4,var)

		    if e.gen_match_3 == 1 or e.gen_match_3 == 3 : weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_3,e.gen_match_3,var)
		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 : weightTID *= antiEleSFToolVL.getSFvsEta(e.eta_4,e.gen_match_4,var)

		if cat[2:] == 'tt' :
                    if e.gen_match_3 == 5 : 
			if 'tauid' not in systematic : weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3)

                        if 'tauid' in systematic : 
                            if tau3pt20 or tau3pt25 or tau3pt30 or tau3pt35 or tau3pthigh :  weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc=var)

                if  cat[2:] == 'tt'  or cat[2:] == 'mt' or cat[2:] == 'et' :
		    if e.gen_match_4 == 5 : 
			if 'tauid' not in systematic : weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4)

                        if 'tauid' in systematic : 
                            if tau4pt20 or tau4pt25 or tau4pt30 or tau4pt35 or tau4pthigh :  weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc=var)




                weight *= weightTID
                weightFM *= weightTID * ww

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)
            #####
            #if not tight1 or not tight2 : hGroup = 'fakes'

	    if not tight1 and tight2: hw_fm_new[hGroup][cat].Fill(1,fW1 )
	    if tight1 and not tight2 : hw_fm_new[hGroup][cat].Fill(2,fW2 )
	    if not tight1 and not tight2: hw_fm_new[hGroup][cat].Fill(3,fW0)
            #if group!='data' and group!='fakes' and group !='f1' and group !='f2' and (not tight1 or not tight2) : print weightFM , hGroup, cat, tight1, tight2, i, e.evt, nickName, fW1, fW2, fW0, e.gen_match_3, e.gen_match_4
           
            #print 'made thus far', leptons_sf
	    fastMTTmass, fastMTTtransverseMass = -1, -1
	    if args.redoFit.lower() == 'yes' or args.redoFit.lower() == 'true' or systematic in jesSyst or 'scale_met' in systematic : 
		fastMTTmass, fastMTTtransverseMass = runSVFit(e,tauV3, tauV4, MetV, cat[2:]) 
            else  : fastMTTmass, fastMTTtransverseMass = e.m_sv, e.mt_sv
	    #print 'new', fastMTTmass, 'old', e.m_sv, fastMTTtransverseMass, e.mt_sv, cat[2:] , args.redoFit.lower() , met, e.MET_pt_UnclUp , e.met ,'scale_met' in systematic


            mass = 0.0005
            if cat[:2] == 'mm' : mass = .105
            L1.SetPtEtaPhiM(e.pt_1, e.eta_1,e.phi_1,mass)
            L2.SetPtEtaPhiM(e.pt_2, e.eta_2,e.phi_2,mass)
            ZPt = (L1+L2).Pt()
            
	    ewkweight = 1.
	    ewkweightUp = 1.
	    ewkweightDown = 1.
            
            aweight, ratio_nlo_up, ratio_nlo_down = 1. ,1., 1.

	    if  nickName == 'ZHToTauTau' :  
                ewkweight = EWK.getEWKWeight(ZPt, "central")
                ewkweightUp = EWK.getEWKWeight(ZPt, "up")
                ewkweightDown = EWK.getEWKWeight(ZPt, "down")


                aweight = 0.001*3*(26.66 * ewkweight +0.31+0.11)
                ratio_nlo_up = (26.66 * ewkweightUp +0.31+0.11)/(26.66 * ewkweight +0.31+0.11)
                ratio_nlo_down = (26.66 * ewkweightDown +0.31+0.11)/(26.66 * ewkweight +0.31+0.11)

                #print 'for signal---------------------->', nickName, ewkweight, ewkweightUp, ewkweightDown , aweight, ratio_nlo_up, ratio_nlo_down
                if 'nloewkup' not in systematic.lower() and 'nloewkdown' not in  systematic.lower(): 
                    #print 'for signal---------------------->', nickName, ewkweight, ewkweightUp, ewkweightDown , 'aweight', aweight, 'weight nom',  weight,  'weightX0.7612', weight*0.7612, 'weight Xaweight', weight*aweight
                    weight *= aweight 
                if 'nloewkup' in systematic.lower() : 
                    weight *=aweight * ratio_nlo_up
                if 'nloewkdown' in systematic.lower() : 
                    weight *=aweight * ratio_nlo_down


	    for plotVar in plotSettings:
		#print plotVar
		val = getattr(e, plotVar, None)
                #print val, plotVar
                #if plotVar =='metvs' and group!='data': 
                #    pl = '(metpt_nom - met)/metpt_nom'
		#    #val = getattr(e, e.metpt_nom - e.met, None)
                #    #print 'for metvs', pl, e.metpt_nom - e.met
                #    val = e.metpt_nom - e.met
                #if plotVar =='metvs' and group=='data': val = 0.

		if val is not None: 
                    try: 
			if hGroup != 'data' : 
			    if hGroup !='fakes' and hGroup !='f1' and hGroup != 'f2' and hGroup !='Reducible': 
				hMC[hGroup][cat][plotVar].Fill(val,weight)
				if not isfakemc1 and not isfakemc2 and tight1 and tight2: 
                                    hMCFM[hGroup][cat][plotVar].Fill(val,weight)

			    if hGroup =='fakes' or hGroup =='f1' or hGroup == 'f2' or hGroup=='Reducible':  hMCFM[hGroup][cat][plotVar].Fill(val,ww)

			else : 
			    if tight1 and tight2 : 
				hMC[hGroup][cat][plotVar].Fill(val,1)
				hMCFM[hGroup][cat][plotVar].Fill(val,1)

                    except KeyError : continue

            #custom made variables

            tauV = tauV3 + tauV4
	    #print fastMTTmass, 'm now==================', ZPt, cat

            #new_jA,jB,jC : hold the ZpT<75, 75<ZpT<150, ZpT>150
            # jBC is filled for ZpT >75

            H_LT = e.pt_3 + e.pt_4
            if fastMTTmass <290 : 
		if hGroup != 'data' : 


		    if hGroup !='fakes' and hGroup !='f1' and hGroup != 'f2' and hGroup !='Reducible': 


                           
			hm_sv_new[hGroup][cat].Fill(fastMTTmass,weight )
			hmt_sv_new[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			hH_LT[hGroup][cat].Fill(H_LT,weight )

                        
                        iBin = hm_sv_new[hGroup][cat].FindBin(fastMTTmass)

			if ZPt>75 and ZPt < 150 : iBin += 7
			if ZPt>150 : iBin += 14
                        if group =='ZH' : 
			    if e.HTXS_Higgs_cat == 400 : hm_sv_new_lep_FWDH_htt125[group][cat].Fill(iBin,weight )
			    if e.HTXS_Higgs_cat == 401 : hm_sv_new_lep_PTV_0_75_htt125[group][cat].Fill(iBin,weight )
			    if e.HTXS_Higgs_cat == 402 : hm_sv_new_lep_PTV_75_150_htt125[group][cat].Fill(iBin,weight )
			    if e.HTXS_Higgs_cat == 403 : hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].Fill(iBin,weight )
			    if e.HTXS_Higgs_cat == 404 : hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].Fill(iBin,weight )
			    if e.HTXS_Higgs_cat == 405 : hm_sv_new_lep_PTV_GT250_htt125[group][cat].Fill(iBin,weight )

                        if group =='ggZH' : 
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

			if ZPt < 75 : 
			    hm_sv_new_jA[hGroup][cat].Fill(fastMTTmass,weight )

			if ZPt>75 and ZPt < 150 : 
			    hm_sv_new_jB[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_jBC[hGroup][cat].Fill(fastMTTmass,weight )
				   
			#if ZPt>150 and ZPt < 250 : 
			if ZPt>150 :
			    hm_sv_new_jC[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_jBC[hGroup][cat].Fill(fastMTTmass,weight )

			if not isfakemc1 and not isfakemc2 and tight1 and tight2: 

			    hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,weight )
			    hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			    hH_LT_FM[hGroup][cat].Fill(H_LT,weight )

			    if ZPt < 75 : 
				hm_sv_new_FMjA[hGroup][cat].Fill(fastMTTmass,weight )

			    if ZPt>75 and ZPt < 150 : 
				hm_sv_new_FMjB[hGroup][cat].Fill(fastMTTmass,weight )
				hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )
				       
			    if ZPt > 150 : 
				hm_sv_new_FMjC[hGroup][cat].Fill(fastMTTmass,weight )
				hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )

		    if hGroup =='fakes' or hGroup =='f1' or hGroup == 'f2' or 'Reducible' in hGroup:  
			weight = ww

			hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,weight )
			hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,weight )
			hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			hH_LT_FM[hGroup][cat].Fill(H_LT,weight )


                        iBin =hm_sv_new[hGroup][cat].FindBin(fastMTTmass)

			if ZPt>75 and ZPt < 150 : iBin += 7
			if ZPt>150 : iBin += 14

                        if e.HTXS_Higgs_cat == 400 : hm_sv_new_lep_FWDH_htt125[group][cat].Fill(iBin,weight )
                        if e.HTXS_Higgs_cat == 401 : hm_sv_new_lep_PTV_0_75_htt125[group][cat].Fill(iBin,weight )
                        if e.HTXS_Higgs_cat == 402 : hm_sv_new_lep_PTV_75_150_htt125[group][cat].Fill(iBin,weight )
                        if e.HTXS_Higgs_cat == 403 : hm_sv_new_lep_PTV_150_250_0J_htt125[group][cat].Fill(iBin,weight )
                        if e.HTXS_Higgs_cat == 404 : hm_sv_new_lep_PTV_150_250_GE1J_htt125[group][cat].Fill(iBin,weight )
                        if e.HTXS_Higgs_cat == 405 : hm_sv_new_lep_PTV_GT250_htt125[group][cat].Fill(iBin,weight )


                        #hm_sv_new_FMjall[group][cat].Fill(iBin,weight)


			if ZPt < 75 : 
			    hm_sv_new_FMjA[hGroup][cat].Fill(fastMTTmass,weight )

			if ZPt>75 and ZPt < 150 : 
			    hm_sv_new_FMjB[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )
				   
			if ZPt > 150 : 
			    hm_sv_new_FMjC[hGroup][cat].Fill(fastMTTmass,weight )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,weight )


		else :  ##this is data
		    if tight1 and tight2 : 
			hmt_sv_new[hGroup][cat].Fill(fastMTTtransverseMass,1)
			hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,1)

			hH_LT[hGroup][cat].Fill(H_LT,1)
			hH_LT_FM[hGroup][cat].Fill(H_LT,1)

			hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,1)
			hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,1)
			hm_sv_new[hGroup][cat].Fill(fastMTTmass,1)

                        iBin = hm_sv_new[hGroup][cat].FindBin(fastMTTmass)

			if ZPt>75 and ZPt < 150 : iBin += 7
			if ZPt>150 : iBin += 14

                        #hm_sv_new_FMjall[group][cat].Fill(iBin,1)

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
            #print '{0:s} \t {1:d} \t  {2:d}  {3:d}  {4:.3f} \t {5:.3f} \t {6:.3f} \t {7:.3f} \t {8:.6f} \t {9:.6f} \t {10:.6f} \t {11:.6f} \t {12:.6f}'.format(cat,  e.lumi,  e.run, e.evt,  e.pt_1, e.pt_2, e.pt_3, e.pt_4, metcor, btag, e.L1PreFiringWeight_Nom, e.HTXS_Higgs_cat, e.mll ), weight

        
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
	    #for i in range(1,  hCutFlowN[cat][nickName].GetNbinsX()) : 
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
            hm_sv_new_FMjall[group][cat].SetBinContent(i,hm_sv_new_FMjA[group][cat].GetBinContent(i))
            hm_sv_new_FMjall[group][cat].SetBinContent(i+7,hm_sv_new_FMjB[group][cat].GetBinContent(i))
            hm_sv_new_FMjall[group][cat].SetBinContent(i+14,hm_sv_new_FMjC[group][cat].GetBinContent(i))

            hm_sv_new_FMjall[group][cat].SetBinError(i,hm_sv_new_FMjA[group][cat].GetBinError(i))
            hm_sv_new_FMjall[group][cat].SetBinError(i+7,hm_sv_new_FMjB[group][cat].GetBinError(i))
            hm_sv_new_FMjall[group][cat].SetBinError(i+14,hm_sv_new_FMjC[group][cat].GetBinError(i))

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
    


