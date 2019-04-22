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
    parser.add_argument("-c","--category",default='mmtt',help="Event category to analyze.") 
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    parser.add_argument("-t","--testMode",default='',help="tylerOnly or DRMonly")
    return parser.parse_args()

def DR(Lep,jt) :
    phi1, eta1 = Lep.Phi(), Lep.Eta()
    phi2, eta2 = entry.Tau_phi[jt], entry.Tau_eta[jt]
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
cat = args.category
maxPrint = 10

cutCounter = GF.cutCounter()

inFileName = args.inFileName
print("Opening {0:s} as input.  Event category {1:s}".format(inFileName,cat))
inFile = TFile.Open(inFileName)
inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
nMax = nentries
print("nentries={0:d} nMax={1:d}".format(nentries,nMax))
if args.nEvents > 0 : nMax = min(args.nEvents,nentries)

outFileName = GF.getOutFileName(args).replace(".root",".ntup")
print("Opening {0:s} as output.".format(outFileName))
outTuple = outTuple.outTuple(outFileName)

tStart = time.time()
eventList = []
for count, entry in enumerate(inTree) :
    cutCounter.count('All')
    if count % 1000 == 0 : print("Count={0:d}".format(count))
    if count > nMax : break
 
    if cat[0:2] == 'mm' and not entry.HLT_IsoMu27 : continue
    if cat[0:2] == 'ee' and not entry.HLT_Ele35_WPTight_Gsf : continue
    cutCounter.count('Trigger')
    
    if cat[0:2] == 'ee' :
        if entry.nElectron < 2 : continue
    if cat[0:2] == 'mm' :
        if entry.nMuon < 2 : continue
        if entry.Muon_pt[0] < 28. : continue    # require 2 muons, one with at least 27 GeV of Pt 

    cutCounter.count('TwoLepton')

    goodElectronList = tauFun.makeGoodElectronList(entry)
    goodMuonList = tauFun.makeGoodMuonList(entry)
    goodElectronList, goodMuonList = tauFun.eliminateCloseLeptons(entry, goodElectronList, goodMuonList)

    if cat[0:2] == 'ee' :
        if len(goodElectronList) < 2 : continue
        pairList = tauFun.findZ(goodElectronList,[], entry)
        
    if cat[0:2] == 'mm' :
        if len(goodMuonList) < 2 :
            continue
        pairList = tauFun.findZ([],goodMuonList, entry)

    if len(pairList) < 1 :
        continue
    cutCounter.count('LeptonPair') 
    LepP, LepM = pairList[0], pairList[1]
    M = (LepM + LepP).M()
    if M < 60. or M > 120. : continue
    cutCounter.count('FoundZ')
        
    tauList = tauFun.getTauList(cat, entry)
    if len(tauList) < 2 : continue
    cutCounter.count('TwoTaus')
    
    bestTauPair = tauFun.getBestTauPair(cat, entry, tauList )
    if len(bestTauPair) < 1 : continue
    cutCounter.count("GoodTauPair")

    if len(bestTauPair) > 1 :
        jt1, jt2 = bestTauPair[0], bestTauPair[1]
    else :
        continue

    # apply DR cuts between leptons and taus
    if DR(LepP,jt1) < 0.5 or DR(LepP,jt2) < 0.5 or DR(LepM,jt1) < 0.5 or DR(LepM,jt2) < 0.5 : continue
    cutCounter.count('DR') 

    SVFit = True
    outTuple.Fill(entry,SVFit,cat[-2:],jt1,jt2,LepP,LepM) 

    if maxPrint > 0 :
        maxPrint -= 1
        print("Good Event")
        print("goodMuonList={0:s} goodElectronList={1:s} Mll={2:.1f} tauList={3:s} bestTauPair={4:s}".format(
            str(goodMuonList),str(goodElectronList),M,str(tauList),str(bestTauPair)))
        GF.printEvent(entry)
                
dT = time.time() - tStart
print("Run time={0:.2f} s  time/event={1:.1f} us".format(dT,1000000.*dT/count))

outTuple.writeTree()
cutCounter.printSummary()
open("eventList.txt",'w').writelines(eventList)









  
            

    
    


