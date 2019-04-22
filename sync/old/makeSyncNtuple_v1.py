#
# make sync ntuple for ZH tau tau analysis
# takes nanoAOD file as input 
#
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector  
import numpy as np
from math import sqrt
import tauFun
import generalFunctions as GF 
import outTuple
import time

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-c","--channel",default='tt',help="Category (tt, et, mt) to be analyzed.")
    parser.add_argument("-u","--unique",default='',help="Unique sample e.g., FSA_only or DRM_only")
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    return parser.parse_args()

args = getArgs()
print("args={0:s}".format(str(args)))
maxPrint = 20
verbose = args.verbose
cutCounter = GF.cutCounter()

if len(args.unique) > 1 :
    vals = open('FSA_{0:s}_only.csv'.format(args.channel),'r').readlines()[0].split(',')
    FSA_only = [] 
    for val in vals : FSA_only.append(int(val))
    print("len(FSA_only)={0:d}".format(len(FSA_only)))

    vals = open('Dan_{0:s}_only.csv'.format(args.channel),'r').readlines()[0].split(',')
    Dan_only = [] 
    for val in vals : Dan_only.append(int(val))
    print("len(Dan_only)={0:d}".format(len(Dan_only)))

    print("FSA_only={0} Dan_only={1}".format(args.unique == 'FSA_only', args.unique == 'Dan_only'))
          
inFileName = args.inFileName
print("Opening {0:s} as input.".format(inFileName))
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

channel = args.channel
goodEventCounter = 0
tStart = time.time()
for count, entry in enumerate(inTree) :
    cutCounter.count('All')
    if count % 1000 == 0 : print("Count={0:d}".format(count))
    if count > nMax : break

    if channel == 'tt' :
        tauList = tauFun.getTauList(channel, entry)
        if len(tauList) < 2 : continue
        cutCounter.count('TwoTaus')
        bestTauPair = tauFun.getBestTauPair(channel, entry, tauList )
    elif channel == 'mt' :
        bestTauPair = tauFun.getBestMuTauPair(entry)
        if len(bestTauPair) < 1 :
            if args.unique == 'FSA_only' and entry.event in FSA_only :
                if True :
                    print("\n** FSA only event *** Count={0:d}".format(count))
                    print("bestTauPair={0:s}".format(str(bestTauPair)))
                    bestTauPair = tauFun.getBestMuTauPair(entry,printOn=True)
                    GF.printEvent(entry)
                    GF.printMC(entry)
                    maxPrint -= 1
            continue
        #iMu = bestTauPair[0]
        #bestTauPair[0] = tauFun.getTauPointer(entry,entry.Muon_eta[iMu],entry.Muon_phi[iMu])
    elif channel == 'et' :
        bestTauPair = tauFun.getBestETauPair(entry)
        if len(bestTauPair) < 1 :
            if args.unique == 'FSA_only' and entry.event in FSA_only :
                if True :
                    print("\n** FSA only event *** Count={0:d}".format(count))
                    print("bestTauPair = {0:s}".format(str(bestTauPair)))
                    best = tauFun.getBestETauPair(entry,printOn=True) 
                    GF.printEvent(entry)
                    maxPrint -= 1
            continue
        #iE = bestTauPair[0]
        #bestTauPair[0] = tauFun.getTauPointer(entry,entry.Electron_eta[iE],entry.Electron_phi[iE])
    if len(bestTauPair) < 1 : continue
    cutCounter.count("TauPair") 
    if bestTauPair[0] < 0 : continue
    cutCounter.count("GoodTauPair")
        
    #if False and len(args.unique) > 0  and (not ((entry.event in Dan_only) or (entry.event in FSA_only))) and maxPrint > 0 :
    if args.unique == 'Dan_only'  and (entry.event in Dan_only)  and maxPrint > 0 :
        print("\n** GOOD EVENT in Dan only sample *** Count={0:d}".format(count))
        print("bestTauPair = {0:s}".format(str(bestTauPair)))
        GF.printEvent(entry)
        maxPrint -= 1
        
    if len(bestTauPair) > 1 :
        jt1, jt2 = bestTauPair[0], bestTauPair[1]
    else :
        continue

    SVFit = True
    LepP, LepM = TLorentzVector(), TLorentzVector()
    outTuple.Fill(entry,SVFit,channel,jt1,jt2,LepP,LepM) 

dT = time.time() - tStart
print("Run time={0:.2f} s  time/event={1:.1f} us".format(dT,1000000.*dT/count))

outTuple.writeTree()
cutCounter.printSummary()








  
            

    
    


