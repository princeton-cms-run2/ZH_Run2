#!/usr/bin/env python

""" ZH.py: makes an nTuple for the ZH->tautau analysis """

__author__ = "Dan Marlow, Alexis Kalogeropoulos, Gage DeZoort" 
__version__ = "GageDev_v1.1"

# import external modules 
import sys
import numpy as np
from ROOT import TFile, TTree, TH1, TH1D, TCanvas, TLorentzVector  
from math import sqrt, pi

# import from ZH_Run2/funcs/
sys.path.insert(1,'../funcs/')
import tauFun
import generalFunctions as GF 
import outTuple
import time

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='ZHtoTauTau_test.root',help="File to be analyzed.")
    #parser.add_argument("-f","--inFileName",default='DY1JetsToLL_test.root',help="File to be analyzed.")
    parser.add_argument("-c","--category",default='none',help="Event category to analyze.")
    parser.add_argument("--nickName",default='',help="MC sample nickname") 
    parser.add_argument("-d","--dataType",default='MC',help="Data or MC") 
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    parser.add_argument("-m","--maxPrint",default=0,type=int,help="Maximum number of events to print.")
    parser.add_argument("-t","--testMode",default='',help="tau MVA selection")
    parser.add_argument("-y","--year",default=2017,type=int,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-l","--flavour",default='ZH',help="is this for the ZH or the AZH analysis?")
    parser.add_argument("-w","--weights",default=False,type=int,help="to re-estimate Sum of Weights")
    
    return parser.parse_args()

def ZHDR(entry,Lep,jt) :
    phi1, eta1 = Lep.Phi(), Lep.Eta()
    try :
        phi2, eta2 = entry.Tau_phi[jt], entry.Tau_eta[jt]
    except IndexError :
        print("In ZHDR: IndexError:  jt={0:d} nTau={1:d} event={2:d}".format(jt,entry.nTau,entry.event))
        return 0.
    
    dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
    return sqrt(dPhi**2 + (eta2-eta1)**2)

def getEventDictionary(fileName) :
    eventDict = {}
    for line in open(fileName,'r').readlines() :
        vals = line.split() 
        eventDict[int(vals[0])] = [float(vals[1]),float(vals[2]),float(vals[3]),float(vals[4]),float(vals[5]),float(vals[6])]
    return eventDict

def tausInList(entry,event) :
    nMatch = 0
    for i in range(2) :
        eta1, phi1 = event[1+2*i], event[2+2*i]
        for j in range(entry.nTau) :
            phi2, eta2 = entry.Tau_phi[j], entry.Tau_eta[j]
            dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
            DR = sqrt(dPhi**2 + (eta2-eta1)**2)
            if DR < 0.1 :
                nMatch += 1
                if nMatch > 1 : return True
                continue
    return False

def goodTyler(entry, tylerListAll, tylerListnanoAOD) :
    if not entry.event in tylerListAll.keys() : return False
    if entry.event in tylerListnanoAOD.keys() : return True
    return tausInList(entry,tylerListAll[entry.event]) 
    
args = getArgs()
print("args={0:s}".format(str(args)))
maxPrint = args.maxPrint 

cutCounter = {}


if args.category != 'none' :
    cats = [args.category]
else :
    cats = ['eeet','eemt','eett','eeem','mmet','mmmt','mmtt','mmem']

for cat in cats : cutCounter[cat] = GF.cutCounter()

inFileName = args.inFileName
print("Opening {0:s} as input.  Event category {1:s}".format(inFileName,cat))

isAZH=False
if str(args.flavour) == 'AZH' : isAZH = True
if isAZH : print 'You are running on the AZH mode !!!'

inFile = TFile.Open(inFileName)
inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
nMax = nentries
print("nentries={0:d} nMax={1:d}".format(nentries,nMax))
if args.nEvents > 0 : nMax = min(args.nEvents-1,nentries)


MC = len(args.nickName) > 0 
if args.dataType != 'Data' and args.dataType != 'data' : MC = True
if args.dataType == 'MC' or args.dataType == 'mc' : MC = True

if MC :
    print "this is MC, will get PU etc"
    PU = GF.pileUpWeight()
    PU.calculateWeights(args.nickName,args.year)
else :
    print "Will run on Data...."
    CJ = GF.checkJSON(filein='Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt')
    if args.year== '2016' : CJ = GF.checkJSON(filein='Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt')
    if args.year== '2017' : CJ = GF.checkJSON(filein='Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt')
    if args.year== '2018' : CJ = GF.checkJSON(filein='Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt')


era=str(args.year)

outFileName = GF.getOutFileName(args).replace(".root",".ntup")

if args.weights > 0 :
    hWeight = TH1D("hWeights","hWeights",1,-0.5,0.5)
    hWeight.Sumw2()

    for count, e in enumerate(inTree) :
        hWeight.Fill(0, e.genWeight)
    
    fName = GF.getOutFileName(args).replace(".root",".weights")
    fW = TFile( fName, 'recreate' )
    print 'Will be saving the Weights in', fName
    fW.cd()
    hWeight.Write()

#############end weights

print("Opening {0:s} as output.".format(outFileName))
outTuple = outTuple.outTuple(outFileName, era)


tStart = time.time()
countMod = 1000
isMC = True
for count, e in enumerate(inTree) :
    for cat in cats : cutCounter[cat].count('All')
    if count % countMod == 0 :
        print("Count={0:d}".format(count))
        if count >= 10000 : countMod = 10000
    if count == nMax : break

    for lepMode in ['ee','mm'] :

        if e.nTau < 1 : continue 
        if lepMode == 'ee' :
            if e.nElectron < 2 : continue
            for cat in cats[:4] : cutCounter[cat].count('LeptonCount')
        if lepMode == 'mm' :
            if e.nMuon < 2 : continue 
            for cat in cats[4:] : cutCounter[cat].count('LeptonCount')

        goodElectronList = tauFun.makeGoodElectronList(e, isAZH)
        goodMuonList = tauFun.makeGoodMuonList(e, isAZH)
        if not isAZH : goodElectronList, goodMuonList = tauFun.eliminateCloseLeptons(e, goodElectronList, goodMuonList)
        if isAZH and lepMode == 'ee' and len(goodElectronList) > 2 : continue 
        if isAZH and lepMode == 'mm' and len(goodMuonList) > 2 : continue 

	lepList=[]

        
        if lepMode == 'ee' :
            if args.year == '2016' and not e.HLT_Ele27_eta2p1_WPTight_Gsf and not e.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ : continue
            if (args.year == '2017' or args.year == '2018') and not e.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ and not e.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL and not e.HLT_Ele35_WPTight_Gsf and not e.HLT_Ele32_WPTight_Gsf: continue

            if len(goodElectronList) < 2 :  continue
            pairList, lepList = tauFun.findZ(goodElectronList,[], e)
            #protect from the case that you dont get back 2 leptons
            if len(lepList) != 2 : continue
            for cat in cats[:4] : cutCounter[cat].count('Trigger')
        
        if lepMode == 'mm' :
            if args.year == '2016' and not e.HLT_IsoMu24 and not e.HLT_IsoTkMu24 and not e.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ and not e.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ: continue
            if (args.year == '2017' or args.year == '2018') and not e.HLT_IsoMu24  and not e.HLT_IsoMu27 and not e.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 and not e.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mas3s8 : continue


            if len(goodMuonList) < 2 : continue
            pairList, lepList = tauFun.findZ([],goodMuonList, e)
            if len(lepList) != 2 : continue
    	    for cat in cats[4:] : cutCounter[cat].count('Trigger')
        
        if len(pairList) < 1 : continue
        if lepMode == 'ee' :
            for cat in cats[:4]: cutCounter[cat].count('LeptonPair')
        if lepMode == 'mm' :
            for cat in cats[4:]: cutCounter[cat].count('LeptonPair')
   
        LepP, LepM = pairList[0], pairList[1]
        M = (LepM + LepP).M()
        if M < 60. or M > 120. : continue ##cut valid for both AZH and ZH
        if lepMode == 'ee' :
            for cat in cats[:4]: cutCounter[cat].count('FoundZ')
        if lepMode == 'mm' :
            for cat in cats[4:]: cutCounter[cat].count('FoundZ')
        
        for tauMode in ['et','mt','tt','em'] :
            cat = lepMode + tauMode
            if tauMode == 'tt' :
                if not isAZH : tauList = tauFun.getTauList(cat, e, pairList=pairList)
                if isAZH : tauList = tauFun.getTauListAZH(cat, e, pairList=pairList)
                bestTauPair = tauFun.getBestTauPair(cat, e, tauList )
                                    
            elif tauMode == 'et' :
                bestTauPair = tauFun.getBestETauPair(e,cat=cat,pairList=pairList)
            elif tauMode == 'mt' :
                bestTauPair = tauFun.getBestMuTauPair(e,cat=cat,pairList=pairList)
            elif tauMode == 'em' :
                bestTauPair = tauFun.getBestEMuTauPair(e,cat=cat,pairList=pairList)
		
            if len(bestTauPair) < 1 :
                if False and maxPrint > 0 and (tauMode == GF.eventID(e)[2:4]) :
                    maxPrint -= 1
                    print("Failed tau-pair cut")
                    print("Event ID={0:s} cat={1:s}".format(GF.eventID(e),cat))
                    print("goodMuonList={0:s} goodElectronList={1:s} Mll={3:.1f} bestTauPair={4:s}".format(
                        str(goodMuonList),str(goodElectronList),str(pairList),M,str(bestTauPair)))
                    print("Lep1.pt() = {0:.1f} Lep2.pt={1:.1f}".format(pairList[0].Pt(),pairList[1].Pt()))
                    GF.printEvent(e)
                    GF.printMC(e)
                continue

            cutCounter[cat].count("GoodTauPair")

            if tauMode == 'tt' and args.testMode.lower() == "vvtight" :
                j1, j2 = bestTauPair[0], bestTauPair[1]
                if ord(e.Tau_idMVAnewDM2017v2[j1]) < 64 : continue
                if ord(e.Tau_idMVAnewDM2017v2[j2]) < 64 : continue

            cutCounter[cat].count("VVtightTauPair")

            if len(bestTauPair) > 1 :
                jt1, jt2 = bestTauPair[0], bestTauPair[1]
            else :
                continue
	    #print  lepList[0], lepList[1], LepP.Pt(), LepM.Pt(), bestTauPair[0],bestTauPair[1],cat

            if MC :
                outTuple.setWeight(PU.getWeight(e.Pileup_nPU)) ## we store the GenWeight * PUweight ?
	    else :
                isInJSON = CJ.checkJSON(e.luminosityBlock,e.run)
                if not isInJSON :
                    print("Event not in JSON: Run:{0:d} LS:{1:d}".format(e.run,e.luminosityBlock))
                    continue
                cutCounter[cat].count("InJSON")
                        
            SVFit = True
	    
            if not MC : isMC = False
            outTuple.Fill(e,SVFit,cat,jt1,jt2,LepP,LepM,lepList,isMC,era) 

            if maxPrint > 0 :
                maxPrint -= 1
                print("\n\nGood Event={0:d} cat={1:s}  MCcat={2:s}".format(e.event,cat,GF.eventID(e)))
                print("goodMuonList={0:s} goodElectronList={1:s} Mll={2:.1f} bestTauPair={3:s}".format(
                    str(goodMuonList),str(goodElectronList),M,str(bestTauPair)))
                print("Lep1.pt() = {0:.1f} Lep2.pt={1:.1f}".format(pairList[0].Pt(),pairList[1].Pt()))
                GF.printEvent(e)
                print("Event ID={0:s} cat={1:s}".format(GF.eventID(e),cat))
                

dT = time.time() - tStart
print("Run time={0:.2f} s  time/event={1:.1f} us".format(dT,1000000.*dT/count))



hCutFlow=[]
countt=0
for cat in cats :
    print('\nSummary for {0:s}'.format(cat))
    cutCounter[cat].printSummary()
    hName="hCutFlow_"+str(cat)
    #print '======================', hName
    #count
    hCutFlow.append( TH1D(hName,hName,10,0.5,10.5))
    lcount=len(cutCounter[cat].getYield())
    for i in range(lcount) :
        #hCutFlow[cat].Fill(1, float(cutCounter[cat].getYield()[i]))
        yields = cutCounter[cat].getYield()[i]
        hCutFlow[countt].Fill(i+1, float(yields))
        hCutFlow[countt].GetXaxis().SetBinLabel(i+1,str(cutCounter[cat].getLabels()[i]))
        #print cutCounter[cat].getYield()[i], i, cutCounter[cat].getLabels()[i]

    
    hCutFlow[countt].Sumw2()
    countt+=1

if not MC : CJ.printJSONsummary()


outTuple.writeTree()









  
            

    
    


