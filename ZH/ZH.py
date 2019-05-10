#
# make sync ntuple for ZH tau tau analysis
# takes nanoAOD file as input 
#
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector  
import numpy as np
from math import sqrt, pi
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
    parser.add_argument("-c","--category",default='mmem',help="Event category to analyze.")
    parser.add_argument("--nickName",default='',help="MC sample nickname") 
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    parser.add_argument("-m","--maxPrint",default=0,type=int,help="Maximum number of events to print.")
    parser.add_argument("-t","--testMode",default='',help="tau MVA selection")
    parser.add_argument("-y","--year",default=2017,type=int,help="tylerOnly or DRMonly")
    
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
cats = ['eeet','eemt','eett','eeem','mmet','mmmt','mmtt','mmem'] 
#cats = ['mmmt','eeem','mmem'] 
for cat in cats : cutCounter[cat] = GF.cutCounter()

inFileName = args.inFileName
print("Opening {0:s} as input.  Event category {1:s}".format(inFileName,cat))
inFile = TFile.Open(inFileName)
inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
nMax = nentries
print("nentries={0:d} nMax={1:d}".format(nentries,nMax))
if args.nEvents > 0 : nMax = min(args.nEvents-1,nentries)

MC = len(args.nickName) > 0 
if MC : 
    PU = GF.pileUpWeight()
    PU.calculateWeights(args.nickName,args.year)

outFileName = GF.getOutFileName(args).replace(".root",".ntup")
print("Opening {0:s} as output.".format(outFileName))
outTuple = outTuple.outTuple(outFileName)


#HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v 29/fb for 2017
#HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL
#HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_

tStart = time.time()
for count, e in enumerate(inTree) :
    for cat in cats : cutCounter[cat].count('All')
    if count % 1000 == 0 : print("Count={0:d}".format(count))
    if count == nMax : break

    #evID = GF.eventID(e)
    #if evID == '' : continue 
    #cutCounter[evID].count('Valid Mode') 
    for lepMode in ['ee','mm'] :
        if lepMode == 'ee'  :
            if not e.HLT_Ele35_WPTight_Gsf : continue
            for cat in cats[:3] : cutCounter[cat].count('Trigger')
        if lepMode == 'mm' :
            if not e.HLT_IsoMu27 : continue
            for cat in cats[3:] : cutCounter[cat].count('Trigger')

        if e.nTau < 1 : continue 
        if lepMode == 'ee' :
            if e.nElectron < 2 : continue
            for cat in cats[:3] : cutCounter[cat].count('LeptonCount')
        if lepMode == 'mm' :
            if e.nMuon < 2 : continue 
            for cat in cats[3:] : cutCounter[cat].count('LeptonCount')

        goodElectronList = tauFun.makeGoodElectronList(e)
        goodMuonList = tauFun.makeGoodMuonList(e)
        goodElectronList, goodMuonList = tauFun.eliminateCloseLeptons(e, goodElectronList, goodMuonList)

        if lepMode == 'ee' :
            if len(goodElectronList) < 2 :  continue
            pairList = tauFun.findZ(goodElectronList,[], e)
        
        if lepMode == 'mm' :
            if len(goodMuonList) < 2 : continue
            pairList = tauFun.findZ([],goodMuonList, e)

        if len(pairList) < 1 : continue
        if lepMode == 'ee' :
            for cat in cats[:3]: cutCounter[cat].count('LeptonPair')
        if lepMode == 'mm' :
            for cat in cats[3:]: cutCounter[cat].count('LeptonPair')
   
            
        LepP, LepM = pairList[0], pairList[1]
        M = (LepM + LepP).M()
        if M < 60. or M > 120. : continue
        if lepMode == 'ee' :
            for cat in cats[:3]: cutCounter[cat].count('FoundZ')
        if lepMode == 'mm' :
            for cat in cats[3:]: cutCounter[cat].count('FoundZ')
        
        for tauMode in ['et','mt','tt','em'] :
            cat = lepMode + tauMode
            if tauMode == 'tt' :
                tauList = tauFun.getTauList(cat, e, pairList=pairList)
                bestTauPair = tauFun.getBestTauPair(cat, e, tauList )
                #print "==================================", lepMode, tauMode, tauList
                                    
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

            #if tauMode != 'em' : cutCounter[cat].count("GoodTauPair")
            cutCounter[cat].count("GoodTauPair")
            #else : cutCounter[cat].count("GoodEMuPair")

            if tauMode == 'tt' and args.testMode.lower() == "vvtight" :
                j1, j2 = bestTauPair[0], bestTauPair[1]
                #print("tau_id_1 = {0:d}".format(ord(e.Tau_idMVAnewDM2017v2[j1])))
                #print("tau_id_2 = {0:d}".format(ord(e.Tau_idMVAnewDM2017v2[j2])))
                if ord(e.Tau_idMVAnewDM2017v2[j1]) < 64 : continue
                if ord(e.Tau_idMVAnewDM2017v2[j2]) < 64 : continue

            cutCounter[cat].count("VVtightTauPair")

            if len(bestTauPair) > 1 :
                jt1, jt2 = bestTauPair[0], bestTauPair[1]
            else :
                continue

            if MC : outTuple.setWeight(PU.getWeight(e.Pileup_nPU))
        
            SVFit = False
            outTuple.Fill(e,SVFit,cat,jt1,jt2,LepP,LepM) 

            if maxPrint > 0 :
                maxPrint -= 1
                print("\n\nGood Event={0:d} cat={1:s}  MCcat={2:s}".format(e.event,cat,GF.eventID(e)))
                print("goodMuonList={0:s} goodElectronList={1:s} Mll={2:.1f} bestTauPair={3:s}".format(
                    str(goodMuonList),str(goodElectronList),M,str(bestTauPair)))
                print("Lep1.pt() = {0:.1f} Lep2.pt={1:.1f}".format(pairList[0].Pt(),pairList[1].Pt()))
                GF.printEvent(e)
                print("Event ID={0:s} cat={1:s}".format(GF.eventID(e),cat))
                #GF.printMC(e)
                
dT = time.time() - tStart
print("Run time={0:.2f} s  time/event={1:.1f} us".format(dT,1000000.*dT/count))

outTuple.writeTree()
for cat in cats :
    print('\nSummary for {0:s}'.format(cat))
    cutCounter[cat].printSummary()
    









  
            

    
    


