#!/usr/bin/env python

""" ZH.py: makes an nTuple for the ZH->tautau analysis """

__author__ = "Dan Marlow, Alexis Kalogeropoulos, Gage DeZoort" 
__version__ = "GageDev_v1.1"

# import external modules 
import sys
import numpy as np
from ROOT import TFile, TTree, TH1, TH1D, TCanvas, TLorentzVector  
from math import sqrt, pi
#from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
#from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
#from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool

# import from ZH_Run2/funcs/
sys.path.insert(1,'../funcs/')
import tauFun2 as TF
import generalFunctions as GF 
import Weights 
import outTuple
import time

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='ZHtoTauTau_test.root',help="File to be analyzed.")
    parser.add_argument("-c","--category",default='none',help="Event category to analyze.")
    parser.add_argument("--nickName",default='',help="MC sample nickname") 
    parser.add_argument("-d","--dataType",default='MC',help="Data or MC") 
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    parser.add_argument("-m","--maxPrint",default=0,type=int,help="Maximum number of events to print.")
    parser.add_argument("-t","--testMode",default='',help="tau MVA selection")
    parser.add_argument("-y","--year",default=2017,type=int,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default='ZH',help="is this for the ZH or the AZH analysis?")
    parser.add_argument("-u","--unique",default='none',help="CSV file containing list of unique events for sync studies.") 
    parser.add_argument("-w","--weights",default=False,type=int,help="to re-estimate Sum of Weights")
    parser.add_argument("-j","--doSystematics",type=str, default='false',help="do JME systematics")
    
    return parser.parse_args()

args = getArgs()
print("args={0:s}".format(str(args)))
maxPrint = args.maxPrint 

cutCounter = {}
cutCounterGenWeight = {}

doJME  = args.doSystematics.lower() == 'true' or args.doSystematics.lower() == 'yes' or args.doSystematics == '1'

doJME = True

cats = ['eeet','eemt','eett','eeem','mmet','mmmt','mmtt','mmem']

for cat in cats : 
    cutCounter[cat] = GF.cutCounter()
    cutCounterGenWeight[cat] = GF.cutCounter()

inFileName = args.inFileName
print("Opening {0:s} as input.  Event category {1:s}".format(inFileName,cat))

isAZH=False
if str(args.selection) == 'AZH' : isAZH = True
if isAZH : print 'You are running on the AZH mode !!!'

inFile = TFile.Open(inFileName)
inFile.cd()

inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
nMax = nentries
print("nentries={0:d} nMax={1:d}".format(nentries,nMax))
if args.nEvents > 0 : nMax = min(args.nEvents-1,nentries)


MC = len(args.nickName) > 0 
if args.dataType == 'Data' or args.dataType == 'data' : MC = False
if args.dataType == 'MC' or args.dataType == 'mc' : MC = True

if MC :
    print "this is MC, will get PU etc", args.dataType
    PU = GF.pileUpWeight()
    PU.calculateWeights(args.nickName,args.year)
    #else : PU.calculateWeights('TTJets_DiLept',args.year)
else :
    CJ = ''#GF.checkJSON(filein='Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt')
    if args.year == 2016 : CJ = GF.checkJSON(filein='Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt')
    if args.year == 2017 : CJ = GF.checkJSON(filein='Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt')
    if args.year == 2018 : CJ = GF.checkJSON(filein='Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt')


print 'systematics', doJME

era=str(args.year)

outFileName = GF.getOutFileName(args).replace(".root",".ntup")

if MC : 
    if "WJetsToLNu" in outFileName and 'TWJets' not in outFileName:
	hWxGenweightsArr = []
	for i in range(5):
	    hWxGenweightsArr.append(TH1D("W"+str(i)+"genWeights",\
		    "W"+str(i)+"genWeights",1,-0.5,0.5))
    elif "DYJetsToLL" in outFileName:
	hDYxGenweightsArr = []
	for i in range(5):
	    hDYxGenweightsArr.append(TH1D("DY"+str(i)+"genWeights",\
		    "DY"+str(i)+"genWeights",1,-0.5,0.5))


if args.weights > 0 :
    hWeight = TH1D("hWeights","hWeights",1,-0.5,0.5)
    hWeight.Sumw2()

    for count, e in enumerate(inTree) :
        hWeight.Fill(0, e.genWeight)
    

        if "WJetsToLNu" in outFileName and 'TWJets' not in outFileName:

            npartons = ord(e.LHE_Njets)
	    if  npartons <= 4: 	hWxGenweightsArr[npartons].Fill(0, e.genWeight)
        if "DYJetsToLL" in outFileName :
            npartons = ord(e.LHE_Njets)
	    if  npartons <= 4 : hDYxGenweightsArr[npartons].Fill(0, e.genWeight)

    fName = GF.getOutFileName(args).replace(".root",".weights")
    fW = TFile( fName, 'recreate' )
    print 'Will be saving the Weights in', fName
    fW.cd()

    if "WJetsToLNu" in outFileName and 'TWJets' not in outFileName:
        for i in range(len(hWxGenweightsArr)):
            hWxGenweightsArr[i].Write()
    elif "DYJetsToLL" in outFileName:
        for i in range(len(hDYxGenweightsArr)):
            hDYxGenweightsArr[i].Write()

    hWeight.Write()
    if args.weights == 2 : 
        fW.Close()
        sys.exit()

#############end weights

# read a CSV file containing a list of unique events to be studied 
unique = False 
if args.unique != 'none' :
    unique = True
    uniqueEvents = set()
    for line in open(args.unique,'r').readlines() : uniqueEvents.add(int(line.strip()))
    print("******* Analyzing only {0:d} events from {1:s} ******.".format(len(uniqueEvents),args.unique))
    
print("Opening {0:s} as output.".format(outFileName))

sysT = ["Central"]

sysall = [
'scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']

#sysall = ['scale_e']

upS=sysall
downS=sysall

for i, sys in enumerate(sysall) : 
    sysT.append(sys+'Up')
    sysT.append(sys+'Down')


#sysT=['Central']
print sysT

isMC = True
if not MC : 
    sysT = ["Central"]
    isMC = False

#sysT = ["Central"]
doSyst= True
outTuple = outTuple.outTuple(outFileName, era, doSyst, sysT, isMC)



tStart = time.time()
countMod = 1000

print outTuple.allsystMET

allMET=[]
for i,j in enumerate(outTuple.allsystMET):
    if 'MET' in j and 'T1_' in j and 'phi' not in j : allMET.append(j)



Weights=Weights.Weights(args.year)

lumiss=['509','1315','779','248','63','69']
lumiss=['313','62', '159','1139']
lumiss=['101']

for count, e in enumerate( inTree) :
    
    if count % countMod == 0 :
        print("Count={0:d}".format(count))
        if count >= 10000 : countMod = 10000
    if count == nMax : break    
    
    #if count<320000 : continue
    #if count>370000 : break

    #if str(e.luminosityBlock) not in lumiss : continue
    #if str(e.luminosityBlock) in lumiss : printOn = True
    #if entry.run==325170 and entry.luminosityBlock==313 and entry.event==578438770 : printOn = True

    for cat in cats : 
        cutCounter[cat].count('All')
	if  MC :   cutCounterGenWeight[cat].countGenWeight('All', e.genWeight)
 
    isInJSON = False
    if not MC : isInJSON = CJ.checkJSON(e.luminosityBlock,e.run)
    if not isInJSON and not MC :
        #print("Event not in JSON: Run:{0:d} LS:{1:d}".format(e.run,e.luminosityBlock))
        continue

    for cat in cats: 
        cutCounter[cat].count('InJSON')
	if  MC :   cutCounterGenWeight[cat].countGenWeight('InJSON', e.genWeight)
    
    MetFilter = GF.checkMETFlags(e,args.year, isMC)
    if MetFilter : continue
    
    for cat in cats: 
        cutCounter[cat].count('METfilter') 
	if  MC :   cutCounterGenWeight[cat].countGenWeight('METfilter', e.genWeight)


    if unique :
        if e.event in uniqueEvents :
            for cat in cats: cutCounter[cat].count('Unique') 
        else :
            continue
    if not TF.goodTrigger(e, args.year) : continue


    for cat in cats: 
	cutCounter[cat].count('Trigger')
	if  MC :   cutCounterGenWeight[cat].countGenWeight('Trigger', e.genWeight)


    met_pt = float(e.MET_pt)
    met_phi = float(e.MET_phi)

    if era=='2017' :
	met_pt = float(e.METFixEE2017_pt)
	met_phi = float(e.METFixEE2017_phi)

    if doJME :  #default after JME systematics with Smear
        if era!='2017' :
	    try : 
		met_pt = float(e.MET_T1_pt)
		met_phi = float(e.MET_T1_phi)
	    except AttributeError : 
		met_pt = float(e.MET_pt)
		met_phi = float(e.MET_pt)
        if era=='2017' :
            try : 
		met_pt = float(e.METFixEE2017_T1_pt)
		met_phi = float(e.METFixEE2017_T1_phi)
	    except AttributeError : 
		met_pt = float(e.METFixEE2017_pt)
		met_phi = float(e.METFixEE2017_phi)

    #print met_pt, 'smear', e.MET_T1Smear_pt, 'uncorrected?', e.MET_pt
    tauMass=[]
    tauPt=[]
    eleMass=[]
    elePt=[]
    muMass=[]
    muPt=[]
    metPtPhi=[]
    metPtPhi.append(float(met_pt))
    metPtPhi.append(float(met_phi))

    if MC : 
	if len(muMass) == 0 :
	    for j in range(e.nMuon):
		muMass.append(e.Muon_mass[j])
		muPt.append(e.Muon_pt[j])

	if len(eleMass) == 0 :
	    for j in range(e.nElectron):
		eleMass.append(e.Electron_mass[j])
		elePt.append(e.Electron_pt[j])

	if len(tauMass) == 0 :
	    for j in range(e.nTau):
		tauMass.append(e.Tau_mass[j])
		tauPt.append(e.Tau_pt[j])



    
    for isyst, systematic in enumerate(sysT) : 
	if isyst>0 : #use the default pT/mass for Ele/Muon/Taus before doing any systematic
	#if 'Central' in systematic or 'prong' in systematic : #use the default pT/mass for Ele/Muon/Taus before doing the Central or the tau_scale systematics ; otherwise keep the correction

	    for j in range(e.nMuon): 
                e.Muon_pt[j] = muPt[j]
                e.Muon_mass[j] = muMass[j]
	    for j in range(e.nElectron): 
                e.Electron_pt[j] = elePt[j]
                e.Electron_mass[j] = eleMass[j]
	    for j in range(e.nTau): 
                e.Tau_pt[j] = tauPt[j]
                e.Tau_mass[j] = tauMass[j]
             

        
        #print ''
        #applyES - do it once for Central and redoit for tau_scale_systematics - otherwise keep the correction
        #print 'before fixxxxxxxxxxxx e.MET_T1_pt', e.MET_T1_pt, '== met_pt ? ', met_pt, '== what is fed in', metPtPhi[0], e.event, systematic
	#met_pt, met_phi = Weights.applyES(e, args.year, systematic, metPtPhi)
	if isMC: 

	    met_pt, met_phi, metlist, philist = Weights.applyES(e, args.year, systematic, metPtPhi, allMET)
	    #met_pt, met_phi = Weights.applyES(e, args.year, systematic, metPtPhi, allMET)
	    #print 'after fixxxxxxxxxxxx e.MET_T1_pt', e.MET_T1_pt, ' == what is fed in', metPtPhi[0], ' corrected MET ->', met_pt,  'some jesTotalUp MET', e.MET_T1_pt_jesTotalUp , e.event, systematic
	    
	    #if len(metlist) != len(philist) : print 'There is a problem with met/phi systematics list - will not concider this event', e.event
	    # uncomment the following if you need to pass the corrected MET for systematics to account for the ES corrections
	    if systematic == 'Central' :
		for i, j in enumerate (metlist): 

		    outTuple.list_of_arrays[i][0] = metlist[i]
		for i, j in enumerate (philist): 
		    outTuple.list_of_arrays[i+len(metlist)][0] = philist[i]

		    #if systematic == 'Central' and ( e.event==1481 or e.event==17892 or e.event==8904):
		    #    print 'it was', outTuple.list_of_arrays[i][0] , i, j, len(metlist) , metlist[i], e.event, e.MET_T1_pt_jesAbsoluteUp, len(sysT), systematic


	for lepMode in ['ee','mm'] :
	    if args.category != 'none' and not lepMode in args.category : continue

	    if lepMode == 'ee' :
		if e.nElectron < 2 : continue
		for cat in cats[:4] : 
		    cutCounter[cat].count('LeptonCount')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('LeptonCount', e.genWeight)
	    if lepMode == 'mm' :
		if e.nMuon < 2 : continue 
		for cat in cats[4:] : 
		    cutCounter[cat].count('LeptonCount')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('LeptonCount', e.genWeight)


	    goodElectronList = TF.makeGoodElectronList(e)
	    goodMuonList = TF.makeGoodMuonList(e)
	    goodElectronList, goodMuonList = TF.eliminateCloseLeptons(e, goodElectronList, goodMuonList)
	    goodElectronListExtraLepton=[]
	    goodMuonListExtraLepton=[]

	    lepList=[]

		   
	    if lepMode == 'ee' :
		if len(goodElectronList) < 2 : continue
		for cat in cats[:4] :
		    cutCounter[cat].count('GoodLeptons')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('GoodLeptons', e.genWeight)

		pairList, lepList = TF.findZ(goodElectronList,[], e)
		if len(lepList) != 2 : continue
		for cat in cats[:4] : 
		    cutCounter[cat].count('LeptonPair')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('LeptonPair', e.genWeight)
	    
	    if lepMode == 'mm' :
		if len(goodMuonList) < 2 : continue
		for cat in cats[4:] :
		    cutCounter[cat].count('GoodLeptons')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('GoodLeptons', e.genWeight)

		pairList, lepList = TF.findZ([],goodMuonList, e)
		if len(lepList) != 2 : continue
		for cat in cats[4:] : 
		    cutCounter[cat].count('LeptonPair')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('LeptonPair', e.genWeight)

	    LepP, LepM = pairList[0], pairList[1]
	    M = (LepM + LepP).M()
	    
	    if not TF.mllCut(M) :
		if unique :
		    print("Zmass Fail: : Event ID={0:d} cat={1:s} M={2:.2f}".format(e.event,cat,M))
		    #GF.printEvent(e)
		    #if MC : GF.printMC(e)
		continue ##cut valid for both AZH and ZH

	    if lepMode == 'ee' :
		for cat in cats[:4]: 
		    cutCounter[cat].count('FoundZ')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('FoundZ', e.genWeight)
	    if lepMode == 'mm' :
		for cat in cats[4:]: 
		    cutCounter[cat].count('FoundZ')
		    if  MC :   cutCounterGenWeight[cat].countGenWeight('FoundZ', e.genWeight)

	    for tauMode in ['et','mt','tt','em'] :
		if args.category != 'none' and tauMode != args.category[2:] : continue
		cat = lepMode + tauMode
		if tauMode == 'tt' :
		    tauList = TF.getTauList(cat, e, pairList=pairList)
		    bestTauPair = TF.getBestTauPair(cat, e, tauList)
					
		elif tauMode == 'et' :
		    bestTauPair = TF.getBestETauPair(e,cat=cat,pairList=pairList)
		elif tauMode == 'mt' :
		    bestTauPair = TF.getBestMuTauPair(e,cat=cat,pairList=pairList)
		elif tauMode == 'em' :
		    bestTauPair = TF.getBestEMuTauPair(e,cat=cat,pairList=pairList)
		else : continue

		
		if len(bestTauPair) < 1 :
		    if unique :
			print("Tau Pair Fail: Event ID={0:d} cat={1:s}".format(e.event,cat))
			bestTauPair = TF.getBestEMuTauPair(e,cat=cat,pairList=pairList,printOn=True) 
			GF.printEvent(e)
					
		    if False and maxPrint > 0 and (tauMode == GF.eventID(e)[2:4]) :
			maxPrint -= 1
			print("Failed tau-pair cut")
			print("Event={0:d} cat={1:s}".format(e.event,cat))
			print("goodMuonList={0:s} goodElectronList={1:s} Mll={3:.1f} bestTauPair={4:s}".format(
			    str(goodMuonList),str(goodElectronList),str(pairList),M,str(bestTauPair)))
			print("Lep1.pt() = {0:.1f} Lep2.pt={1:.1f}".format(pairList[0].Pt(),pairList[1].Pt()))
			GF.printEvent(e)
			GF.printMC(e)
		    continue

		if len(bestTauPair) > 1 :
		    jt1, jt2 = bestTauPair[0], bestTauPair[1]
		else :
		    continue

		goodElectronListExtraLepton = TF.makeGoodElectronListExtraLepton(e,lepList)
		goodMuonListExtraLepton = TF.makeGoodMuonListExtraLepton(e,lepList)
		goodElectronListExtraLepton, goodMuonListExtraLepton = TF.eliminateCloseLeptons(e, goodElectronListExtraLepton, goodMuonListExtraLepton)
		if tauMode == 'et' :
		    if bestTauPair[0] in goodElectronListExtraLepton : goodElectronListExtraLepton.remove(bestTauPair[0])

		if tauMode == 'mt' :
		    if bestTauPair[0] in goodMuonListExtraLepton : goodMuonListExtraLepton.remove(bestTauPair[0])

		if tauMode == 'em' :
		    if bestTauPair[0] in goodElectronListExtraLepton : goodElectronListExtraLepton.remove(bestTauPair[0])
		    if bestTauPair[1] in goodMuonListExtraLepton : goodMuonListExtraLepton.remove(bestTauPair[1])


		#if len(goodMuonListExtraLepton) > 0 or len(goodElectronListExtraLepton) >0 : 
		#    print 'some info', cat, 'lepList', lepList, tauList, 'tauPair', bestTauPair, 'extra', goodElectronListExtraLepton, goodMuonListExtraLepton, 'will remove it'

		if len(goodMuonListExtraLepton) > 0 or len(goodElectronListExtraLepton) >0 : continue

		cutCounter[cat].count("GoodTauPair")
		if  MC:   cutCounterGenWeight[cat].countGenWeight('GoodTauPair', e.genWeight)

		if MC :
		    outTuple.setWeight(PU.getWeight(e.PV_npvs)) 
		    outTuple.setWeightPU(PU.getWeight(e.Pileup_nPU)) 
		    outTuple.setWeightPUtrue(PU.getWeight(e.Pileup_nTrueInt)) 
		    #print 'nPU', e.Pileup_nPU, e.Pileup_nTrueInt, PU.getWeight(e.Pileup_nPU), PU.getWeight(e.Pileup_nTrueInt), PU.getWeight(e.PV_npvs), PU.getWeight(e.PV_npvsGood)
		else : 
		    outTuple.setWeight(1.) 
		    outTuple.setWeightPU(1.) ##
		    outTuple.setWeightPUtrue(1.)


		#cutCounter[cat].count("VVtightTauPair")
		#if MC :   cutCounterGenWeight[cat].countGenWeight('VVtightTauPair', e.genWeight)
			    
		SVFit = True
		#SVFit = False
		
		if not MC : isMC = False
		 
		#print 'again--------------->', e.MET_pt, e.MET_phi
                #print 'will Fill for syst', isyst, sysT[isyst]
		outTuple.Fill(e,SVFit,cat,jt1,jt2,LepP,LepM,lepList,isMC,era,doJME, met_pt, met_phi,  isyst, tauMass, tauPt, eleMass, elePt, muMass, muPt)
		#outTuple.Fill(e,SVFit,cat,jt1,jt2,LepP,LepM,lepList,isMC,era,doJME, met_pt, met_phi,  isyst)

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

hLabels=[]
hLabels.append('All')
hLabels.append('inJSON')
hLabels.append('METfilter')
hLabels.append('Trigger')
hLabels.append('LeptonCount')
hLabels.append('GoodLeptons')
hLabels.append('LeptonPair')
hLabels.append('FoundZ')
hLabels.append('GoodTauPair')

hCutFlow=[]
hCutFlowW=[]

#
outTuple.writeTree()
fW = TFile( outFileName, 'update' )
fW.cd()

print '------------------------->',fW, outFileName
for icat,cat in enumerate(cats) :
    print('\nSummary for {0:s}'.format(cat))
    cutCounter[cat].printSummary()
    hName="hCutFlow_"+str(cat)
    hNameW="hCutFlowWeighted_"+str(cat)
    hCutFlow.append( TH1D(hName,hName,20,0.5,20.5))
    if MC  : hCutFlowW.append( TH1D(hNameW,hNameW,20,0.5,20.5))
    #if not MC : lcount=len(cutCounter[cat].getYield()) #lcount stands for how many different values you have
    #else : lcount=len(cutCounterGenWeight[cat].getYieldWeighted()) #lcount stands for how many different values you have
    lcount=len(hLabels)
    print lcount, cat, icat
    for i in range(len(hLabels)) :
        hCutFlow[icat].GetXaxis().SetBinLabel(i+1,hLabels[i])
        if MC : hCutFlowW[icat].GetXaxis().SetBinLabel(i+1,hLabels[i])

    for i in range(lcount) :
        #hCutFlow[cat].Fill(1, float(cutCounter[cat].getYield()[i]))
        yields = cutCounter[cat].getYield()[i]
        hCutFlow[icat].Fill(i+1, float(yields))

        if MC : 
	    yieldsW = cutCounterGenWeight[cat].getYieldWeighted()[i]
            hCutFlowW[icat].Fill(i+1, float(yieldsW))
        #print cutCounter[cat].getYield()[i], i, cutCounter[cat].getLabels()[i]

       
    hCutFlow[icat].Sumw2()
    hCutFlow[icat].Write()
    if MC : 
        hCutFlowW[icat].Sumw2()
        hCutFlowW[icat].Write()
    icat+=1

if not MC : CJ.printJSONsummary()



