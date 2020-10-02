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
import ScaleFactor as SF
sys.path.append('./TauPOG')
from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool
import fakeFactor 


def catToNumber(cat) :
    number = { 'eeet':1, 'eemt':2, 'eett':3, 'eeem':4, 'mmet':5, 'mmmt':6, 'mmtt':7, 'mmem':8, 'et':9, 'mt':10, 'tt':11 }
    return number[cat]

def numberToCat(number) :
    cat = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem', 9:'et', 10:'mt', 11:'tt' }
    return cat[number]


def systToNumber(syst) :
    varSyst= { 'none':0, 'nom':1, 'jesTotalUp':2, 'jesTotalDown':3, 'jerUp':4, 'jerDown':5, 'UnclUp':6, 'UnclDown':7}
    return varSyst[str(syst)]

def NumberToSyst(num) :
    varSyst= { 0:'none', 1:'nom', 2:'jesTotalUp', 3:'jesTotalDown', 4:'jerUp', 5:'jerDown', 6:'UnclUp', 7:'UnclDown'}
    return varSyst[num]

def systForMET(syst) :
    varSyst= {'none':'',  'nom':'nom', 'jesTotalUp':'JESUp', 'jesTotalDown':'JESDown', 'jerUp':'JESUp', 'jerDown':'JESDown', 'UnclUp':'UnclUp', 'UnclDown':'UnclDown'}

    return varSyst[str(syst)]


varSystematics=['none', 'nom', 'jesTotalUp', 'jesTotalDown', 'jerUp', 'jerDown', 'UnclUp', 'UnclDown']



def search(values, searchFor):
    for k in values:
        for v in values[k]:
            if searchFor ==v:
                return True
    return False

def runSVFit(entry,tau1,  tau2,  METV, channel,  doJME, variation) :
		  
    measuredMETx = METV.Pt()*cos(METV.Phi())
    measuredMETy = METV.Pt()*sin(METV.Phi())
    if doJME  :
        metpt = 'metpt_'+variation
        metphi = 'methi_'+variation
        valpt = getattr(e, 'metpt_'+variation, None)
        valphi= getattr(e, 'metphi_'+variation, None)
	#measuredMETx = 'entry.metpt_{0:s}*cos(entry.metphi_{0:s}'.format(str(variation)) #entry.metpt_+variation*cos(entry.metphi_+variation)
	#measuredMETy = 'entry.metpt_{0:s}*sin(entry.metphi_{0:s}'.format(str(variation)) #entry.metpt_+variation*cos(entry.metphi_+variation)
	measuredMETx = valpt*cos(valphi)
	measuredMETy = valpt*sin(valphi)

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
	measTau1 = ROOT.MeasuredTauLepton(kTauToHadDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), tau1.E())
		    
    if channel != 'em' :
	measTau2 = ROOT.MeasuredTauLepton(kTauToHadDecay, tau2.Pt(), tau2.Eta(), tau2.Phi(), tau2.E())

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

#def runSVFit(entry, channel,  doJME, met, metphi) :
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
    parser.add_argument("--looseCuts",action='store_true',help="Loose cuts")
    parser.add_argument("-r", "--redoFit",default='no',help="redo FastMTT and adjust MET after to Tau ES corrections")
    parser.add_argument("-w", "--workingPoint",type=int, default=16, help="working point for fakes 16 (M), 32(T), 64(VT), 128(VVT)")
    parser.add_argument("-b", "--bruteworkingPoint",type=int, default=16, help="make working point for fakes 16 (M), 32(T), 64(VT), 128(VVT)")
    parser.add_argument("-p", "--plotsScheme",type=bool, default=False, help="more categories for the plots")
    parser.add_argument("-j", "--inSystematics",type=str, default='',help='systematic variation - choose from nom, jesTotalUp, jesTotalDown, jerUp, jerDown')
    parser.add_argument("-e", "--extraTag",type=str, default='',help='extra tag; wL, noL wrt to fakes method')
    parser.add_argument("-g", "--genTag",type=str, default='',help='extra tag for gen, pow or mcnlo')
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


def getFakeWeightsvspTvsDM(ic, pt1,pt2, WP, DM1, DM2) :
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
    filein = './FakesResult_{0:s}_SS_{1:s}WP.root'.format(str(args.year),str(WP))
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
tightCuts = not args.looseCuts 
dataDriven = not args.MConly

dataDriven = True


inputSystematics=[]

if str(args.inSystematics) not in varSystematics : 
    print 'the input ', args.inSystematics, ' systematic does not exist, choose on from:', varSystematics
    sys.exit() 
#inputSystematics.append(str(args.inSystematics))

Pblumi = 1000.
tauID_w = 1.

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


# Tau Decay types
kUndefinedDecayType, kTauToHadDecay,  kTauToElecDecay, kTauToMuDecay = 0, 1, 2, 3   

gInterpreter.ProcessLine(".include .")
for baseName in ['./SVFit/MeasuredTauLepton','./SVFit/svFitAuxFunctions','./SVFit/FastMTT', './HTT-utilities/RecoilCorrections/src/MEtSys', './HTT-utilities/RecoilCorrections/src/RecoilCorrector'] : 
    if os.path.isfile("{0:s}_cc.so".format(baseName)) :
	gInterpreter.ProcessLine(".L {0:s}_cc.so".format(baseName))
    else :
	gInterpreter.ProcessLine(".L {0:s}.cc++".format(baseName))   
	# .L is not just for .so files, also .cc

jm=['0j','1j','2j','j']
reg=['A','B','C','D']
hnames =['hm_sv_new', 'hm_sv_new_FM']

print 'compiled it====================================================================='

weights= {''}


campaign = {2016:'2016Legacy', 2017:'2017ReReco', 2018:'2018ReReco'}







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


if era == '2016' : recoilCorrector  = ROOT.RecoilCorrector("./Type1_PFMET_Run2016BtoH.root");
if era == '2017' : recoilCorrector  = ROOT.RecoilCorrector("./Type1_PFMET_2017.root");
if era == '2018' : recoilCorrector  = ROOT.RecoilCorrector("./TypeI-PFMet_Run2018.root");


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
hMCnof = {}
hMCFM = {}

hm_sv_new = {}
hm_sv_new_FM = {}
hm_sv_new_FMext = {}
hmt_sv_new = {}
hmt_sv_new_FM = {}

# pT <75, 0,1, >1 jets

hm_sv_new_jA = {}
hm_sv_new_jB = {}
hm_sv_new_jC = {}
hm_sv_new_jBC = {}

hm_sv_new0jA = {}
hm_sv_new_FM0jA = {}
hm_sv_new1jA = {}
hm_sv_new_FM1jA = {}
hm_sv_new2jA = {}
hm_sv_new_FM2jA = {}
hm_sv_newjA = {}
hm_sv_new_FMjA = {}

hm_sv_new_FMjall = {}
hm_sv_new_jall = {}
hm_sv_new_FMjallv2 = {}

# 75<pT <150, 0,1, >1 jets
hm_sv_new0jB = {}
hm_sv_new_FM0jB = {}
hm_sv_new1jB = {}
hm_sv_new_FM1jB = {}
hm_sv_new2jB = {}
hm_sv_new_FM2jB = {}
hm_sv_newjB = {}
hm_sv_new_FMjB = {}
hm_sv_new_FMjBC = {}


# 150<pT <250, 0,1, >1 jets
hm_sv_new0jC = {}
hm_sv_new_FM0jC = {}
hm_sv_new1jC = {}
hm_sv_new_FM1jC = {}
hm_sv_new2jC = {}
hm_sv_new_FM2jC = {}
hm_sv_newjC = {}
hm_sv_new_FMjC = {}

# 75<pT <150, 0,1, >1 jets
hm_sv_new0jD = {}
hm_sv_new_FM0jD = {}
hm_sv_new1jD = {}
hm_sv_new_FM1jD = {}
hm_sv_new2jD = {}
hm_sv_new_FM2jD = {}
hm_sv_newjD = {}
hm_sv_new_FMjD = {}




hw_fm_new = {}
hH_LT= {}
hH_LT_FM= {}
hCutFlow = {}
hCutFlowN = {}
hCutFlowFM = {}
hW = {}
hTriggerW= {}
hLeptonW= {}
hCutFlowPerGroup = {}
hCutFlowPerGroupFM = {}
WCounter = {}


isW = False
isDY = False
muonMass = 0.106
electronMass = 0.000511
		
MetV = TLorentzVector()
MetVcor = TLorentzVector()
tauV3 = TLorentzVector()
tauV4 = TLorentzVector()
tauV = TLorentzVector()
tauV3cor = TLorentzVector()
tauV3corUp = TLorentzVector()
tauV3corDown = TLorentzVector()
tauV4cor = TLorentzVector()
tauV4corUp = TLorentzVector()
tauV4corDown = TLorentzVector()
L1 = TLorentzVector()
L2 = TLorentzVector()
L1.SetXYZM(0,0,0,0)
L2.SetXYZM(0,0,0,0)
L1g = TLorentzVector()
L2g = TLorentzVector()
L1g.SetXYZM(0,0,0,0)
L2g.SetXYZM(0,0,0,0)
MetV.SetXYZM(0,0,0,0)
MetVcor.SetXYZM(0,0,0,0)
tauV3.SetXYZM(0,0,0,0)
tauV4.SetXYZM(0,0,0,0)
tauV3cor.SetXYZM(0,0,0,0)
tauV4cor.SetXYZM(0,0,0,0)
tauV3corUp.SetXYZM(0,0,0,0)
tauV3corUp.SetXYZM(0,0,0,0)
tauV4corDown.SetXYZM(0,0,0,0)
tauV4corDown.SetXYZM(0,0,0,0)
tauV.SetXYZM(0,0,0,0)

# dictionary where the nickName is the key
nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}

#groups = ['fakes','Signal','Other','Top','DY','WZ','ZZ','data']
#groups = ['Signal','Other','Top','DY','WZ','ZZ','data','fakes','f1','f2']
groups = ['Reducible','fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','qqZH','ggZH', 'WH','Other','Top','DY','WZ','ZZ','data']

ngroups = ['Reducible', 'fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','qqZH','ggZH', 'WH','Other','Top','DY','WZ','ZZ','data']
ngroups = ['Reducible', 'fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','qqZH','ggZH', 'WH','Other','ZZ','data']

ngroups = ['Reducible', 'fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','qqZH','ggZH', 'WH','Other','ZZ','data']

ngroups = ['Reducible', 'fakes','f1', 'f2','gfl1','bfl1', 'lfl1','lfl2','ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','Other','ZZ']
fgroups = ['bfl', 'ljfl',  'cfl','jfl', 'jft1', 'jft2']

if str(args.gType.lower()) != 'other' : 
    ngroups = [] 
    ngroups.append(str(args.gType))


for group in groups :
    nickNames[group] = []


# make a first pass to get the weights


WJets_kfactor = 1.166
DY_kfactor = 1.137

WNJetsXsecs = [40322.3]  #LO for 0-jet
DYNJetsXsecs = [4738.53]  #LO  for 0-jet

WIncl_xsec = 52760*WJets_kfactor ##LO *kfactor inclusive
DYIcl_xsec = 6077.22 ##NNLO inclusive


WxGenweightsArr = []
DYxGenweightsArr = []



islocal=False
if str(args.isLocal) == '1' or str(args.isLocal) =='yes' : islocal=True




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


for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    if '#' in vals[0] : continue
    nickName = vals[0]
    group = vals[1]
    nickNames[group].append(nickName)
    if '*' in vals[2] : 
        value1, value2 = map(float, vals[2].split("*"))
        xsec[nickName] = float(value1*value2)
    else : xsec[nickName] = float(str(vals[2]))
    #totalWeight[nickName] = float(vals[4])
    if islocal :    filein = '../MC/condor/{0:s}//{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
    else : filein = '{1:s}_{2:s}.root'.format(args.analysis,vals[0],era)
    if 'data' not in filein : 
	fIn = TFile.Open(filein,"READ")
	totalWeight[nickName] = float(fIn.Get("hWeights").GetSumOfWeights())
	sampleWeight[nickName]= Pblumi*weights['lumi']*xsec[nickName]/totalWeight[nickName]
    else : 
        #nickName = 'data_{0:s}'.format(era)
        totalWeight[nickName] = 1.
        sampleWeight[nickName] = 1.
    

    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

    #print("{0:100s}  & {1:10.3f} & {2:11.1f} & {3:10.6f}\\\\\\hline".format(
    #     str(vals[6]),xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

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



print nickNames

print("tightCuts={0}".format(tightCuts))
if tightCuts :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut))
    if args.MConly :
        print("args.MConly is TRUE")
        outFileName = outFileName.replace('.root','_MC.root') 
else :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_loose.root'.format(args.year,args.sign,int(args.LTcut))
    
if args.redoFit.lower() == 'no' : outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_{3:s}noSV'.format(args.year,args.sign,int(args.LTcut), str(args.workingPoint))
if args.redoFit.lower() != 'no' : outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_{3:s}SV'.format(args.year,args.sign,int(args.LTcut), str(args.workingPoint))


WP = args.workingPoint
vertag = str(args.genTag)
WPSR= 16
if args.workingPoint == args.bruteworkingPoint : WPSR = WP
outFileName = outFileName +"_"+str(args.bruteworkingPoint)+"brute_"+str(args.inSystematics)
FF = fakeFactor.fakeFactor(args.year,WP,extratag, vertag)


ffout='testZH_{0:s}_{1:s}.root'.format(extratag,vertag)
if vertag== '' : ffout='testZH_{0:s}.root'.format(extratag)

ffout='testFile.root'

print("Opening {0:s} as output.".format(ffout))
fOut = TFile( ffout, 'recreate' )

plotSettings = { # [nBins,xMin,xMax,units]
        "m_sv":[20,0,400,"[Gev]","m(#tau#tau)(SV)"]}

plotSettingss = { # [nBins,xMin,xMax,units]

        "weight":[20,-10,10,"","PUWeight"],
        "weightPUtrue":[20,-10,10,"","PUtrue"],
        "nPV":[120,-0.5,119.5,"","nPV"],
        "nPU":[130,-0.5,129.5,"","nPU"],
        "nPUtrue":[130,-0.5,129.5,"","nPUtrue"],
        "Generator_weight":[20,-10,10,"","genWeight"],

        "pt_1":[8,0,160,"[Gev]","P_{T}(#tau_{1})"],
        "eta_1":[30,-3,3,"","#eta(l_{1})"],
        "phi_1":[30,-3,3,"","#phi(l_{1})"],
        "iso_1":[20,0,1,"","relIso(l_{1})"],
        "dZ_1":[10,-0.1,0.1,"[cm]","d_{z}(l_{1})"],
        "d0_1":[10,-0.1,0.1,"[cm]","d_{xy}(l_{1})"],
        "q_1":[3,-1.5,1.5,"","charge(l_{1})"],

        "pt_2":[8,0,160,"[Gev]","P_{T}(l_{2})"],
        "eta_2":[30,-3,3,"","#eta(l_{2})"],
        "phi_2":[30,-3,3,"","#phi(l_{2})"],
        "iso_2":[20,0,1,"","relIso(l_{2})"],
        "dZ_2":[10,-0.1,0.1,"[cm]","d_{z}(l_{2})"],
        "d0_2":[10,-0.1,0.1,"[cm]","d_{xy}(l_{2})"],
        "q_2":[3,-1.5,1.5,"","charge(l_{2})"],

	"iso_3":[20,0,1,"","relIso(l_{3})"],
        "pt_3":[8,0,160,"[Gev]","P_{T}(l_{3})"],
        "eta_3":[30,-3,3,"","#eta(l_{3})"],
        "phi_3":[30,-3,3,"","#phi(l_{3})"],
        "dZ_3":[10,-0.1,0.1,"[cm]","d_{z}(l_{3})"],
        "d0_3":[10,-0.1,0.1,"[cm]","d_{xy}(l_{3})"],

        "iso_4":[20,0,1,"","relIso(l_{4})"],
        "pt_4":[8,0,160,"[Gev]","P_{T}(l_{4})"],
        "eta_4":[30,-3,3,"","#eta(l_{4})"],
        "phi_4":[30,-3,3,"","#phi(l_{4})"],
        "dZ_4":[10,-0.1,0.1,"[cm]","d_{z}(l_{4})"],
        "d0_4":[10,-0.1,0.1,"[cm]","d_{xy}(l_{4})"],

        "njets":[10,-0.5,9.5,"","nJets"],

        "jpt_1":[10,0,200,"[GeV]","Jet^{1} P_{T}"], 
        "jeta_1":[30,-3,3,"","Jet^{1} #eta"],
        "jpt_2":[10,0,200,"[GeV]","Jet^{2} P_{T}"], 
        "jeta_2":[6,-3,3,"","Jet^{2} #eta"],

        #"bpt_1":[10,0,200,"[GeV]","BJet^{1} P_{T}"], 

        "nbtag":[5,-0.5,4.5,"","nBTag"],

        #"metvs":[20,-2,2,"[GeV]","#it{p}_{T}^{miss}*"], 
        #"metpt_nom":[10,0,200,"[GeV]","#it{p}_{T}^{miss}*"], 
        #"metphi_nom":[30,-3,3,"","#it{p}_{T}^{miss} #phi*"], 
        "met":[20,0,400,"[GeV]","#it{p}_{T}^{miss}"], 
        "metphi":[30,-3,3,"","#it{p}_{T}^{miss} #phi"], 

        "mll":[40,50,130,"[Gev]","m(l^{+}l^{-})"],

        "m_vis":[15,50,200,"[Gev]","m(#tau#tau)"],
        "pt_tt":[10,0,200,"[GeV]","P_{T}(#tau#tau)"],
        "H_DR":[60,0,6,"","#Delta R(#tau#tau)"],
        "H_tot":[30,0,200,"[GeV]","m_{T}tot(#tau#tau)"],

        "mt_sv":[20,0,400,"[Gev]","m_{T}(#tau#tau)"],
        "m_sv":[20,0,400,"[Gev]","m(#tau#tau)(SV)"],
        #"AMass":[50,50,550,"[Gev]","m_{Z+H}(SV)"],

        "Z_Pt":[10,0,200,"[Gev]","P_T(l_{1}l_{2})"],
        #"Z_DR":[30,0,6,"[Gev]","#Delta R(l_{1}l_{2})"],
        "gen_match_1":[30,-0.5,29.5,"","gen_match_1"],
        "gen_match_2":[30,-0.5,29.5,"","gen_match_2"],
        "gen_match_3":[30,-0.5,29.5,"","gen_match_3"],
        "gen_match_4":[30,-0.5,29.5,"","gen_match_4"]
        }


canvasDict = {}
legendDict = {}
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


########## initializing triggers
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
antiEleSFToolT = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSe','Tight')
antiMuSFToolT  = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSmu','Tight')



sf_MuonTrig = SF.SFs()
sf_MuonTrig.ScaleFactor("{0:s}{1:s}".format(TriggerSF['dir'],TriggerSF['fileMuon']))
sf_EleTrig = SF.SFs()
sf_EleTrig.ScaleFactor("{0:s}{1:s}".format(TriggerSF['dir'],TriggerSF['fileElectron']))

sf_MuonId = SF.SFs()
sf_MuonId.ScaleFactor("{0:s}{1:s}".format(LeptonSF['dir'],LeptonSF['fileMuon0p2']))
sf_ElectronId = SF.SFs()
sf_ElectronId.ScaleFactor("{0:s}{1:s}".format(LeptonSF['dir'],LeptonSF['fileElectron0p15']))


#for icat, cat in cats.items()[0:8] :

for icat, cat in cats.items()[0:8] :
    hCutFlow[cat] = {}
    hCutFlowN[cat] = {}
    hCutFlowFM[cat] = {}
    hW[cat] = {}

isSignal = False
for group in groups :

    if 'qqZH' in group or 'ggZH' in group or 'WH' in group  : isSignal = True
    for inick, nickName in enumerate(nickNames[group]) :
        #if group == 'data':
	#    #inFileName = './data/{0:s}/data_{1:s}/{2:s}.root'.format(args.analysis,era,nickName)
	#    inFileName = './data/{0:s}//data_{1:s}/{2:s}.root'.format(args.analysis,era,nickName)
        for icat, cat in cats.items()[0:8] :
	    #setting up the CutFlow histogram
	    hCutFlow[cat][nickName] = {}
	    hCutFlowN[cat][nickName] = {}
	    hCutFlowFM[cat][nickName] = {}
	    hW[cat][nickName] = {}
	    hW[cat][nickName] = TH1D("hW_"+nickName+"_"+cat,"weights",3,-0.5,2.5)
	    hCutFlowN[cat][nickName] = TH1D("hCutFlow_"+nickName+"_"+cat,"CutFlow",20,-0.5,19.5)
	    hCutFlowFM[cat][nickName] = TH1D("hCutFlowFM_"+nickName+"_"+cat,"CutFlow",20,-0.5,19.5)

	    #if group != 'data' :
	    inFileName = '{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
	    if islocal : 
                if group != 'data' : inFileName = '../MC/condor/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
                else : inFileName = '../data/condor/{0:s}/data_{2:s}/data_{2:s}.root'.format(args.analysis,nickName,era)

	    inFile = TFile.Open(inFileName)
	    inFile.cd()

	    #print '========================================> will use this one',inFileName, inick, nickName, cat, inick, nicks
	    if group != 'data' :
		hCutFlow[cat][nickName] = inFile.Get("hCutFlowWeighted_{0:s}".format(cat))
	    else :
		hCutFlow[cat][nickName] = inFile.Get("hCutFlow_{0:s}".format(cat))
            
	    for i in range(1,10) :
 		WCounter[i-1][icat-1][inick] = float(hCutFlow[cat][nickName].GetBinContent(i))
                hCutFlowN[cat][nickName].SetBinContent(i,WCounter[i-1][icat-1][inick])
		#print i, hCutFlow[cat][nickName].GetBinContent(i), hCutFlow[cat][nickName].GetXaxis().GetBinLabel(i), cat, ' <===>', WCounter[i-1][icat-1][inick], nickName
            
	    inFile.Close()

for ig, group in enumerate(groups) :

    hMC[group] = {}
    hMCnof[group] = {}
    hMCFM[group] = {}
    hm_sv_new[group] = {}
    hm_sv_new_FM[group] = {}
    hm_sv_new_FMext[group] = {}

    hm_sv_new_jA[group] = {}
    hm_sv_new_jB[group] = {}
    hm_sv_new_jC[group] = {}
    hm_sv_new_jBC[group] = {}

    hm_sv_new0jA[group] = {}
    hm_sv_new_FM0jA[group] = {}
    hm_sv_new1jA[group] = {}
    hm_sv_new_FM1jA[group] = {}
    hm_sv_new2jA[group] = {}
    hm_sv_new_FM2jA[group] = {}
    hm_sv_newjA[group] = {}
    hm_sv_new_FMjA[group] = {}
    hm_sv_new_FMjall[group] = {}
    hm_sv_new_FMjallv2[group] = {}
    hm_sv_new_jall[group] = {}

    hm_sv_new0jB[group] = {}
    hm_sv_new_FM0jB[group] = {}
    hm_sv_new1jB[group] = {}
    hm_sv_new_FM1jB[group] = {}
    hm_sv_new2jB[group] = {}
    hm_sv_new_FM2jB[group] = {}
    hm_sv_newjB[group] = {}
    hm_sv_new_FMjB[group] = {}
    hm_sv_new_FMjBC[group] = {}



    hm_sv_new0jC[group] = {}
    hm_sv_new_FM0jC[group] = {}
    hm_sv_new1jC[group] = {}
    hm_sv_new_FM1jC[group] = {}
    hm_sv_new2jC[group] = {}
    hm_sv_new_FM2jC[group] = {}
    hm_sv_newjC[group] = {}
    hm_sv_new_FMjC[group] = {}


    hm_sv_new0jD[group] = {}
    hm_sv_new_FM0jD[group] = {}
    hm_sv_new1jD[group] = {}
    hm_sv_new_FM1jD[group] = {}
    hm_sv_new2jD[group] = {}
    hm_sv_new_FM2jD[group] = {}
    hm_sv_newjD[group] = {}
    hm_sv_new_FMjD[group] = {}

    hmt_sv_new[group] = {}
    hmt_sv_new_FM[group] = {}



    hw_fm_new[group] = {}
    hTriggerW[group] = {}
    hLeptonW[group] = {}
    hH_LT[group] = {}
    hH_LT_FM[group] = {}
    hCutFlowPerGroup[group] = {}
    hCutFlowPerGroupFM[group] = {}
   

    for icat, cat in cats.items()[0:8] :
        hMC[group][cat] = {}
        hMCnof[group][cat] = {}
        hMCFM[group][cat] = {}

        hName = 'h{0:s}_{1:s}'.format(group,cat)

        hH_LT[group][cat] = TH1D(hName+'_H_LT',hName+'_H_LT',10,0,200)
        hH_LT[group][cat].SetDefaultSumw2()
        hH_LT_FM[group][cat] = TH1D(hName+'_H_LT_FM',hName+'_H_LT',10,0,200)
        hH_LT_FM[group][cat].SetDefaultSumw2()
        hTriggerW[group][cat] = TH1D (hName+'_TriggerW',hName+'_TriggerW',75,0.75,1.50)
        hLeptonW[group][cat] = TH1D (hName+'_LeptonW',hName+'_LeptonW',40,0.8,1.2)
        hTriggerW[group][cat].SetDefaultSumw2()
        hLeptonW[group][cat].SetDefaultSumw2()

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

	hm_sv_new0jA[group][cat] = {}
	hm_sv_new_FM0jA[group][cat] = {}
	hm_sv_new1jA[group][cat] = {}
	hm_sv_new_FM1jA[group][cat] = {}
	hm_sv_new2jA[group][cat] = {}
	hm_sv_new_FM2jA[group][cat] = {}
	hm_sv_newjA[group][cat] = {}
	hm_sv_new_FMjA[group][cat] = {}
	hm_sv_new_FMjall[group][cat] = {}
	hm_sv_new_FMjallv2[group][cat] = {}
	hm_sv_new_jall[group][cat] = {}

	hm_sv_new0jB[group][cat] = {}
	hm_sv_new_FM0jB[group][cat] = {}
	hm_sv_new1jB[group][cat] = {}
	hm_sv_new_FM1jB[group][cat] = {}
	hm_sv_new2jB[group][cat] = {}
	hm_sv_new_FM2jB[group][cat] = {}
	hm_sv_newjB[group][cat] = {}
	hm_sv_new_FMjB[group][cat] = {}
	hm_sv_new_FMjBC[group][cat] = {}



	hm_sv_new0jC[group][cat] = {}
	hm_sv_new_FM0jC[group][cat] = {}
	hm_sv_new1jC[group][cat] = {}
	hm_sv_new_FM1jC[group][cat] = {}
	hm_sv_new2jC[group][cat] = {}
	hm_sv_new_FM2jC[group][cat] = {}
	hm_sv_newjC[group][cat] = {}
	hm_sv_new_FMjC[group][cat] = {}


	hm_sv_new0jD[group][cat] = {}
	hm_sv_new_FM0jD[group][cat] = {}
	hm_sv_new1jD[group][cat] = {}
	hm_sv_new_FM1jD[group][cat] = {}
	hm_sv_new2jD[group][cat] = {}
	hm_sv_new_FM2jD[group][cat] = {}
	hm_sv_newjD[group][cat] = {}
	hm_sv_new_FMjD[group][cat] = {}




	hmt_sv_new[group][cat] = {}
	hmt_sv_new_FM[group][cat] = {}

        #for syst in varSystematics : 

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


	hName = 'h{0:s}_{1:s}_m_sv_new0jA'.format(group,cat)
	hm_sv_new0jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new0jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new0jB'.format(group,cat)
	hm_sv_new0jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new0jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new0jC'.format(group,cat)
	hm_sv_new0jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new0jC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new0jD'.format(group,cat)
	hm_sv_new0jD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new0jD[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_m_sv_new1jA'.format(group,cat)
	hm_sv_new1jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new1jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new1jB'.format(group,cat)
	hm_sv_new1jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new1jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new1jC'.format(group,cat)
	hm_sv_new1jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new1jC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new1jD'.format(group,cat)
	hm_sv_new1jD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new1jD[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new2jA'.format(group,cat)
	hm_sv_new2jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new2jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new2jB'.format(group,cat)
	hm_sv_new2jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new2jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new2jC'.format(group,cat)
	hm_sv_new2jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new2jC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new2jD'.format(group,cat)
	hm_sv_new2jD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new2jD[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_newjA'.format(group,cat)
	hm_sv_newjA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_newjA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_newjB'.format(group,cat)
	hm_sv_newjB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_newjB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_newjC'.format(group,cat)
	hm_sv_newjC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_newjC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_newjD'.format(group,cat)
	hm_sv_newjD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_newjD[group][cat].SetDefaultSumw2()



	hName = 'h{0:s}_{1:s}_m_sv_new_FM0jA'.format(group,cat)
	hm_sv_new_FM0jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM0jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM0jB'.format(group,cat)
	hm_sv_new_FM0jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM0jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM0jC'.format(group,cat)
	hm_sv_new_FM0jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM0jC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM0jD'.format(group,cat)
	hm_sv_new_FM0jD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM0jD[group][cat].SetDefaultSumw2()


	hName = 'h{0:s}_{1:s}_m_sv_new_FM1jA'.format(group,cat)
	hm_sv_new_FM1jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM1jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM1jB'.format(group,cat)
	hm_sv_new_FM1jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM1jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM1jC'.format(group,cat)
	hm_sv_new_FM1jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM1jC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM1jD'.format(group,cat)
	hm_sv_new_FM1jD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM1jD[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_FM2jA'.format(group,cat)
	hm_sv_new_FM2jA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM2jA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM2jB'.format(group,cat)
	hm_sv_new_FM2jB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM2jB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM2jC'.format(group,cat)
	hm_sv_new_FM2jC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM2jC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FM2jD'.format(group,cat)
	hm_sv_new_FM2jD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FM2jD[group][cat].SetDefaultSumw2()

	hName = 'h{0:s}_{1:s}_m_sv_new_FMjA'.format(group,cat)
	hm_sv_new_FMjA[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjA[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjB'.format(group,cat)
	hm_sv_new_FMjB[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjB[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjC'.format(group,cat)
	hm_sv_new_FMjC[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjC[group][cat].SetDefaultSumw2()
	hName = 'h{0:s}_{1:s}_m_sv_new_FMjD'.format(group,cat)
	hm_sv_new_FMjD[group][cat] = TH1D(hName ,hName,  nbins, array('d',Bins))
	hm_sv_new_FMjD[group][cat].SetDefaultSumw2()

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

        for plotVar in plotSettings:
            hMC[group][cat][plotVar] = {}
            hMCnof[group][cat][plotVar] = {}
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

            hName = 'h{0:s}_{1:s}_{2:s}_nof'.format(group,cat,plotVar)
            hMCnof[group][cat][plotVar] = TH1D(hName,hName,nBins,xMin,xMax)
            hMCnof[group][cat][plotVar].SetDefaultSumw2()


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
	#cf = os.path.isfile('{0:s}'.format(inFileName))
	#if not cf : continue
        if group == 'data' :
            isData = True
            #varSystematics=['', 'nom']
            inFileName = 'data_{1:s}.root'.format(args.analysis,era,nickName)
            if islocal : inFileName = './data/{0:s}/data_{1:s}/data_{1:s}.root'.format(args.analysis,era,nickName)
	    print 'for data will use ',inFileName
        try :

            inFile = TFile.Open(inFileName)
            inFile.cd()
            inTree = inFile.Get("Events")
            nentries = inTree.GetEntries()
        except AttributeError :
            print("  Failure on file {0:s}".format(inFileName))
	    #continue
            exit()

        # resume here
        nEvents, totalWeight = 0, 0.
	sWeight = 0.
        DYJets = ('DYJetsToLL' in nickName and 'M10' not in nickName)
	WJets  = ('WJetsToLNu' in nickName and 'TW' not in nickName)
        sWeight = sampleWeight[nickName]
	print '========================================> start looping on events now',inFileName, inick, nickName, sWeight

        systmet = ''
	isys=0
	mu_iso = 0.15
	el_iso = 0.15
	mu_eta = 2.4
	el_eta = 2.5
	if doJME:
	    isys = systToNumber(str(args.inSystematics))
	    #isys = 1
	    if group=='data' : isys=1 #in case we run on data, consider the _nom systematic
            if 'Uncl' in str(args.inSystematics) : isys = 1 #UnclUp and UnclDown exist only on MET, for everything else use the _nom brach which is after the JEC corrections
            sysmet = systForMET(str(args.inSystematics))

        for i, e in enumerate(inTree) :

            inTree.GetEntry(i)
            iCut=icut
            hGroup = group
            trigw = 1.
	    weight=1.
            weightCF = 1.
	    weightFM=1.
            weightTID = 1.
            weightTIDUp = 1.
            weightTIDDown = 1.
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
                met = e.MET_pt_nom
                metphi = e.MET_phi_nom
            except AttributeError :
                met = e.met
                metphi = e.metphi
            
	    if str(args.inSystematics) != 'none': 
		met = getattr(e, 'metpt_'+sysmet, None)
		metphi = getattr(e, 'metphi_'+sysmet, None)
            #print 'ok now', doJME, isys, args.inSystematics, 'njets-->', njets, e.njets[0], e.njets[1], e.njets[2], 'btag-->', nbtag, e.nbtag[0], e.nbtag[1], e.nbtag[2], 'met-->', met, metphi, 'and met_nom', e.metpt_nom, e.metphi_nom, 'for syst', args.inSystematics, 'jetpT--->', jpt_1, e.jpt_1[0], e.jpt_1[1], e.jpt_1[2], group, i, nickName

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
		weight = e.weightPUtrue * e.Generator_weight *sWeight 
		#ww = e.weightPUtrue * e.Generator_weight *sWeight 
		weightFM = e.weightPUtrue * e.Generator_weight *sWeight * e.L1PreFiringWeight_Nom
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

            
	    if cat[2:] == 'tt' :
                    tight1 = e.idDeepTau2017v2p1VSjet_3 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_3 >= 0 and  e.idDeepTau2017v2p1VSe_3 >= 0
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_4 >= 0 and  e.idDeepTau2017v2p1VSe_4 >= 0

	    if cat[2:] == 'mt' : tight2 = e.idDeepTau2017v2p1VSjet_4 >  WPSR-1 and e.idDeepTau2017v2p1VSmu_4 >= 0 and  e.idDeepTau2017v2p1VSe_4 >= 0
	    if cat[2:] == 'et' : tight2  = e.idDeepTau2017v2p1VSjet_4 > WPSR-1 and e.idDeepTau2017v2p1VSmu_4 >= 0 and  e.idDeepTau2017v2p1VSe_4 >= 0


            
            if group != 'data' :
                if not tight1 or not tight2 : continue

            if not dataDriven and (not tight1 or not tight2) : continue

            #if group == 'data' :
            #    if DD[cat].checkEvent(e,cat) : continue 

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
	    try :
		if e.nbtag[0] > 0 : continue
	    except TypeError :
		if e.nbtag > 0 : continue

            iCut +=1
            WCounter[iCut-1][icat-1][inick] += weightCF
            hCutFlowN[cat][nickName].SetBinContent(iCut-1, hCutFlowN[cat][nickName].GetBinContent(iCut-1)+weight)
            hCutFlowFM[cat][nickName].SetBinContent(iCut-1, hCutFlowFM[cat][nickName].GetBinContent(iCut-1)+weightFM)

            ########### Trigger
            ################### Trigger SF
            
       
            if group == 'data' :
                if DD[cat].checkEvent(e,cat) : continue 

            ##### btag
            if group != 'data' :
		nj=e.njets[0]
		if nj > 0 :
		    #for ib in range(0, int(nj)) :
                    #    print nj, ib, e.jeta[ib], e.jpt[ib], i, cat

		    for ib in range(0, int(nj)) :
                        try : 
			    flv = 0
			    if abs(e.jflavour[ib]) == 5 : 
				btag_sf *= reader_b.eval_auto_bounds( 'central',  0,     abs(e.jeta[ib]), e.jpt[ib])
			    if abs(e.jflavour[ib]) == 4 : 
				btag_sf *= reader_c.eval_auto_bounds( 'central',  1,     abs(e.jeta[ib]), e.jpt[ib])
			    if abs(e.jflavour[ib]) < 4 or abs(e.jflavour[ib]) == 21 :
				btag_sf *= reader_light.eval_auto_bounds( 'central',  2,     abs(e.jeta[ib]), e.jpt[ib])
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
		    dm1=e.decayMode_3
		    dm2=e.decayMode_4
                    #if dm1 < 0 or dm2 < 0 : print 'problem with data ? ', dm1, dm2, e.pt_3, e.pt_4
		    #fW1, fW2, fW0 = getFakeWeightsvspT(cat[2:], e.pt_3, e.pt_4, WP)
		    fW1, fW2, fW0 = FF.getFakeWeightsvspTvsDM(cat[2:], e.pt_3, e.pt_4, WP, dm1, dm2)
		    #fW1, fW2, fW0 = getFakeWeightsvspT(cat[2:], e.pt_3, e.pt_4, WP, dm1, dm2)
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
		    
            weightFM=ww
           
            #if group != 'data' and group!='Signal' :
            #    if not isfakemc1 or not isfakemc2  : continue

            ########### tauID
            tauV3.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
            tauV4.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)
            tauV3cor.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
            tauV4cor.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)
            tauV3corUp  = tauV3cor
            tauV3corDown  = tauV3cor
            tauV4corUp  = tauV4cor
            tauV4corDown  = tauV4cor


	    MetV.SetPx(met * cos (metphi))
	    MetV.SetPy(met * sin (metphi))
	    MetVcor.SetPx(met * cos (metphi))
	    MetVcor.SetPy(met * sin (metphi))
	    met_x = met * cos(metphi)
	    met_y = met * sin(metphi)
	    metcor = met


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

            if group != 'data' and (cat[2:] == 'et' or cat[2:]  == 'mt' or cat[2:]  == 'tt') :

                # leptons faking taus // muon->tau
		if e.gen_match_4 == 1 or e.gen_match_4 == 3 :  weightTID *= antiEleSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)
		if e.gen_match_4 == 2 or e.gen_match_4 == 4 :  weightTID *= antiMuSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)

                '''
		    if e.decayMode_4 == 1 :  
			tauV4cor  *= (1 +  weights_muTotauES['DM1']*0.01)
			tauV4corUp  *= (1 +  weights_muTotauES['DM1']*0.01)
			tauV4corDown  *= (1 +  weights_muTotauES['DM1']*0.01)
			MetVcor +=  tauV4*(1 +  weights_muTotauES['DM1']*0.01)

			tauV4cor *= (1 +  weights_muTotauES['DM0']*0.01)
			tauV4corUp *= (1 +  weights_muTotauES['DM0']*0.01)
			tauV4corDown *= (1 +  weights_muTotauES['DM0']*0.01)
			MetVcor +=   tauV4*(1 +  weights_muTotauES['DM0']*0.01)


		    if e.decayMode_4 == 0 :  
			tauV4cor  *= (1 +  weights_elTotauES['DM0']*0.01)
			tauV4corUp  *= (1 +  weights_elTotauES['DM0']*0.01)
			tauV4corDown  *= (1 +  weights_elTotauES['DM0']*0.01)
			MetVcor +=   tauV4*(1 +  weights_elTotauES['DM0']*0.01)

		    if e.decayMode_4 == 1 :  
			tauV4cor  *= (1 +  weights_elTotauES['DM1']*0.01)
			tauV4corUp  *= (1 +  weights_elTotauES['DM1']*0.01)
			tauV4corDown  *= (1 +  weights_elTotauES['DM1']*0.01)
			MetVcor +=   tauV4*(1 +  weights_elTotauES['DM1']*0.01)
                '''

		
                if  cat[2:] == 'tt' :
		    #muon faking _3 tau

		    if e.gen_match_3 == 2 or e.gen_match_3 == 4 : weightTID *= antiMuSFToolT.getSFvsEta(e.eta_3,e.gen_match_3)
		    if e.gen_match_4 == 2 or e.gen_match_4 == 4 : weightTID *= antiMuSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)

		    if e.gen_match_3 == 1 or e.gen_match_3 == 3 : weightTID *= antiEleSFToolT.getSFvsEta(e.eta_3,e.gen_match_3)
		    if e.gen_match_4 == 1 or e.gen_match_4 == 3 : weightTID *= antiEleSFToolT.getSFvsEta(e.eta_4,e.gen_match_4)
                    '''

			if e.decayMode_3 == 1 :  
			    tauV3cor  *= (1 +  weights_muTotauES['DM1']*0.01)
			    tauV3corUp  *= (1 +  weights_muTotauES['DM1']*0.01)
			    tauV3corDown  *= (1 +  weights_muTotauES['DM1']*0.01)
			    MetVcor +=   tauV3*(1 +  weights_muTotauES['DM1']*0.01)

			if e.decayMode_3 == 0 :  

			    tauV3cor  *= (1 +  weights_muTotauES['DM0']*0.01)
			    tauV3corUp  *= (1 +  weights_muTotauES['DM0']*0.01)
			    tauV3corDown  *= (1 +  weights_muTotauES['DM0']*0.01)
			    MetVcor +=   tauV3*(1 +  weights_muTotauES['DM0']*0.01)


                    # electron faking _3 tau
		    if e.gen_match_3 == 1 or e.gen_match_3 == 3 :
		        #weightTID *= festool.getFES(e.eta_3,e.decayMode_3,e.gen_match_3)
			if e.decayMode_3 == 0 :  

			    tauV3cor  *= (1 +  weights_elTotauES['DM0']*0.01)
			    tauV3corUp  *= (1 +  weights_elTotauES['DM0']*0.01)
			    tauV3corDown  *= (1 +  weights_elTotauES['DM0']*0.01)
			    MetVcor +=   tauV3*(1 +  weights_elTotauES['DM0']*0.01)

			if e.decayMode_3 == 1 :  

			    tauV3cor  *= (1 +  weights_elTotauES['DM1']*0.01)
			    tauV3corUp  *= (1 +  weights_elTotauES['DM1']*0.01)
			    tauV3corDown  *= (1 +  weights_elTotauES['DM1']*0.01)
			    MetVcor +=   tauV3*(1 +  weights_elTotauES['DM1']*0.01)
                    '''

		if cat[2:] == 'tt' :
                    if e.gen_match_3 == 5 : 
			weightTID *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3)
			weightTIDUp *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Up')
			weightTIDDown *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3, unc='Down')

                        #print 'tesSTOOL', testool.getTES(e.pt_3, e.decayMode_3, e.gen_match_3)

                        '''
			tauV3cor *= testool.getTES(e.pt_3, e.decayMode_3, e.gen_match_3)
			tauV3corUp *= testool.getTES(e.pt_3, e.decayMode_3, e.gen_match_3,unc='Up')
			tauV3corDown *= testool.getTES(e.pt_3, e.decayMode_3, e.gen_match_3,unc='Down')


			if e.decayMode_3 == 1 : 
			    e.m_3 =  0.1396  
			    tauV3cor.SetE(0.1396)
			    tauV3corUp.SetE(0.1396)
			    tauV3corDown.SetE(0.1396)
			MetVcor +=   tauV3 - tauV3cor
                        '''

                if  cat[2:] == 'tt'  or cat[2:] == 'mt' or cat[2:] == 'et' :
		    if e.gen_match_4 == 5 : 
			weightTID *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4)
			weightTIDUp *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Up')
			weightTIDDown *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4, unc='Down')

                        '''
			tauV4cor *= testool.getTES(e.pt_4, e.decayMode_4, e.gen_match_4)
			if e.decayMode_4 == 1 : 
			    e.m_4 =  0.1396  
			    tauV4cor.SetE(0.1396)
			MetVcor+=   tauV4 - tauV4cor
                        '''

                #if isW or isDY : print 'try', MetVcor.Pt(), MetV.Pt()

                #weight *= weightTID
                #weightFM *= weightTID * ww

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
	    if args.redoFit.lower() == 'yes' or args.redoFit.lower() == 'true' : 
                #for iv in inputSystematics :  
		#fastMTTmass, fastMTTtransverseMass = runSVFit(e, cat[2:], doJME, met, metphi) 
		fastMTTmass, fastMTTtransverseMass = runSVFit(e,tauV3cor, tauV4cor, MetVcor, cat[2:]) 
            else  : fastMTTmass, fastMTTtransverseMass = e.m_sv, e.mt_sv
	    #print 'new', fastMTTmass, 'old', e.m_sv, fastMTTtransverseMass, e.mt_sv, cat[2:]

            mass = 0.0005
            if cat[:2] == 'mm' : mass = .105
            L1.SetPtEtaPhiM(e.pt_1, e.eta_1,e.phi_1,mass)
            L2.SetPtEtaPhiM(e.pt_2, e.eta_2,e.phi_2,mass)
            ZPt = (L1+L2).Pt()

	    ewkweight = 1.
	    if  nickName == 'ZHToTauTau' :  
                ewkweight = FF.getEWKWeight(ZPt, "central")
                #print 'for signal---------------------->', nickName, ewkweight

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

                #if plotVar=='njets' or 'nbtag' in plotVar or 'jpt_' in plotVar or 'jeta_' in plotVar or 'bpt_' in plotVar or 'beta_' in plotVar or 'jphi' in plotVar or 'beta_' in plotVar or 'jphi_' in plotVar:  
                #    val=val[isys]

		if val is not None: 
                    try: 
			if hGroup != 'data' : 
			    if hGroup !='fakes' and hGroup !='f1' and hGroup != 'f2' and hGroup !='Reducible': 
				hMC[hGroup][cat][plotVar].Fill(val,weight)
				if not isfakemc1 and not isfakemc2 and tight1 and tight2: 
                                    hMCFM[hGroup][cat][plotVar].Fill(val,weight)
                                    hMCnof[hGroup][cat][plotVar].Fill(val,weight)

			    if hGroup =='fakes' or hGroup =='f1' or hGroup == 'f2' or hGroup=='Reducible':  hMCFM[hGroup][cat][plotVar].Fill(val,ww)

			else : 
			    if tight1 and tight2 : 
				hMC[hGroup][cat][plotVar].Fill(val,1)
				hMCFM[hGroup][cat][plotVar].Fill(val,1)
				hMCnof[hGroup][cat][plotVar].Fill(val,1)

                    except KeyError : continue

            #custom made variables

            tauV = tauV3cor + tauV4cor
	    #print fastMTTmass, 'm now==================', ZPt, cat

            H_LT = e.pt_3 + e.pt_4
            if fastMTTmass <290 : 
		if hGroup != 'data' : 
		    if hGroup !='fakes' and hGroup !='f1' and hGroup != 'f2' and hGroup !='Reducible': 

			hm_sv_new[hGroup][cat].Fill(fastMTTmass,weight )
			hmt_sv_new[hGroup][cat].Fill(fastMTTtransverseMass,weight )
			hH_LT[hGroup][cat].Fill(H_LT,weight )

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
			    #print fastMTTmass, 'm now==================', ZPt, cat

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
			#print fastMTTmass, 'm now==================', ZPt, cat, hGroup

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


		else : 
		    if tight1 and tight2 : 
			hmt_sv_new[hGroup][cat].Fill(fastMTTtransverseMass,1)
			hmt_sv_new_FM[hGroup][cat].Fill(fastMTTtransverseMass,1)

			hH_LT[hGroup][cat].Fill(H_LT,1)
			hH_LT_FM[hGroup][cat].Fill(H_LT,1)

			hm_sv_new_FM[hGroup][cat].Fill(fastMTTmass,1)
			hm_sv_new_FMext[hGroup][cat].Fill(fastMTTmass,1)
			hm_sv_new[hGroup][cat].Fill(fastMTTmass,1)

                        if fastMTTmass<50.01 and cat[:2]=='em' : print 'info, data iso', e.iso_3, 'ele_WP_3', e.Electron_mvaFall17V2noIso_WP90_3, '_4 =============> iso ', e.iso_4, 'isGlobal ', e.isGlobal_4, e.isTracker_4, 'ismedium', e.mediumId_4, 'tight', e.tightId_4,   e.lumi, e.run, e.evt, met

			if ZPt < 75 : 
			    hm_sv_newjA[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjA[hGroup][cat].Fill(fastMTTmass,1 )

			if ZPt>75 and ZPt < 150 : 
			    hm_sv_newjB[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjB[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,1)
				   
			if ZPt> 150 : 
			    hm_sv_newjC[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjC[hGroup][cat].Fill(fastMTTmass,1 )
			    hm_sv_new_FMjBC[hGroup][cat].Fill(fastMTTmass,1 )



            if group != 'data' : 
	        hLeptonW[group][cat].Fill(lepton_sf)
                hTriggerW[group][cat].Fill(trigw)
                    

	    nEvents += 1

        
	print("{0:30s} {1:7d} {2:10.6f} {3:5d}".format(nickName,nentries,sampleWeight[nickName],nEvents))
        
        inFile.Close()

htest={}

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
        hLeptonW[group][cat].Write()
        hTriggerW[group][cat].Write()

	OverFlow(hm_sv_newjA[group][cat])
	OverFlow(hm_sv_newjB[group][cat])
	OverFlow(hm_sv_newjC[group][cat])
	OverFlow(hm_sv_newjD[group][cat])

	OverFlow(hm_sv_new0jA[group][cat])
	OverFlow(hm_sv_new0jB[group][cat])
	OverFlow(hm_sv_new0jC[group][cat])
	OverFlow(hm_sv_new0jD[group][cat])

	OverFlow(hm_sv_new1jA[group][cat])
	OverFlow(hm_sv_new1jB[group][cat])
	OverFlow(hm_sv_new1jC[group][cat])
	OverFlow(hm_sv_new1jD[group][cat])

	OverFlow(hm_sv_new2jA[group][cat])
	OverFlow(hm_sv_new2jB[group][cat])
	OverFlow(hm_sv_new2jC[group][cat])
	OverFlow(hm_sv_new2jD[group][cat])


	OverFlow(hm_sv_new_jA[group][cat])
	OverFlow(hm_sv_new_jB[group][cat])
	OverFlow(hm_sv_new_jC[group][cat])

	OverFlow(hm_sv_new_FMjA[group][cat])
	OverFlow(hm_sv_new_FMjB[group][cat])
	OverFlow(hm_sv_new_FMjC[group][cat])
	OverFlow(hm_sv_new_FMjD[group][cat])

	OverFlow(hm_sv_new_FM0jA[group][cat])
	OverFlow(hm_sv_new_FM0jB[group][cat])
	OverFlow(hm_sv_new_FM0jC[group][cat])
	OverFlow(hm_sv_new_FM0jD[group][cat])

	OverFlow(hm_sv_new_FM1jA[group][cat])
	OverFlow(hm_sv_new_FM1jB[group][cat])
	OverFlow(hm_sv_new_FM1jC[group][cat])
	OverFlow(hm_sv_new_FM1jD[group][cat])

	OverFlow(hm_sv_new_FM2jA[group][cat])
	OverFlow(hm_sv_new_FM2jB[group][cat])
	OverFlow(hm_sv_new_FM2jC[group][cat])
	OverFlow(hm_sv_new_FM2jD[group][cat])
      
        
        hm_sv_newjA[group][cat].Write()
        hm_sv_newjB[group][cat].Write()
        hm_sv_newjC[group][cat].Write()
        hm_sv_newjD[group][cat].Write()
 

        hm_sv_new_jA[group][cat].Write()
        hm_sv_new_jB[group][cat].Write()
        hm_sv_new_jC[group][cat].Write()

        hm_sv_new0jA[group][cat].Write()
        hm_sv_new0jB[group][cat].Write()
        hm_sv_new0jC[group][cat].Write()
        hm_sv_new0jD[group][cat].Write()

        hm_sv_new1jA[group][cat].Write()
        hm_sv_new1jB[group][cat].Write()
        hm_sv_new1jC[group][cat].Write()
        hm_sv_new1jD[group][cat].Write()
 

        hm_sv_new2jA[group][cat].Write()
        hm_sv_new2jB[group][cat].Write()
        hm_sv_new2jC[group][cat].Write()
        hm_sv_new2jD[group][cat].Write()


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


            hm_sv_new_jall[group][cat].SetBinContent(i,hm_sv_new_jA[group][cat].GetBinContent(i))
            hm_sv_new_jall[group][cat].SetBinContent(i+10,hm_sv_new_jB[group][cat].GetBinContent(i))
            hm_sv_new_jall[group][cat].SetBinContent(i+20,hm_sv_new_jC[group][cat].GetBinContent(i))
            hm_sv_new_jall[group][cat].SetBinError(i,hm_sv_new_jA[group][cat].GetBinError(i))
            hm_sv_new_jall[group][cat].SetBinError(i+10,hm_sv_new_jB[group][cat].GetBinError(i))
            hm_sv_new_jall[group][cat].SetBinError(i+20,hm_sv_new_jC[group][cat].GetBinError(i))

        hm_sv_new_FMjall[group][cat].Write()
        hm_sv_new_FMjallv2[group][cat].Write()
        hm_sv_new_jall[group][cat].Write()

        hm_sv_new_FMjA[group][cat].Write()
        hm_sv_new_FMjB[group][cat].Write()
        hm_sv_new_FMjC[group][cat].Write()
        hm_sv_new_FMjD[group][cat].Write()
        hm_sv_new_FMjBC[group][cat].Write()



        hm_sv_new_FM0jA[group][cat].Write()
        hm_sv_new_FM0jB[group][cat].Write()
        hm_sv_new_FM0jC[group][cat].Write()
        hm_sv_new_FM0jD[group][cat].Write()

        hm_sv_new_FM1jA[group][cat].Write()
        hm_sv_new_FM1jB[group][cat].Write()
        hm_sv_new_FM1jC[group][cat].Write()
        hm_sv_new_FM1jD[group][cat].Write()


        hm_sv_new_FM2jA[group][cat].Write()
        hm_sv_new_FM2jB[group][cat].Write()
        hm_sv_new_FM2jC[group][cat].Write()
        hm_sv_new_FM2jD[group][cat].Write()




        '''
        for hn in hnames :
            hnn=hn.replace('hm_','m_')
	    for jj in jm:
		for rr in reg:
		    str_='{0:s}{1:s}{2:s}[3:s][4:s]'.format(hn,str(jj), rr,group,cat)
		    
	            hName = 'h{0:s}_{1:s}_{2:s}{3:s}{4:s}'.format(group,cat, hnn, str(jj),rr)
                    OverFlow(str_)
                    str_.Write()

        '''


        for plotVar in plotSettings:
            OverFlow(hMC[group][cat][plotVar])
            OverFlow(hMCnof[group][cat][plotVar])
	    #if 'gen_match' not in plotVar and 'CutFlow' not in plotVar and 'iso' not in plotVar: 
            #    hMC[group][cat][plotVar].Rebin(2)
            #    hMCFM[group][cat][plotVar].Rebin(2)
            hMC[group][cat][plotVar].Write()
            hMCnof[group][cat][plotVar].Write()
            OverFlow(hMCFM[group][cat][plotVar])
            hMCFM[group][cat][plotVar].Write()
    htest.Write()

for cat in cats.values():
    print("Duplicate summary for {0:s}".format(cat))
    DD[cat].printSummary()
    


