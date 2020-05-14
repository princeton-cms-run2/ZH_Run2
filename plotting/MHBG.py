#
# read MC file root files and histogram by group 
#

from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector
import ROOT 
from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
import os
from math import sin, cos 

import ScaleFactor as SF

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    parser.add_argument("-l","--LTcut",default=0.,type=float,help="H_LTcut")
    parser.add_argument("-s","--sign",default='OS',help="Opposite or same sign (OS or SS).")
    parser.add_argument("-a","--analysis",default='AZH',help="Type of analysis ZH or AZH") 
    parser.add_argument("--MConly",action='store_true',help="MC only") 
    parser.add_argument("--looseCuts",action='store_true',help="Loose cuts")
    parser.add_argument("--unBlind",action='store_true',help="Unblind signal region for OS")
    parser.add_argument("--tauIDSF",action='store_false',help="Disable tauID SF correction.") 
    parser.add_argument("-r", "--redoFit",action='store_true',help="redo FastMTT and adjust MET after to Tau ES corrections")
    
    return parser.parse_args()

class dupeDetector() :
    
    def __init__(self):
        self.nCalls = 0 
        self.runEventList = []

    def checkEvent(self,entry) :
        self.nCalls += 1 
        runEvent = "{0:d}:{1:d}".format(entry.run,entry.evt)
        if runEvent in self.runEventList :
            #print("Event in list: runEventList={0:s}".format(str(self.runEventList)))
            return True
        else :
            self.runEventList.append(runEvent)
            #print("New event: runEventList={0:s}".format(str(self.runEventList)))
            return False

    def printSummary(self) :
        print("Duplicate Event Summary: Calls={0:d} Unique Events={1:d}".format(self.nCalls,len(self.runEventList)))
        return

def getFakeWeights(f1,f2) :
    w1 = f1/(1.-f1)
    w2 = f2/(1.-f2)
    w0 = w1*w2
    return w1, w2, w0

def printTrigger(e, year) :

    # electron trigger
    print("\ncat={0:s} isTrig_1={1:.1f} isTrig_2={2:.1f} isDoubleTrig={3:.1f}".format(cats[e.cat],e.isTrig_1,e.isTrig_2,e.isDoubleTrig))
    trigs = ['SE35','SE32','SE27','SE25','DE23_12','DE23_12b']
    txt = ''
    for i in range(len(trigs)) : txt += "{0:s}={1} ".format(trigs[i],(e.electronTriggerWord & 2**i) > 0) 
    print("ElectronTriggerWord={0:04x} Trigs: {1:s}".format(e.electronTriggerWord,txt))

    trigs = ['SM27','SM24','SM24Tk','','','','','','DM17_8','DM17_8b','DM17_8c','DM17_8Tk','DM17_8Tkb']
    txt = ''
    for i in range(len(trigs)) :
        if len(trigs[i]) > 1 : txt += "{0:s}={1} ".format(trigs[i],(e.muonTriggerWord & 2**i) > 0)
    print("    MuonTriggerWord={0:04x} Trigs: {1:s}".format(e.muonTriggerWord,txt))

def runSVFit(entry, channel, tau1, tau2 ) :
                      
    measuredMETx = entry.met*cos(entry.metphi)
    measuredMETy = entry.met*sin(entry.metphi)

    #define MET covariance
    covMET = ROOT.TMatrixD(2,2)
    covMET[0][0] = entry.metcov00
    covMET[1][0] = entry.metcov10
    covMET[0][1] = entry.metcov01
    covMET[1][1] = entry.metcov11

    kUndefinedDecayType, kTauToHadDecay,  kTauToElecDecay, kTauToMuDecay = 0, 1, 2, 3    
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

# calculate corrected di-tau mass 
def getTEScorrectedMass(e, cat, testool,unc=None) :
    # no correction for em mode 
    if cat[2:] == 'em' : return e.m_sv 
    tauV3, tauV4= TLorentzVector(), TLorentzVector()
    tauV3.SetPtEtaPhiM(e.pt_3, e.eta_3, e.phi_3, e.m_3)
    tauV4.SetPtEtaPhiM(e.pt_4, e.eta_4, e.phi_4, e.m_4)
    if cat[2] == 't' : tauV3 *= testool.getTES(e.pt_3,e.decayMode_3,e.gen_match_3)
    tauV4 *= testool.getTES(e.pt_4,e.decayMode_4,e.gen_match_4)
    Mfit, MtFit = runSVFit(e, cat[2:], tauV3, tauV4) 
    return Mfit
    
args = getArgs()
era=str(args.year)

lumi = {'2016':1000.*35.92,'2017':1000.*41.53,'2018':1000.*59.74}
tightCuts = not args.looseCuts
dataDriven = not args.MConly

nBins, xMin, xMax = 10, 0., 200.
groups = ['Signal','Reducible','Rare','ZZ','data']

cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem', 9:'et', 10:'mt', 11:'tt' }

# use this utility class to screen out duplicate events
DD = {}
for cat in cats.values() :
    DD[cat] = dupeDetector()

# dictionary where the group is the key
hMtt, hLT, hPt1, hESratio, hCutFlow = {}, {}, {}, {}, {}

# set up tauID Scale Factor (SF) tool
campaign = {2016:'2016Legacy', 2017:'2017ReReco', 2018:'2018ReReco'} 
tauSFTool = TauIDSFTool(campaign[args.year],'DeepTau2017v2p1VSjet','Medium')
antiEleSFTool = TauIDSFTool(campaign[args.year],'antiEleMVA6','Loose')
antiMuSFTool  = TauIDSFTool(campaign[args.year],'antiMu3','Tight')

# set up the tau energy scale by year
testool = TauESTool(campaign[args.year])    # properly IDed taus
festool = TauESTool(campaign[args.year])    # wrongly IDed taus 

# set up the trigger SF tool

muName = {2016:'SingleMuon_Run2016_IsoMu24orIsoMu27.root',2017:'SingleMuon_Run2017_IsoMu24orIsoMu27.root',
          2018:'SingleMuon_Run2018_IsoMu24orIsoMu27.root' }

eName = { 2016:'SingleElectron_Run2016_Ele25orEle27.root', 2017:'SingleElectron_Run2017_Ele32orEle35.root',
          2018:'SingleElectron_Run2018_Ele32orEle35.root'}
          
TriggerSF = {'dir' : '../tools/ScaleFactors/TriggerEffs/', 'fileMuon' : 'Muon/{0:s}'.format(muName[args.year]),
           'fileElectron' : 'Electron/{0:s}'.format(eName[args.year]) }

sf_MuonTrig = SF.SFs()
sf_MuonTrig.ScaleFactor("{0:s}{1:s}".format(TriggerSF['dir'],TriggerSF['fileMuon']))
sf_EleTrig = SF.SFs()
sf_EleTrig.ScaleFactor("{0:s}{1:s}".format(TriggerSF['dir'],TriggerSF['fileElectron']))

# setup FastMtt stuff 
for baseName in ['MeasuredTauLepton','svFitAuxFunctions','FastMTT'] : 
    if os.path.isfile("{0:s}_cc.so".format(baseName)) :
        ROOT.gInterpreter.ProcessLine(".L {0:s}_cc.so".format(baseName))
    else :
        ROOT.gInterpreter.ProcessLine(".L {0:s}.cc++".format(baseName))   
        # .L is not just for .so files, also .cc
                
# dictionary where the nickName is the key
nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}

for group in groups :
    nickNames[group] = []

#       0                 1       2        3        4        5            6
# GluGluHToTauTau	Signal	48.58	9259000	198813970.4	 	/GluGluHToTauTau_...

# make a first pass to get the weights
csvFile = '../MC/MCsamples_{0:s}_{1:s}.csv'.format(era,args.analysis)
print("csvFile={0:s}".format(csvFile))
for line in open(csvFile,'r').readlines() :
    #print("line={0:s}".format(line.strip()))
    vals = line.split(',')
    #print("vals={0:s}".format(str(vals)))
    if vals[5].lower() == 'ignore' :
        print("Skipping line={0:s}".format(line.strip()[0:40]))
        continue 
    nickName = vals[0]
    group = vals[1]
    #print("nickName={0:s} group={1:s}".format(nickName,group))
    nickNames[group].append(nickName) 
    xsec[nickName] = float(vals[2])
    totalWeight[nickName] = float(vals[4])
    sampleWeight[nickName]= lumi[era]*xsec[nickName]/totalWeight[nickName]
    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

# Stitch the DYJets and WJets samples

for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i) 
    sampleWeight[nn] = lumi[era]/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + totalWeight[nn]/xsec[nn])

for i in range(1,4) :
    nn = 'W{0:d}JetsToLNu'.format(i)
    print("nn={0:s}".format(nn))
    sampleWeight[nn] = lumi[era]/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + totalWeight[nn]/xsec[nn])
    
# now add the data
nickName = '../data/condor/{0:s}/{1:s}/{1:s}_data.root'.format(args.analysis,era)
totalWeight[nickName] = 1.
sampleWeight[nickName] = 1.
nickNames['data'].append(nickName) 

print("tightCuts={0}".format(tightCuts))
if tightCuts :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut))
    if args.MConly :
        print("args.MConly is TRUE")
        outFileName = outFileName.replace('.root','_MC.root') 
else :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_loose.root'.format(args.year,args.sign,int(args.LTcut))
    
print("Opening {0:s} as output.".format(outFileName))
fOut = TFile( outFileName, 'recreate' )

#fe, fm, ft_et, ft_mt, f1_tt, f2_tt   = 0.0456, 0.0935, 0.1391, 0.1284, 0.0715, 0.0609
# values with nbtag = 0 cut 
fe, fm, ft_et, ft_mt, f1_tt, f2_tt   = 0.0390, 0.0794, 0.1397, 0.1177, 0.0756, 0.0613
fW1, fW2, fW0 = {}, {}, {}
fW1['et'], fW2['et'], fW0['et'] = getFakeWeights(fe,ft_et)
fW1['mt'], fW2['mt'], fW0['mt'] = getFakeWeights(fm,ft_mt)
fW1['tt'], fW2['tt'], fW0['tt'] = getFakeWeights(f1_tt,f2_tt)
fW1['em'], fW2['em'], fW0['em'] = getFakeWeights(fe,fm)

print("\n  Group           Nickname                  Entries    Wt/Evt  Ngood   Tot Wt")

#for group in ['Signal','ZZ','data']  :
for group in groups : 
    fOut.cd()
    hMtt[group], hLT[group], hPt1[group], hESratio[group], hCutFlow[group] = {}, {}, {}, {}, {}
    for cat in cats.values()[0:8] :
        hName1 = 'h{0:s}_{1:s}_Mtt'.format(group,cat)
        hMtt[group][cat] = TH1D(hName1,hName1,nBins,xMin,xMax)
        hName2 = 'h{0:s}_{1:s}_LT'.format(group,cat)
        hLT[group][cat] = TH1D(hName2,hName2,nBins,xMin,xMax)
        hName3 = 'h{0:s}_{1:s}_Pt1'.format(group,cat)
        hPt1[group][cat] = TH1D(hName3,hName3,nBins,xMin,xMax)
        hName4 = 'h{0:s}_{1:s}_ESratio'.format(group,cat)
        hESratio[group][cat] = TH1D(hName4,hName4,200,0.9,1.1)
        hName5 = 'h{0:s}_{1:s}_cutflow'.format(group,cat)
        hCutFlow[group][cat] = TH1D(hName5,hName5,20,0.,20.) 
        
    #print("\nGroup: {0:s}\n      Nickname                 Entries    Wt/Evt  Ngood   Tot Wt".format(group))
    for nickName in nickNames[group] :
        #print("nickName={0:s}".format(nickName))
        isData = False 
        inFileName = '../MC/condor/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.analysis,nickName,era)
        if group == 'data' :
            isData = True
            inFileName = '../data/condor/{0:s}/{1:s}/{1:s}_data.root'.format(args.analysis,era) 
        try :
            inFile = TFile.Open(inFileName)
            inFile.cd()
            inTree = inFile.Get("Events")
            nentries = inTree.GetEntries()
        except AttributeError :
            print("  Failure on file {0:s}".format(inFileName))
            exit()

        nEvents, trigw, totalWeight = 0, 1., 0.
        sWeight = sampleWeight[nickName]
        DYJets = (nickName == 'DYJetsToLL')
        WJets  = (nickName == 'WJetsToLNu')

        for i, e in enumerate(inTree) :
            #if group != 'ZZ' : continue
            hGroup = group
            sw = sWeight
            if e.LHE_Njets > 0 :
                if DYJets : sw = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
                if WJets  : sw = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)] 

            if group == 'data' :
                ww = 1.
            else :
                weight = e.weightPUtrue * e.Generator_weight * sw 
                ww = weight
                
            if group == 'Signal' : ww *= 10.

            cat = cats[e.cat]
            hCutFlow[group][cat].Fill(0.5) 

            #print("New event cat={0:s} nbtag={1}".format(cat,e.nbtag)) 
            if tightCuts :
                if args.sign == 'SS':
                    if e.q_3*e.q_4 < 0. : continue
                else :
                    if e.q_3*e.q_4 > 0. : continue

                hCutFlow[group][cat].Fill(1.5)
                hCutFlow[group][cat].Fill(2.5,ww)
                
                try :
                    if e.nbtag[0] > 0 : continue
                except TypeError :
                    if e.nbtag > 0 : continue

                hCutFlow[group][cat].Fill(3.5,ww)
                
	        if cat[:2] == 'mm' :
                    if (e.iso_1 > 0.2 or e.iso_2 > 0.2) : continue
                    if (e.isGlobal_1 < 1 and e.isTracker_1 < 1) : continue
                    if (e.isGlobal_2 < 1 and e.isTracker_2 < 1) : continue
                    
	        if cat[:2] == 'ee' and  (e.iso_1 > 0.15 or e.iso_2 > 0.15) : continue

                hCutFlow[group][cat].Fill(4.5,ww) 

                if cat[2:] == 'em'  :
                    tight1 = e.iso_3 < 0.15 and e.Electron_mvaFall17V2noIso_WP90_3 > 0 
                    tight2 = e.iso_4 < 0.2 and e.isGlobal_4 > 0 and e.isTracker_4 > 0

                    # use Alexis's cuts 
                    tight1, tight2 = True, True
                    if  (e.isGlobal_4 < 1 and e.isTracker_4 < 1) : tight2 = False
                    #if e.iso_4 > 0.20 or e.tightId_4 < 1 : tight2 = False
                    if e.iso_4 > 0.20 : tight2 = False
	            if e.Electron_mvaFall17V2noIso_WP90_3 < 1 or e.iso_3 > 0.15 : tight1 = False

                    
	        if cat[2:] == 'mt' :
                    tight1 = e.iso_3 < 0.2 and e.isGlobal_3 > 0 and e.isTracker_3 > 0
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >= 15 and e.idDeepTau2017v2p1VSmu_4 >= 0 and  e.idDeepTau2017v2p1VSe_4 >= 0
	        if cat[2:] == 'et':
                    tight1 = e.iso_3 < 0.15 and e.Electron_mvaFall17V2noIso_WP90_3 > 0 
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >= 15 and e.idDeepTau2017v2p1VSmu_4 >= 0 and  e.idDeepTau2017v2p1VSe_4 >= 0
                if cat[2:] == 'tt' :
                    tight1 = e.idDeepTau2017v2p1VSjet_3 >= 15 and e.idDeepTau2017v2p1VSmu_3 >= 0 and  e.idDeepTau2017v2p1VSe_3 >= 0
                    tight2 = e.idDeepTau2017v2p1VSjet_4 >= 15 and e.idDeepTau2017v2p1VSmu_4 >= 0 and  e.idDeepTau2017v2p1VSe_4 >= 0
                
                if tight1 and tight2 : hCutFlow[group][cat].Fill(5.5,ww)

                if group == 'data' :
                    ww = 1. 
                    if dataDriven :
                        hGroup = 'Reducible'
                        if not tight1 and tight2 : ww = fW1[cat[2:]]
                        elif tight1 and not tight2 : ww = fW2[cat[2:]]
                        elif not (tight1 or tight2) : ww = -fW0[cat[2:]]
                        else :
                            ww = 1.
                            hGroup = 'data'
                    else :
                        hGroup = 'data'
                        if not (tight1 and tight2) : continue
                else : 
                    #print("Good MC event: group={0:s} nickName={1:s} cat={2:s} gen_match_1={3:d} gen_match_2={4:d}".format(
                    #    group,nickName,cat,e.gen_match_1,e.gen_match_2))
                    if not (tight1 and tight2) : continue
                    if dataDriven :   # include only events with MC matching
                        if cat[2:] == 'em'  :
                            if not(e.gen_match_3 == 15) : continue
                            if not(e.gen_match_4 == 15) : continue
                            
	                if cat[2:] == 'et' or cat[2:] == 'mt' :
                            #print("    et or mt: gen_match_3={0:d} gen_match_4={1:d}".format(e.gen_match_3,e.gen_match_4)) 
                            if not(e.gen_match_3 == 15) : continue
                            if e.gen_match_4 > 5  : continue
                            if (group == 'Reducible') and not(e.gen_match_4 == 5) : continue 
                            # TauID Scalefactor Corrections
                            if args.tauIDSF :
                                ww *= tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4)
                                if e.gen_match_4 == 1 or e.gen_match_4 == 3 : ww *= antiEleSFTool.getSFvsEta(e.eta_4,e.gen_match_4)
                                if e.gen_match_4 == 2 or e.gen_match_4 == 4 : ww *=  antiMuSFTool.getSFvsEta(e.eta_4,e.gen_match_4)
                            
                        if cat[2:] == 'tt' :
                            if e.gen_match_3 > 5 : continue
                            if e.gen_match_4 > 5 : continue

                            if (group == 'Reducible') and not(e.gen_match_3 == 5 or e.gen_match_4 == 5) : continue
                            hCutFlow[group][cat].Fill(6.5,ww)
                            
                            # TauID Scalefactor Corrections
                            if args.tauIDSF :
                                ww *= tauSFTool.getSFvsPT(e.pt_3,e.gen_match_3)*tauSFTool.getSFvsPT(e.pt_4,e.gen_match_4)
                                if e.gen_match_3 == 1 or e.gen_match_3 == 3 : ww *= antiEleSFTool.getSFvsEta(e.eta_3,e.gen_match_3)
                                if e.gen_match_3 == 2 or e.gen_match_3 == 4 : ww *=  antiMuSFTool.getSFvsEta(e.eta_3,e.gen_match_3)
                                if e.gen_match_4 == 1 or e.gen_match_4 == 3 : ww *= antiEleSFTool.getSFvsEta(e.eta_4,e.gen_match_4)
                                if e.gen_match_4 == 2 or e.gen_match_4 == 4 : ww *=  antiMuSFTool.getSFvsEta(e.eta_4,e.gen_match_4)

                            hCutFlow[group][cat].Fill(7.5,ww)
                            
            #hCutFlow[group][cat].Fill(6.5,ww)

            #goodTrig = e.isTrig_1 != 0 # or e.isDoubleTrig != 0
            mask = 0xF
            #mask = 0xFFF
            if False :
                goodTrig = (cat[0:2] == 'ee') and (e.electronTriggerWord & mask > 0)
                goodTrig = goodTrig or ((cat[0:2] == 'mm') and (e.muonTriggerWord & mask  > 0))
            else :
                goodTrig = True

            #print("    goodTrig={0}".format(goodTrig))
            if False :
                if cat[:2] == 'mm' :                
		    eff_trig_d_1 =  sf_MuonTrig.get_EfficiencyData(e.pt_1,e.eta_1)
		    eff_trig_mc_1 =  sf_MuonTrig.get_EfficiencyMC(e.pt_1,e.eta_1)

	        if cat[:2] == 'ee' :                 
		    eff_trig_d_1 =  sf_EleTrig.get_EfficiencyData(e.pt_1,e.eta_1)
		    eff_trig_mc_1 =  sf_EleTrig.get_EfficiencyMC(e.pt_1,e.eta_1)

                if group != 'data' and eff_trig_mc_1 !=0 : ww *= float(eff_trig_d_1/eff_trig_mc_1)
                
            if not goodTrig :
                #if group == 'data' : printTrigger(e,2016) 
                continue
                
            H_LT = e.pt_3 + e.pt_4
            if H_LT < args.LTcut : continue

            m_sv = e.m_sv
            if group == 'data' :
                if DD[cat].checkEvent(e) : continue
            else :
                # this is the correction factor to be applied to the di-Tau mass 
                if args.redoFit :
                    m_sv = getTEScorrectedMass(e,cat,testool) 
                    #print("m_sv: before={0:.3f} after={1:.3f}".format(e.m_sv,m_sv))

            #hCutFlow[group][cat].Fill(6.5,ww)
            
            if cat == 'mmtt' :
                totalWeight += ww
                nEvents += 1

            if args.sign == 'SS' or hGroup != 'data' or args.looseCuts or e.m_sv < 80. or e.m_sv > 140. or args.unBlind:
                try :
                    hMtt[hGroup][cat].Fill(m_sv,ww)
                    hESratio[hGroup][cat].Fill(m_sv/e.m_sv)
                except KeyError : pass

            try :
                hLT[hGroup][cat].Fill(H_LT,ww)
                hPt1[hGroup][cat].Fill(e.pt_1,ww)
                if False and hGroup == 'data' :
                    printTrigger(e,args.year)
            except KeyError : pass 
            
        print("{0:12s} {1:30s} {2:7d} {3:10.6f} {4:5d} {5:8.3f}".format(
            group,nickName,nentries,sampleWeight[nickName],nEvents,totalWeight))
        inFile.Close()
    fOut.cd()
    for cat in cats.values()[0:6] :
        hMtt[group][cat].Write()
        hLT[group][cat].Write() 

for cat in cats.values():
    print("Duplicate summary for {0:s}".format(cat))
    DD[cat].printSummary()
    
fOut.cd()
fOut.Write()
fOut.Close()        


