# !/usr/bin/env python

""" tauFun.py: apply selection sequence to four-lepton final state """

import io
import yaml
import subprocess
from ROOT import TLorentzVector
from math import sqrt, sin, cos, pi
from itertools import combinations
import os
import os.path
import sys
sys.path.append('../TauPOG')
from TauPOG.TauIDSFs.TauIDSFTool import TauIDSFTool
from TauPOG.TauIDSFs.TauIDSFTool import TauESTool
from TauPOG.TauIDSFs.TauIDSFTool import TauFESTool

__author__ = "Dan Marlow, Alexis Kalogeropoulos, Gage DeZoort"
__date__   = "Monday, Oct. 28th, 2019"

# get selections from configZH.yaml:
with io.open('cuts.yaml', 'r') as stream:
    selections = yaml.load(stream)
print "Using selections:\n", selections



def goodTrigger(e, year):
    trig = selections['trig']
    if not (trig['singleLepton'] or trig['doubleLepton']) : return True
    #single mu 2016: HLT IsoMu22 v, HLT IsoMu22 eta2p1 v, HLT IsoTkMu22 v, HLT IsoTkMu22 eta2p1 v and cut pt(mu)>23, eta(mu)<2.1
    #single ele 2016: HLT Ele25 eta2p1 WPTight Gsf v and cut pt(ele)>26, eta(ele)<2.1
    #single mu 2017: HLT IsoMu24 v, HLT IsoMu27 v and cut pt(mu)>25, eta(mu)<2.4
    #single ele 2017: HLT Ele27 WPTight Gsf v, HLT Ele32 WPTight Gsf v, HLT Ele35 WPTight Gsf v and cut pt(ele)>28, eta(ele)<2.1
    #single mu 2018: HLT IsoMu24 v, HLT IsoMu27 v and cut pt(mu)>25, eta(mu)<2.4
    #single ele 2018:  HLT Ele32 WPTight Gsf v, HLT Ele35 WPTight Gsf v and cut pt(ele)>33, eta(ele)<2.1
   
    
    if year == 2016 :
        goodSingle = (e.HLT_IsoMu22 or e.HLT_IsoMu22_eta2p1 or e.HLT_IsoTkMu22 or e.HLT_IsoTkMu22_eta2p1 or e.HLT_Ele25_eta2p1_WPTight_Gsf or e.HLT_Ele27_eta2p1_WPTight_Gsf or e.HLT_IsoMu24 or e.HLT_IsoTkMu24 or e.HLT_IsoMu27)

        goodDouble = (e.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ or e.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ or e.HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ )
    elif (year == 2017 or year == 2018) :
        goodSingle = (e.HLT_Ele27_WPTight_Gsf or e.HLT_Ele35_WPTight_Gsf or e.HLT_Ele32_WPTight_Gsf or e.HLT_IsoMu24 or e.HLT_IsoMu27)

        goodDouble = (e.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL or e.HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ  or e.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 or e.HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8)
    


    else :
        print("Invalid year={0:d} in goodTrigger()".format(year))
        return False
    
    return (trig['singleLepton'] and goodSingle) or (trig['doubleLepton'] and goodDouble)  

    

def getTauList(channel, entry, pairList=[],printOn=False) :
    """ tauFun.getTauList(): return a list of taus that 
                             pass the basic selection cuts               
    """

    if not channel in ['mmtt','eett'] :
        print("Warning: invalid channel={0:s} in tauFun.getTauList()".format(channel))
        exit()

    if printOn : print ' getTauList : will be checking nTau', entry.nTau

    if entry.nTau == 0: 
        if printOn : print ' failed nTau', entry.nTau
        return []

    tauList = []
    tt = selections['tt'] # selections for H->tau(h)+tau(h)
    for j in range(entry.nTau):   
        #print entry.Tau_pt[j] 
        # apply tau(h) selections 
        if printOn : print 'looking for Tau j', j, 'Q', entry.Tau_charge[j]
        if entry.Tau_pt[j] < tt['tau_pt']: 
            if printOn : print("        fail Tau pT {0:f}".format(entry.Tau_pt[j]))
            continue
        if abs(entry.Tau_eta[j]) > tt['tau_eta']: 
       
            if printOn : print("        fail Tau eta {0:f}".format(abs(entry.Tau_eta[j])))
            continue
        if abs(entry.Tau_dz[j]) > tt['tau_dz']: 
            if printOn : print("        fail Tau dZ {0:f}".format(entry.Tau_dz[j]))
            continue
        if not entry.Tau_idDecayModeNewDMs[j]: 
            if printOn : print("        fail Tau decayModeNewDM {0:f}".format(entry.Tau_idDecayModeNewDMs[j]))
            continue
	if  entry.Tau_decayMode[j] == 5 or entry.Tau_decayMode[j] == 6 : 
            if printOn : print("        fail Tau decayMode {0:f}".format(entry.Tau_decayMode[j]))
            continue
        if abs(entry.Tau_charge[j]) != 1: 
            if printOn : print("        fail Tau Q {0:d}".format(entry.Tau_charge[j]))
            continue
        
        if tt['tau_vJet'] > 0  and not ord(entry.Tau_idDeepTau2017v2p1VSjet[j]) & tt['tau_vJet'] > 0 :
            if printOn : print("        fail DeepTau vs. Jet={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSjet[j])))
            continue
	if tt['tau_vEle'] > 0 and not ord(entry.Tau_idDeepTau2017v2p1VSe[j]) & tt['tau_vEle'] > 0 :
            if printOn : print("        fail DeepTau vs. ele={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSe[j])))
            continue
        if tt['tau_vMu'] > 0 and not ord(entry.Tau_idDeepTau2017v2p1VSmu[j]) & tt['tau_vMu'] > 0 :
            if printOn : print("        fail DeepTau vs.  mu={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSmu[j])))
            continue

        eta, phi = entry.Tau_eta[j], entry.Tau_phi[j]
        DR0, DR1 =  lTauDR(eta,phi, pairList[0]), lTauDR(eta,phi,pairList[1]) 
        if DR0 < tt['tt_DR'] or DR1 < tt['tt_DR']: 
              
            if printOn : print("        fail DR0={0:f} or DR1={1:f}". format(DR0, DR1))
            continue
        tauList.append(j)
        #print ord(entry.Tau_idDeepTau2017v2p1VSmu[j]), ord(entry.Tau_idDeepTau2017v2p1VSe[j]), ord(entry.Tau_idDeepTau2017v2p1VSjet[j])
    
    if printOn  : print 'returning with tauList from getTauList', tauList
    return tauList




def tauDR(entry, j1,j2) :
    if j1 == j2 : return 0. 
    phi1, eta1, phi2, eta2 = entry.Tau_phi[j1], entry.Tau_eta[j1], entry.Tau_phi[j2], entry.Tau_eta[j2]
    return sqrt( (phi2-phi1)**2 + (eta2-eta1)**2 )


def lTauDR(eta1,phi1,Lep) :
    phi2, eta2 = Lep.Phi(), Lep.Eta()
    dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
    return sqrt(dPhi**2 + (eta2-eta1)**2)


def DRobj(eta1,phi1,eta2,phi2) :
    dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
    return sqrt(dPhi**2 + (eta2-eta1)**2)

def mllCut(mll) :
    mllcuts = selections['mll']
    if mll < mllcuts['mll_low'] or mll > mllcuts['mll_high'] : return False
    return True

def getTauPointer(entry, eta1, phi1) :
    # find the j value that most closely matches the specified eta or phi value
    bestMatch, jBest = 999., -1
    for j in range(entry.nTau) :
        eta2, phi2 = entry.Tau_eta[j], entry.Tau_phi[j]
        dPhi = min(abs(phi2-phi1),2.*pi-abs(phi2-phi1))
        DR = sqrt(dPhi**2 + (eta2-eta1)**2)
        if DR < bestMatch : bestMatch, jBest = DR, j
    if bestMatch > 0.1 :
        jBest = -1 
        print("Error in getTauPointer():   No match found eta={0:.3f} phi={1:.3f}".format(eta1,phi1))
    return jBest

 

def comparePairvspT(entry, tauPairList, printOn=False) :
    """ comparevsPt : return the index of the pair with the highest scalar sum 
    """
    SumList=[]
    for i in range(0,len(tauPairList)) :
         
        j1, j2 = tauPairList[i][0], tauPairList[i][1] # look at leading pt tau in each pair
        if printOn : print 'appending now', entry.Tau_pt[j1] + entry.Tau_pt[j2], j1, j2, tauPairList[i]
        SumList.append(entry.Tau_pt[j1] + entry.Tau_pt[j2])

    
    maxI=SumList.index(max(SumList))

    return maxI
       
def comparePair(entry, pair1, pair2) :
    """ tauFun.comparePair.py: return true if pair2 is 
                               better than pair1 
    """
    
    j1, j2 = pair1[0], pair2[0] # look at leading pt tau in each pair
    j3, j4 = pair1[1], pair2[1] # look at leading pt tau in each pair
    if entry.Tau_rawDeepTau2017v2p1VSjet[j2] > entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
        return True
    if  entry.Tau_rawDeepTau2017v2p1VSjet[j2] < entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
        return False
    if  entry.Tau_rawDeepTau2017v2p1VSjet[j2] == entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
        if entry.Tau_pt[j2] > entry.Tau_pt[j1] :
            return True
        if entry.Tau_pt[j2] < entry.Tau_pt[j1] :
            return False
        if entry.Tau_pt[j2] == entry.Tau_pt[j1] :
            if  entry.Tau_rawDeepTau2017v2p1VSjet[j4] > entry.Tau_rawDeepTau2017v2p1VSjet[j3] : 
                return True
            if  entry.Tau_rawDeepTau2017v2p1VSjet[j4] < entry.Tau_rawDeepTau2017v2p1VSjet[j3] : 
                return False
            if  entry.Tau_rawDeepTau2017v2p1VSjet[j4] == entry.Tau_rawDeepTau2017v2p1VSjet[j3] : 
                if entry.Tau_pt[j4] > entry.Tau_pt[j3] : return True
                if entry.Tau_pt[j4] < entry.Tau_pt[j3] : return False
                if entry.Tau_pt[j4] == entry.Tau_pt[j3] : return False

    # do it once more swapping the tau pairs
    j1, j2 = pair1[1], pair2[1] # look at leading pt tau in each pair
    j3, j4 = pair1[0], pair2[0] # look at leading pt tau in each pair
    if entry.Tau_rawDeepTau2017v2p1VSjet[j2] > entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
        return True
    if  entry.Tau_rawDeepTau2017v2p1VSjet[j2] < entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
        return False
    if  entry.Tau_rawDeepTau2017v2p1VSjet[j2] == entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
        if entry.Tau_pt[j2] > entry.Tau_pt[j1] :
            return True
        if entry.Tau_pt[j2] < entry.Tau_pt[j1] :
            return False
        if entry.Tau_pt[j2] == entry.Tau_pt[j1] :
            if  entry.Tau_rawDeepTau2017v2p1VSjet[j4] > entry.Tau_rawDeepTau2017v2p1VSjet[j3] : 
                return True
            if  entry.Tau_rawDeepTau2017v2p1VSjet[j4] < entry.Tau_rawDeepTau2017v2p1VSjet[j3] : 
                return False
            if  entry.Tau_rawDeepTau2017v2p1VSjet[j4] == entry.Tau_rawDeepTau2017v2p1VSjet[j3] : 
                if entry.Tau_pt[j4] > entry.Tau_pt[j3] : return True
                if entry.Tau_pt[j4] < entry.Tau_pt[j3] : return False
                if entry.Tau_pt[j4] == entry.Tau_pt[j3] : return False



def getBestTauPair(channel, entry, tauList,printOn=False) :
    """ tauFun.getBestTauPair(): return two taus that 
                                 best represent H->tt
    """ 

    if not channel in ['mmtt','eett'] : 
        if printOn : print("Invalid channel={0:s} in tauFun.getBestTauPair()".format(channel))
        exit()

    if len(tauList) < 2: 
        if printOn : print 'failed to find good TauTau Pair'
        if printOn : print("Entering getTauPairs failing nTauList={0:s}".format(tauList))
        return [] 
    
    # form all possible pairs that satisfy DR requirement
    tauPairList = []
    tt = selections['tt'] # selections for H->(tau_h)(tau_h)
    for i in range(len(tauList)) :
        idx_tau1 = tauList[i]
        for j in range(len(tauList)) :
            if i == j: continue
            idx_tau2 = tauList[j]
            if tauDR(entry, idx_tau1, idx_tau2) < tt['tt_DR'] : 
                tdR= tauDR(entry, idx_tau1, idx_tau2) < tt['tt_DR'] 
                if printOn : print "failed tDR=",tdR, "tt_DR =", tt['tt_DR']
                continue
            #tauPairList.append([idx_tau1, idx_tau2])
            if idx_tau1 not in tauPairList : tauPairList.append(idx_tau1)
            if idx_tau2 not in tauPairList : tauPairList.append(idx_tau2)


    if len(tauPairList) == 0 : 
        if printOn : print 'fail tauPairList =0'
        return []

    c = set(combinations(tauPairList, 2))
    if printOn : print 'these are the combinations', c, 'from', tauPairList
    tauPairList=list(c)

    if printOn : print 'Do I need to do the comparePair ? ', len(tauPairList),  tauPairList
   
    maxI= comparePairvspT(entry, tauPairList, printOn)
    tauPairList=tauPairList[maxI]

    if printOn : print 'this is the list of sums', maxI, tauPairList, tauPairList[0], tauPairList[1]

    idx_tau1, idx_tau2 = tauPairList[0], tauPairList[1]
    if entry.Tau_pt[idx_tau2] > entry.Tau_pt[idx_tau1] : 
        if printOn : print 'Sorting tt tauPair', entry.Tau_pt[idx_tau2], entry.Tau_pt[idx_tau1], idx_tau2, idx_tau1
        tauPairList = {}
        tauPairList[0] = idx_tau2
        tauPairList[1] = idx_tau1
        
    if printOn : print 'returning tt tauPairList', tauPairList
    return tauPairList


def getMuTauPairs(entry,cat='mt',pairList=[],printOn=False) :
    """  tauFun.getMuTauPairs.py: return list of acceptable pairs
                                 of muons and taus 
    """

    if entry.nMuon < 1 or entry.nTau < 1:
        if printOn : print("Entering getMuTauPairs failing nMuon={0:d} nTau={1:d}".format(entry.nMuon,entry.nTau))
        return []
    if cat == 'mmmt' and entry.nMuon < 3: return []

    muTauPairs = []
    mt = selections['mt'] # H->tau(mu)+tau(h) selections
    if printOn : print("Entering tauFun.getMuTauPairs() nMuon={0:d} nTau={1:d}".format(entry.nMuon,entry.nTau))
    for i in range(entry.nMuon):
        
        # apply tau(mu) selections
        if mt['mu_type']:
            if not (entry.Muon_isGlobal[i] or entry.Muon_isTracker[i]) :
                if printOn : print("    fail mu_type Global or Tracker={0}".format(entry.Muon_isGlobal[i]))
                continue
        if mt['mu_ID']:
            if not (entry.Muon_mediumId[i] or entry.Muon_tightId[i]) :
                if printOn : print("    fail mu_ID mediumId={0}".format(entry.Muon_mediumId[i]))
                continue
        if abs(entry.Muon_dxy[i]) > mt['mu_dxy']:
            if printOn : print("    fail mu_dxy={0:f}".format(entry.Muon_dxy[i]))
            continue
        if abs(entry.Muon_dz[i]) > mt['mu_dz']:
            if printOn : print("    fail mu_dz={0:f}".format(entry.Muon_dz[i]))
            continue
        mu_eta, mu_phi = entry.Muon_eta[i], entry.Muon_phi[i] 
        if entry.Muon_pt[i] < mt['mu_pt']:
            if printOn : print("    fail mu_pt={0:f}".format(entry.Muon_pt[i]))
            continue
        if abs(mu_eta) > mt['mu_eta']:
            if printOn : print("    fail mu_eta={0:f}".format(entry.Muon_eta[i]))
            continue 
        if  mt['mu_iso_f'] and entry.Muon_pfRelIso04_all[i] > mt['mu_iso']:
            if printOn : print("    fail mu_iso={0:f}".format(entry.Muon_pfRelIso04_all[i]))
            continue

        DR0 = lTauDR(mu_eta,mu_phi,pairList[0]) # l1 vs. tau(mu)
        DR1 = lTauDR(mu_eta,mu_phi,pairList[1]) # l2 vs. tau(mu)
        if DR0 < mt['ll_DR'] or DR1 < mt['ll_DR']:
            if printOn : print("    fail muon DR  DR0={0:f} DR1={1:f} for muon={2:s} vs 0.pT={3:f} vs 1.pT={4:f}".format(DR0,DR1, str(i), pairList[0].Pt(), pairList[1].Pt()))
            continue
        if printOn : print("    Good muon i={0:d}".format(i))
                        
        for j in range(entry.nTau):

            # apply tau(h) selections
            if printOn : print("        tau j={0:d}".format(j))
            if abs(entry.Tau_eta[j]) > mt['tau_eta']:
                if printOn : print("        fail tau eta={0:f}".format(entry.Tau_eta[j]))
                continue
            if entry.Tau_pt[j] < mt['tau_pt']:
                if printOn : print("        fail tau  pt={0:f}".format(entry.Tau_pt[j]))
                continue
            if abs(entry.Tau_dz[j]) > mt['tau_dz']:
                if printOn : print("        fail tau  dz={0:f}".format(entry.Tau_dz[j]))
                continue
            if mt['tau_ID']:
                if not entry.Tau_idDecayModeNewDMs[j]:
                    if printOn : print("        fail tau idDecayModeNewDMs={0}".format(entry.Tau_idDecayModeNewDMs[j]))
                    continue
	    if  mt['tau_decayMode'] and (entry.Tau_decayMode[j] == 5 or entry.Tau_decayMode[j] == 6) :
                if printOn : print("        fail tau decayMode={0:d}".format(entry.Tau_decayMode[j]))
                continue

            ''' # this is the old (pre-DeepTau) selection
	    if ord(entry.Tau_idAntiMu[j]) <= mt['tau_antiMu']: continue
            if ord(entry.Tau_idAntiEle[j]) <= mt['tau_antiEle']: continue
            if cat == 'eemt':
                if ord(entry.Tau_idAntiMu[j]) < mt['tau_eemt_antiMu']: continue
	    '''

	    if mt['tau_vJet'] > 0  and not ord(entry.Tau_idDeepTau2017v2p1VSjet[j]) & mt['tau_vJet'] > 0 :
                if printOn : print("        fail DeepTau vs. Jet={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSjet[j])))
                continue
	    if mt['tau_vEle'] > 0 and not ord(entry.Tau_idDeepTau2017v2p1VSe[j]) & mt['tau_vEle'] > 0 :
                if printOn : print("        fail DeepTau vs. ele={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSe[j])))
                continue
            if mt['tau_vMu'] > 0 and not ord(entry.Tau_idDeepTau2017v2p1VSmu[j]) & mt['tau_vMu'] > 0 :
                if printOn : print("        fail DeepTau vs.  mu={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSmu[j])))
                continue
            
            tau_eta, tau_phi = entry.Tau_eta[j], entry.Tau_phi[j]
            dPhi = min(abs(tau_phi-mu_phi),2.*pi-abs(tau_phi-mu_phi))
            DR = sqrt(dPhi**2 + (tau_eta-mu_eta)**2) # tau(mu) vs. tau(h)
            if DR < mt['mt_DR']:
                if printOn : print("        fail mtDR DR={0:f} for tau={1:d}".format(DR, j))
                continue
            DR0 = lTauDR(tau_eta, tau_phi, pairList[0]) #l1 vs. tau(h)
            DR1 = lTauDR(tau_eta, tau_phi, pairList[1]) #l2 vs. tau(h)
            if DR0 < mt['mt_DR'] or DR1 < mt['mt_DR']:
                if printOn : print("        fail DR  DR0={0:f} DR1={1:f} for tau={2:i}, mu={3:d}".format(DR0,DR1, j ))
                continue
            if printOn: print("        Tau j={0:d} passes all cuts.".format(j))
            muTauPairs.append([i,j])

    return muTauPairs


def compareMuTauPair(entry,pair1,pair2) :
    # a return value of True means that pair2 is "better" than pair 1 
    i1, i2, j1, j2 = pair1[0], pair2[0], pair1[1], pair2[1]
    if entry.Muon_pfRelIso04_all[i2]  <  entry.Muon_pfRelIso04_all[i1] : return True
    if entry.Muon_pfRelIso04_all[i2] ==  entry.Muon_pfRelIso04_all[i1] :
        if entry.Muon_pt[i2] >  entry.Muon_pt[i1] : return True
        if entry.Muon_pt[i2] == entry.Muon_pt[i1] :
            if entry.Tau_rawDeepTau2017v2p1VSjet[j2] > entry.Tau_rawDeepTau2017v2p1VSjet[j1] : return True   
            if entry.Tau_rawDeepTau2017v2p1VSjet[j2] == entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
                if entry.Tau_pt[j2] > entry.Tau_pt[j1] : return True

    return False

def compareMuTauPairvspT(entry,tauPairList, printOn=False) :

    SumList=[]
    for i in range(0,len(tauPairList)) :
         
        j1, j2 = tauPairList[i][0], tauPairList[i][1] # look at leading pt tau in each pair
        if printOn : print 'appending now', entry.Muon_pt[j1] + entry.Tau_pt[j2], j1, j2, tauPairList[i]
        SumList.append(entry.Muon_pt[j1] + entry.Tau_pt[j2])
    
    maxI=SumList.index(max(SumList))

    return maxI


def getBestMuTauPair(entry,cat='mt',pairList=[],printOn=False) :

    # form all possible pairs that satisfy DR requirement
    if printOn : print("Entering getBestMuTauPair()") 
    tauPairList = getMuTauPairs(entry,cat=cat,pairList=pairList,printOn=printOn) 


    if len(tauPairList) == 0 : 
        if printOn : print 'failed to find good MuTau Pair', cat
        return []

    
    maxI= compareMuTauPairvspT(entry, tauPairList, printOn)
    tauPairList=tauPairList[maxI]

    return tauPairList


def getEMuTauPairs(entry,cat='em',pairList=[],printOn=False) :
    """ tauFun.getEMuTauPairs(): returns a list of suitable
                                 H-> tau(mu) + tau(ele) cands 
    """

    if printOn : print("Entering getEMuTauPairs() nMuon={0:d} nElectron={1:d}".format(entry.nMuon,entry.nElectron)) 
    if entry.nMuon < 1 or entry.nElectron < 1: return []
    if cat == 'mmem' and entry.nMuon < 3:      return []
    if cat == 'eeem' and entry.nElectron < 3:  return []

    elmuTauPairs = []
    em = selections['em'] # selections for H->tau(ele)+tau(mu)
    for i in range(entry.nMuon):

        # selections for tau(mu)
        if printOn : print("Muon i={0:d}".format(i))
        if em['mu_ID']:
            if not (entry.Muon_mediumId[i] or entry.Muon_tightId[i]) :
                if printOn : print("    failed muID={0}".format(entry.Muon_mediumId[i]))
                continue

        if em['mu_type']:
            if not (entry.Muon_isGlobal[i] or entry.Muon_isTracker[i]) :
                if printOn : print("    fail mu_type Global or Tracker={0}".format(entry.Muon_isGlobal[i]))
                continue
        if abs(entry.Muon_dxy[i]) > em['mu_dxy']:
            if printOn : print("    failed dxy={0:f}".format(entry.Muon_dxy[i]))
            continue
        if abs(entry.Muon_dz[i]) > em['mu_dz']:
            if printOn : print("    failed dz={0:f}".format(entry.Muon_dz[i]))
            continue
        mu_eta, mu_phi = entry.Muon_eta[i], entry.Muon_phi[i] 
        if entry.Muon_pt[i] < em['mu_pt']:
            if printOn : print("    failed pt={0:f}".format(entry.Muon_pt[i]))
            continue
        if abs(mu_eta) > em['mu_eta']:
            if printOn : print("    failed eta={0:f}".format(entry.Muon_eta[i]))
            continue   
        if em['mu_iso_f'] and entry.Muon_pfRelIso04_all[i] > em['mu_iso']:
            if printOn : print("    failed iso={0:f}".format(entry.Muon_pfRelIso04_all[i]))
            continue 
        
        DR0 = lTauDR(mu_eta,mu_phi,pairList[0]) #l1 vs. tau(mu)
        DR1 = lTauDR(mu_eta,mu_phi,pairList[1]) #l2 vs. tau(mu)
        if DR0 < em['ll_DR'] or DR1 < em['ll_DR']:
            if printOn : print("    failed DR  DR0={0:f} DR1={1:f}".format(DR0,DR1))
            continue
                        
        for j in range(entry.nElectron):
           
            # selections for tau(ele)
            if printOn: print("    electron={0:d}".format(j))
            if abs(entry.Electron_dxy[j]) > em['ele_dxy']:
                if printOn : print("        failed dxy={0:f}".format(entry.Electron_dxy[j]))
                continue
            if abs(entry.Electron_dz[j]) > em['ele_dz']:
                if printOn : print("        failed dz={0:f}".format(entry.Electron_dz[j]))
                continue
            ele_eta, ele_phi = entry.Electron_eta[j], entry.Electron_phi[j] 
            if entry.Electron_pt[j] < em['ele_pt']:
                if printOn : print("        failed pt={0:f}".format(entry.Electron_pt[j]))
                continue
            if abs(ele_eta) > em['ele_eta']:
                if printOn : print("        failed eta={0:f}".format(entry.Electron_eta[j]))
                continue
            if ord(entry.Electron_lostHits[j]) > em['ele_lostHits']:
                if printOn : print("        failed lost hits={0:d}".format(entry.Electron_lostHits[j]))
                continue 
            if em['ele_convVeto']:
                if not entry.Electron_convVeto[j]:
                    if printOn : print("        failed conv. veto={0}".format(entry.Electron_convVeto[j]))
                    continue
            if em['ele_ID']:    
                if not entry.Electron_mvaFall17V2noIso_WP90[j]:
                    if printOn : print("        failed mvaWP90={0}".format(entry.entry.Electron_mvaFall17V2noIso_WP90[j]))
                    continue
            if em['ele_iso_f'] and entry.Electron_pfRelIso03_all[j] > em['ele_iso']:
                if printOn : print("        failed iso={0:f}".format(entry.Electron_pfRelIso03_all[j]))
                continue

            dPhi = min(abs(mu_phi-ele_phi),2.*pi-abs(mu_phi-ele_phi))
            DR = sqrt(dPhi**2 + (mu_eta-ele_eta)**2) # tau(mu) vs. tau(ele)
            if DR < em['em_DR']:
                if printOn : print("        failed emDR={0:f}".format(DR))
                continue
            DR0 = lTauDR(ele_eta,ele_phi,pairList[0]) # l1 vs. tau(ele) 
            DR1 = lTauDR(ele_eta,ele_phi,pairList[1]) # l2 vs. tau(ele)
            if DR0 < em['ll_DR'] or DR1 < em['ll_DR']:
                if printOn : print("        failed ltDR DR0={0:f} DR1={1:f}".format(DR0,DR1))
                continue
            if printOn : print("        found a good pair i={0:i}, j={1:i}".format(i,j))
            elmuTauPairs.append([j,i])

    return elmuTauPairs

'''
def compareEMuTauPair(entry,pair1,pair2) :
    # a return value of True means that pair2 is "better" than pair 1 
    i1, i2, j1, j2 = pair1[0], pair2[0], pair1[1], pair2[1]
    #if entry.Electron_mvaFall17Iso[i2]  < entry.Electron_mvaFall17Iso[i2] : return True
    if entry.Electron_pfRelIso03_all[i2]  < entry.Electron_pfRelIso03_all[i1] : return True
    #if entry.Electron_mvaFall17Iso[i2] == entry.Electron_mvaFall17Iso[i2] :
    if entry.Electron_pfRelIso03_all[i1] == entry.Electron_mvaFall17V2noIso_WP90[i2] : 
        if entry.Electron_pt[i2]  > entry.Electron_pt[i1] : return True 
        if entry.Electron_pt[i2] == entry.Electron_pt[i1] : 
            if entry.Muon_pt[j2] < entry.Muon_pt[j1] : return True   
    return False 
'''
def compareEMuPairvspT(entry,tauPairList,printOn=False) :

    SumList=[]
    for i in range(0,len(tauPairList)) :
         
        j1, j2 = tauPairList[i][0], tauPairList[i][1] # look at leading pt tau in each pair
        if printOn : print 'appending now', entry.Electron_pt[j1] + entry.Muon_pt[j2], j1, j2, tauPairList[i]
        SumList.append(entry.Electron_pt[j1] + entry.Muon_pt[j2])

    
    maxI=SumList.index(max(SumList))

    return maxI




def compareEMuTauPair(entry,pair1,pair2) :
    # a return value of True means that pair2 is "better" than pair 1 
    i1, i2, j1, j2 = pair1[0], pair2[0], pair1[1], pair2[1]
    if entry.Muon_pfRelIso04_all[j2]  < entry.Muon_pfRelIso04_all[j1] : return True
    if entry.Muon_pfRelIso04_all[j1] == entry.Muon_pfRelIso04_all[j2] : 
	if entry.Muon_pt[j2]  > entry.Muon_pt[j1] : return True 
	if entry.Muon_pt[j2] == entry.Muon_pt[j1] : 
	    if entry.Electron_pt[i2] < entry.Electron_pt[i1] : return True   
    return False 




def getBestEMuTauPair(entry,cat,pairList=[],printOn=False) :

    if printOn : print("Entering getBestEMuTauPair")
    # form all possible pairs that satisfy DR requirement
    tauPairList = getEMuTauPairs(entry,cat=cat,pairList=pairList,printOn=printOn) 

    # Sort the pair list using a bubble sort
    # The list is not fully sorted, since only the top pairing is needed


    if len(tauPairList) == 0 : 
        if printOn : print 'failed to find good EMu Pair', cat
        return []
  
  
    maxI= compareEMuPairvspT(entry, tauPairList, printOn)
    tauPairList=tauPairList[maxI]

    return tauPairList

def getETauPairs(entry,cat='et',pairList=[],printOn=False) :
    """ tauFun.getETauPairs(): get suitable pairs of 
                               H -> tau(ele) + tau(h) 
    """

    if printOn : print("Entering getETauPairs() nElectron={0:d} nTau={1:d}".format(entry.nElectron,entry.nTau)) 
    if entry.nElectron < 1 or entry.nTau < 1: return []
    if cat == 'eeet' and entry.nElectron < 3: return []
    
    eTauPairs = []
    et = selections['et'] # selections for H->tau(ele)+tau(h)
    for i in range(entry.nElectron) :

        # selections for tau(ele)
        if printOn : print("Electron i={0:d}".format(i))
        if abs(entry.Electron_dxy[i]) > et['ele_dxy']:
            if printOn : print("    failed dxy={0:f}".format(entry.Electron_dxy[i]))
            continue
        if abs(entry.Electron_dz[i]) > et['ele_dz']:
            if printOn : print("    failed dz={0:f}".format(entry.Electron_dz[i]))
            continue
        if et['ele_ID']:
            if not entry.Electron_mvaFall17V2noIso_WP90[i]:
                if printOn : print("    failed mva={0}".format(entry.Electron_mvaFall17V2noIso_WP90[i]))
                continue
        if ord(entry.Electron_lostHits[i]) > et['ele_lostHits']:
            if printOn : print("    failed losthits={0:s}".format(entry.Electron_lostHits[i]))
            continue 
        if et['ele_convVeto']:
            if not entry.Electron_convVeto[i]:
                if printOn : print("    failed convVeto={0}".format(entry.Electron_convVeto[i]))
                continue
        if et['ele_iso_f'] :
            if entry.Electron_pfRelIso03_all[i] > et['ele_iso']:
                if printOn : print("    failed convVeto={0:f}".format(entry.Electron_pfRelIso03_all[i]))
                continue

        if entry.Electron_pt[i] < et['ele_pt']:
            if printOn : print("    failed pt={0:f}".format(entry.Electron_pt[i]))
            continue
        
        ele_eta, ele_phi = entry.Electron_eta[i], entry.Electron_phi[i]
        if abs(ele_eta) > et['ele_eta']:
            if printOn : print("    failed eta={0:f}".format(entry.Electron_eta[i]))
            continue
        
        DR0 = lTauDR(ele_eta,ele_phi,pairList[0]) # l1 vs. tau(ele)
        DR1 = lTauDR(ele_eta,ele_phi,pairList[1]) # l2 vs. tau(ele)
        if DR0 < et['ll_DR'] or DR1 < et['ll_DR']:
            if printOn : print("    failed ltDR DR0={0:f} DR1={1:f}".format(DR0,DR1))
            continue
            
        for j in range(entry.nTau) :

            # selections for tau(h)
            if printOn : print("    tau={0:d}".format(j))
            if entry.Tau_pt[j] < et['tau_pt']:
                if printOn : print("        failed pt={0:f}".format(entry.Tau_pt[j]))
                continue
            if abs(entry.Tau_eta[j]) > et['tau_eta']:
                if printOn : print("        failed eta={0:f}".format(entry.Tau_eta[j]))
                continue

            if et['tau_ID'] and not entry.Tau_idDecayModeNewDMs[j]:
                if printOn : print("        failed idDecayMode={0}".format(entry.idDecayModeNewDMs[j]))
                continue
	    if  et['tau_decayMode'] and (entry.Tau_decayMode[j] == 5 or entry.Tau_decayMode[j] == 6) :
                if printOn : print("        failed DecayMode={0}".format(entry.Tau_decayMode[j]))
                continue
            if abs(entry.Tau_dz[j]) > et['tau_dz']:
                if printOn : print("        failed dz={0:f}".format(entry.Tau_dz[j]))
                continue
            if abs(entry.Tau_charge[j]) != 1:
                if printOn : print("        failed tauCharge={0:d}".format(entry.Tau_charge[j]))
                continue

            '''
	    if ord(entry.Tau_idAntiMu[j]) <= et['tau_antiMu']: continue
            if ord(entry.Tau_idAntiEle[j]) <= et['tau_antiEle']: continue
            if cat == 'eeet':
                if ord(entry.Tau_idAntiEle[j]) < et['tau_eeet_antiEle']: continue
	    '''

            '''
            if not ord(entry.Tau_idDeepTau2017v2p1VSjet[j]) & 16 > 0 : continue
	    if not ord(entry.Tau_idDeepTau2017v2p1VSe[j]) & 32 > 0 : continue
            if not ord(entry.Tau_idDeepTau2017v2p1VSmu[j]) & 1 > 0 : continue
            '''
            
            if et['tau_vJet'] > 0  and not ord(entry.Tau_idDeepTau2017v2p1VSjet[j]) & et['tau_vJet'] > 0 :
                if printOn : print("        fail DeepTau vs. Jet={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSjet[j])))
                continue
	    if et['tau_vEle'] > 0 and not ord(entry.Tau_idDeepTau2017v2p1VSe[j]) & et['tau_vEle'] > 0 :
                if printOn : print("        fail DeepTau vs. ele={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSe[j])))
                continue
            if et['tau_vMu'] > 0 and not ord(entry.Tau_idDeepTau2017v2p1VSmu[j]) & et['tau_vMu'] > 0 :
                if printOn : print("        fail DeepTau vs.  mu={0:d}".format(ord(entry.Tau_idDeepTau2017v2p1VSmu[j])))
                continue


            tau_eta, tau_phi = entry.Tau_eta[j], entry.Tau_phi[j]
            dPhi = min(abs(tau_phi-ele_phi),2.*pi-abs(tau_phi-ele_phi))
            DR = sqrt(dPhi**2 + (tau_eta-ele_eta)**2)
            if DR < et['tt_DR']:
                if printOn : print("        failed ttDR={0:f}".format(DR))
                continue # tau(ele) vs. tau(h)
            DR0 = lTauDR(tau_eta,tau_phi,pairList[0]) # l1 vs. tau(h)
            DR1 = lTauDR(tau_eta,tau_phi,pairList[1]) # l2 vs. tau(h)
            if DR0 < et['tt_DR'] or DR1 < et['tt_DR']:
                if printOn : print("        failed ltDR DR0={0:f} DR1={1:f}".format(DR0,DR1))
                continue
            eTauPairs.append([i,j])

    return eTauPairs

def compareETauPairvspT(entry,tauPairList, printOn=False) :

    SumList=[]
    for i in range(0,len(tauPairList)) :
         
        j1, j2 = tauPairList[i][0], tauPairList[i][1] # look at leading pt tau in each pair
        if printOn : print 'appending now', entry.Electron_pt[j1] + entry.Tau_pt[j2], j1, j2, tauPairList[i]
        SumList.append(entry.Electron_pt[j1] + entry.Tau_pt[j2])

    
    maxI=SumList.index(max(SumList))

    return maxI


def compareETauPair(entry,pair1,pair2) :
    # a return value of True means that pair2 is "better" than pair 1 
    i1, i2, j1, j2 = pair1[0], pair2[0], pair1[1], pair2[1]
    if entry.Electron_pfRelIso03_all[i2]  < entry.Electron_pfRelIso03_all[i1] : return True
    if entry.Electron_pfRelIso03_all[i1] == entry.Electron_pfRelIso03_all[i2] : 
        if entry.Electron_pt[i2]  > entry.Electron_pt[i1] : return True 
        if entry.Electron_pt[i2] == entry.Electron_pt[i1] : 
            if entry.Tau_rawDeepTau2017v2p1VSjet[j2] > entry.Tau_rawDeepTau2017v2p1VSjet[j1] : return True   
            if entry.Tau_rawDeepTau2017v2p1VSjet[j2] == entry.Tau_rawDeepTau2017v2p1VSjet[j1] :
                if entry.Tau_pt[j2] > entry.Tau_pt[j1] : return True
    return False 

def getBestETauPair(entry,cat,pairList=[],printOn=False) :

    if printOn : print("Entering getBestETauPair")
    # form all possible pairs that satisfy DR requirement
    tauPairList = getETauPairs(entry,cat=cat,pairList=pairList,printOn=printOn) 


    if len(tauPairList) == 0 : 
        if printOn : print 'failed to find good ETau Pair', cat
        return []


    maxI= compareETauPairvspT(entry, tauPairList, printOn)
    tauPairList=tauPairList[maxI]

    return tauPairList



def getEEPairs(entry, cat='ee', pairList=[], printOn=False):
    
    if printOn: print ("Entering getEEPairs(): nElectron={0:d}".format(entry.nElectron))

    # need a sufficient number of leptons
    if entry.nElectron < 2: return []
    if cat == 'eeee' and entry.nElectron < 4: return []
    
    selected_elecs = []
    ee = selections['et'] # impose selections for tau(ele) on each electron
    
    # get a list of suitable electrons
    for i in range(entry.nElectron):
        
        if printOn: print("Electron i={0:d}".format(i))
        
        if abs(entry.Electron_dxy[i]) > ee['ele_dxy']:
            if printOn: print("\t failed dxy={0:f}".format(entry.Electron_dxy[i]))
            continue
        if abs(entry.Electron_dz[i]) > ee['ele_dz']:
            if printOn: print("\t failed dz={0:f}".format(entry.Electron_dz[i]))
            continue
        if ee['ele_ID']:
            if not entry.Electron_mvaFall17V2noIso_WP90[i]:
                if printOn: print("\t failed mva={0}".format(entry.Electron_mvaFall17V2noIso_WP90[i]))
                continue
        if ord(entry.Electron_lostHits[i]) > ee['ele_lostHits']:
            if printOn: print("\t failed losthits={0}".format(entry.Electron_lostHits[i]))
            continue
        if ee['ele_convVeto']:
            if not entry.Electron_convVeto[i]:
                if printOn: print("\t failed convVeto={0}".format(entry.Electron_convVeto[i]))
                continue
        if ee['ele_iso_f']:
            if entry.Electron_pfRelIso03_all[i] > ee['ele_iso']:
                if printOn: print("\t failed convVeto={0:f}".format(entry.Electron_pfRelIso03_all[i]))
                continue
        if entry.Electron_pt[i] < ee['ele_pt']:
            if printOn: print("\t failed pt={0:f}".format(entry.Electron_pt[i]))
            continue

        ele_eta, ele_phi = entry.Electron_eta[i], entry.Electron_phi[i]
        if abs(ele_eta) > ee['ele_eta']:
            if printOn: print("\t failed eta={0:f}".format(entry.Electron_eta[i]))
            continue
        
        DR0 = lTauDR(ele_eta,ele_phi,pairList[0]) # l1 vs. e1
        DR1 = lTauDR(ele_eta,ele_phi,pairList[1]) # l2 vs. e2
        if DR0 < ee['ll_DR'] or DR1 < ee['ll_DR']:
            if printOn: print("\t failed DR(l_i,e) check: DR0={0:f} DR1={1:f}".format(DR0,DR1))
            continue

        selected_elecs.append(i)

    # pair up suitable electrons
    ee_pairs = []
    for i in selected_elecs:
        for j in selected_elecs:
            
            if (j <= i): continue
            if printOn: print("\t considering (i,j)=({0:d}, {1:d})".format(i, j))
            
            e1_eta, e1_phi = entry.Electron_eta[i], entry.Electron_phi[i]
            e2_eta, e2_phi = entry.Electron_eta[j], entry.Electron_eta[j]
            dPhi = min(abs(e1_phi-e2_phi), 2.*pi-abs(e1_phi-e2_phi))
            DR = sqrt(dPhi**2 + (e1_eta-e2_eta)**2)

            if DR < ee['tt_DR']:
                if printOn: print("\t failed eeDR={0:f}".format(DR))
                continue
            
            # store in leading, sub-leading order
            if (entry.Electron_pt[i] > entry.Electron_pt[j]):
                ee_pairs.append([i,j])
            else: ee_pairs.append([j,i])

    return ee_pairs


def compareEEPairs(entry, pair1, pair2):
    i1, i2, j1, j2 = pair1[0], pair2[0], pair1[1], pair2[1]
    
    if entry.Electron_pfRelIso03_all[i2]  < entry.Electron_pfRelIso03_all[i1]:
        if entry.Electron_pfRelIso03_all[j2] <= entry.Electron_pfRelIso03_all[j1]:
            return True

    if entry.Electron_pfRelIso03_all[j2] < entry.Electron_pfRelIso03_all[j1]:
         if entry.Electron_pfRelIso03_all[i2]  <= entry.Electron_pfRelIso03_all[i1]:
             return True

    if entry.Electron_pfRelIso03_all[i1] == entry.Electron_pfRelIso03_all[i2]:
        if entry.Electron_pfRelIso03_all[j1] == entry.Electron_pfRelIso03_all[j2]:
            if (entry.Electron_pt[i2]+entry.Electron_pt[j2]) > (entry.Electron_pt[i1]+entry.Electron_pt[j1]):
                return True
                
    return False


def getBestEEPair(entry, cat, pairList=[], printOn=False):
    
    if printOn: print("Entering getBestEEPair")
    
    ee_pairs = getEEPairs(entry, cat=cat, pairList=pairList, printOn=printOn)
    for i in range(len(ee_pairs)-1, 0, -1):
        if compareEEPairs(entry, ee_pairs[i], ee_pairs[i-1]):
            ee_pairs[i-1], ee_pairs[i] = ee_pairs[i], ee_pairs[i-1]

    if len(ee_pairs) == 0: return []
    return ee_pairs[0]


def getMuMuPairs(entry, cat='mm', pairList=[], printOn=False):
    
    if entry.nMuon < 2:
        if printOn: print ("Entering getMuMuPairs, failing nMuon={0:d}".format(entry.nMuon))
        return []
    if cat == 'mmmm' and entry.nMuon < 4: return []

    if printOn: print("Entering tauFun.getMuMuPairs() nMuon={0:d}".format(entry.nMuon))

    mm = selections['mt'] # inherit selections for tau(mu)
    selected_muons = []
    for i in range(entry.nMuon):
        
        if mm['mu_type']:
            if not (entry.Muon_isGlobal[i] or entry.Muon_isTracker[i]) :
                if printOn: print("\t fail mu_type Global or Tracker={0}".format(entry.Muon_isGlobal[i]))
                continue
        if mm['mu_ID']:
            if not (entry.Muon_mediumId[i] or entry.Muon_tightId[i]) :
                if printOn: print("\t fail mu_ID mediumId={0}".format(entry.Muon_mediumId[i]))
                continue
        if abs(entry.Muon_dxy[i]) > mm['mu_dxy']:
            if printOn: print("\t fail mu_dxy={0:f}".format(entry.Muon_dxy[i]))
            continue
        if abs(entry.Muon_dz[i]) > mm['mu_dz']:
            if printOn: print("\t fail mu_dz={0:f}".format(entry.Muon_dz[i]))
            continue

        mu_eta, mu_phi = entry.Muon_eta[i], entry.Muon_phi[i]
        if entry.Muon_pt[i] < mm['mu_pt']:
            if printOn: print("\t fail mu_pt={0:f}".format(entry.Muon_pt[i]))
            continue
        if abs(mu_eta) > mm['mu_eta']:
            if printOn: print("\t fail mu_eta={0:f}".format(entry.Muon_eta[i]))
            continue
        if  mm['mu_iso_f'] and entry.Muon_pfRelIso04_all[i] > mm['mu_iso']:
            if printOn: print("\t fail mu_iso={0:f}".format(entry.Muon_pfRelIso04_all[i]))
            continue

        DR0 = lTauDR(mu_eta,mu_phi,pairList[0]) # l1 vs. m
        DR1 = lTauDR(mu_eta,mu_phi,pairList[1]) # l2 vs. m
        if DR0 < mm['ll_DR'] or DR1 < mm['ll_DR']:
            if printOn : print("\t fail muon DR  DR0={0:f} DR1={1:f}".format(DR0,DR1))
            continue
        if printOn : print("\t Good muon i={0:d}".format(i))
    
        selected_muons.append(i)
        
    # pair up the selected muons
    mm_pairs = []    
    for i in selected_muons:
        for j in selected_muons:
           
            if j <= i: continue
            if printOn: print("\t considering (i,j)=({0:d}, {1:d})".format(i, j))
            
            m1_eta, m1_phi = entry.Muon_eta[i], entry.Muon_phi[i]
            m2_eta, m2_phi = entry.Muon_eta[j], entry.Muon_phi[j]
            
            dPhi = min(abs(m1_phi-m2_phi), 2.*pi-abs(m1_phi-m2_phi))
            DR = sqrt(dPhi**2 + (m1_eta-m2_eta)**2)
            if DR < mm['mt_DR']:
                if printOn: print("\t fail mmDR DR={0:f}".format(DR))
                continue
            
            # store in [leading, sub-leading] order
            if entry.Muon_pt[i] > entry.Muon_pt[j]: 
                mm_pairs.append([i,j])
            else: mm_pairs.append([j,i])
            
    return mm_pairs


def compareMuMuPairs(entry, pair1, pair2):
    i1, i2, j1, j2 = pair1[0], pair2[0], pair1[1], pair2[1]

    if entry.Muon_pfRelIso04_all[i2]  < entry.Muon_pfRelIso04_all[i1]:
        if entry.Muon_pfRelIso04_all[j2] <= entry.Muon_pfRelIso04_all[j1]:
            return True

    if entry.Muon_pfRelIso04_all[j2] < entry.Muon_pfRelIso04_all[j1]:
         if entry.Muon_pfRelIso04_all[i2]  <= entry.Muon_pfRelIso04_all[i1]:
             return True

    if entry.Muon_pfRelIso04_all[i1] == entry.Muon_pfRelIso04_all[i2]:
        if entry.Muon_pfRelIso04_all[j1] == entry.Muon_pfRelIso04_all[j2]:
            if (entry.Muon_pt[i2]+entry.Muon_pt[j2]) > (entry.Muon_pt[i1]+entry.Muon_pt[j1]):
                return True
    
    return False


def getBestMuMuPair(entry, cat='mm', pairList=[], printOn=False):
    
    # form all possible pairs that satisfy DR requirement
    if printOn: print("Entering getBestMuMuPair()")
    mm_pairs = getMuMuPairs(entry,cat=cat,pairList=pairList,printOn=printOn)

    for i in range(len(mm_pairs)-1,0,-1) :
        if compareMuMuPairs(entry, mm_pairs[i], mm_pairs[i-1]) :
            mm_pairs[i-1], mm_pairs[i] = mm_pairs[i], mm_pairs[i-1]

    if len(mm_pairs) == 0 : return []
    return mm_pairs[0]


# select a muon for the Z candidate
def goodMuon(entry, j ):
    """ tauFun.goodMuon(): select good muons
                           for Z -> mu + mu
    """
    
    mm = selections['mm'] # selections for Z->mumu
    if entry.Muon_pt[j] < mm['mu_pt']: return False
    if abs(entry.Muon_eta[j]) > mm['mu_eta']: return False
    if mm['mu_iso_f'] and entry.Muon_pfRelIso04_all[j] >  mm['mu_iso']: return False
    if mm['mu_ID'] :
        if not (entry.Muon_mediumId[j] or entry.Muon_tightId[j]): return False
    if mm['mu_ID'] and not entry.Muon_looseId[j] : return False
    if abs(entry.Muon_dxy[j]) > mm['mu_dxy']: return False 
    if abs(entry.Muon_dz[j]) > mm['mu_dz']: return False
    if mm['mu_type'] :
        if not (entry.Muon_isGlobal[j] or entry.Muon_isTracker[j]) : return False
             
    return True 

def makeGoodMuonList(entry) :
    goodMuonList = []
    for i in range(entry.nMuon) :
        if goodMuon(entry, i) : goodMuonList.append(i)
    #print("In tauFun.makeGoodMuonList = {0:s}".format(str(goodMuonList)))
    return goodMuonList

# select an electron for the Z candidate
def goodElectron(entry, j) :
    """ tauFun.goodElectron(): select good electrons 
                               for Z -> ele + ele
    """
    ee = selections['ee'] # selections for Z->ee
    if entry.Electron_pt[j] < ee['ele_pt']: return False
    if abs(entry.Electron_eta[j]) > ee['ele_eta']: return False
    if abs(entry.Electron_dxy[j]) > ee['ele_dxy']: return False
    if abs(entry.Electron_dz[j]) > ee['ele_dz']: return False
    if ord(entry.Electron_lostHits[j]) > ee['ele_lostHits']: return False
    if ee['ele_iso_f'] and entry.Electron_pfRelIso03_all[j] >  ee['ele_iso']: return False
    if ee['ele_convVeto']:
        if not entry.Electron_convVeto[j]: return False
    if ee['ele_ID']:
        if not entry.Electron_mvaFall17V2noIso_WP90[j] : return False

    return True 

def makeGoodElectronList(entry) :
    goodElectronList = []
    for i in range(entry.nElectron) :
        if goodElectron(entry, i) : goodElectronList.append(i)
    return goodElectronList


##############
def goodMuonExtraLepton(entry, j):
    """ tauFun.goodMuon(): select good muons
                           for Z -> mu + mu
    """
    
    mm = selections['mextra'] # selections for Z->mumu
    if entry.Muon_pt[j] < mm['mu_pt']: return False
    if abs(entry.Muon_eta[j]) > mm['mu_eta']: return False
    if mm['mu_iso_f'] and entry.Muon_pfRelIso04_all[j] >  mm['mu_iso']: return False
    if mm['mu_ID'] and not (entry.Muon_mediumId[j] or entry.Muon_tightId[j]): return False
    if abs(entry.Muon_dxy[j]) > mm['mu_dxy']: return False 
    if abs(entry.Muon_dz[j]) > mm['mu_dz']: return False
    if mm['mu_type'] :
        if not (entry.Muon_isGlobal[j] or entry.Muon_isTracker[j]) : return False
             
    return True 

def makeGoodMuonListExtraLepton(entry, listMu) :
    goodExtraMuonList = []
    for i in range(entry.nMuon) :
        if i not in listMu and goodMuonExtraLepton(entry, i) : goodExtraMuonList.append(i)
    #print("In tauFun.makeGoodMuonList = {0:s}".format(str(goodMuonList)))
    return goodExtraMuonList

# select an electron for the Z candidate
def goodElectronExtraLepton(entry, j) :
    """ tauFun.goodElectron(): select good electrons 
                               for Z -> ele + ele
    """
    ee = selections['eextra'] # selections for Z->ee
    if entry.Electron_pt[j] < ee['ele_pt']: return False
    if abs(entry.Electron_eta[j]) > ee['ele_eta']: return False
    if abs(entry.Electron_dxy[j]) > ee['ele_dxy']: return False
    if abs(entry.Electron_dz[j]) > ee['ele_dz']: return False
    if ord(entry.Electron_lostHits[j]) > ee['ele_lostHits']: return False
    if ee['ele_iso_f'] and entry.Electron_pfRelIso03_all[j] >  ee['ele_iso']: return False
    if ee['ele_convVeto']:
        if not entry.Electron_convVeto[j]: return False
    if ee['ele_ID']:
        if not entry.Electron_mvaFall17V2noIso_WP90[j] : return False

    return True 

def makeGoodElectronListExtraLepton(entry, listEl) :
    goodExtraElectronList = []
    for i in range(entry.nElectron) :
        if i not in listEl and goodElectronExtraLepton(entry, i) : goodExtraElectronList.append(i)
    return goodExtraElectronList

def eliminateCloseTauAndLepton(entry, goodElectronList, goodMuonList, goodTauList) :

    badMuon, badElectron, badTau = [], [], []
    # check tau vs tau
    for tau1 in goodTauList :
        for tau2 in goodTauList :
            if tau1 == tau2 : continue
            dEta = abs(entry.Tau_eta[tau1] - entry.Tau_eta[tau2])
            if dEta > 0.3 : continue
            dPhi = abs(entry.Tau_phi[tau1] - entry.Tau_phi[tau2])
            if dPhi > 0.3 : continue
            if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
            if not (tau1 in badTau) and entry.Tau_pt[tau1] < entry.Tau_pt[tau2] : badTau.append(tau1)
            if not (tau2 in badTau) and entry.Tau_pt[tau1] > entry.Tau_pt[tau2] : badTau.append(tau2)

        #check tau vs mu
        for mu2 in goodMuonList :
            dEta = abs(entry.Tau_eta[tau1] - entry.Muon_eta[mu2])
            if dEta > 0.3 : continue
            dPhi = abs(entry.Tau_phi[tau1] - entry.Muon_phi[mu2])
            if dPhi > 0.3 : continue
            if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
            if not (tau1 in badTau) and entry.Tau_pt[tau1] < entry.Muon_pt[mu2] : badTau.append(tau1)
            if not (mu2 in badMuon) and entry.Tau_pt[tau1] > entry.Muon_pt[mu2] : badMuon.append(mu2)

        #check tau vs el
        for e2 in goodElectronList :
            dEta = abs(entry.Tau_eta[tau1] - entry.Electron_eta[e2])
            if dEta > 0.3 : continue
            dPhi = abs(entry.Tau_phi[tau1] - entry.Electron_phi[e2])
            if dPhi > 0.3 : continue
            if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
            if not (tau1 in badTau) : badTau.append(tau1)
            if not (e2 in badElectron) : badElectron.append(e2)
            if not (tau1 in badTau) and entry.Tau_pt[tau1] < entry.Electron_pt[e2] : badTau.append(tau1)
            if not (e2 in badElectron) and entry.Tau_pt[tau1] > entry.Electron_pt[e2] : badElectron.append(e2)

    # check el vs el        
    for e1 in goodElectronList :
        for e2 in goodElectronList :
            if e1 == e2 : continue 
            dEta = abs(entry.Electron_eta[e1] - entry.Electron_eta[e2])
            if dEta > 0.3 : continue
            dPhi = abs(entry.Electron_phi[e1] - entry.Electron_phi[e2])
            if dPhi > 0.3 : continue
            if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
            if not (e1 in badElectron) and entry.Electron_pt[e1] < entry.Electron_pt[e2] : badElectron.append(e1)
            if not (e2 in badElectron) and entry.Electron_pt[e1] > entry.Electron_pt[e2] : badElectron.append(e2)

    #check mu vs mu and vs el
    for mu1 in goodMuonList :
        for mu2 in goodMuonList :
            if mu1 == mu2 : continue
            dEta = abs(entry.Muon_eta[mu1] - entry.Muon_eta[mu2])
            if dEta > 0.3 : continue
            dPhi = abs(entry.Muon_phi[mu1] - entry.Muon_phi[mu2])
            if dPhi > 0.3 : continue
            if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
            if not (mu1 in badMuon) and entry.Muon_pt[mu1] < entry.Muon_pt[mu2] : badMuon.append(mu1)
            if not (mu2 in badMuon) and entry.Muon_pt[mu1] > entry.Muon_pt[mu2] : badMuon.append(mu2)


        for e2 in goodElectronList :
            dEta = abs(entry.Muon_eta[mu1] - entry.Electron_eta[e2])
            if dEta > 0.3 : continue
            dPhi = abs(entry.Muon_phi[mu1] - entry.Electron_phi[e2])
            if dPhi > 0.3 : continue
            if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
            if not (mu1 in badMuon) and entry.Muon_pt[mu1] < entry.Electron_pt[e2] : badMuon.append(mu1)
            if not (e2 in badElectron) and entry.Muon_pt[mu1] > entry.Electron_pt[e2] : badElectron.append(e2)



    for bade in badElectron : goodElectronList.remove(bade)
    for badmu in badMuon : goodMuonList.remove(badmu)
    for badtau in badTau : goodTauList.remove(badtau)

    return goodElectronList, goodMuonList, goodTauList


def eliminateCloseLeptons(entry, goodElectronList, goodMuonList) :
    badMuon, badElectron = [], []
    if len(goodMuonList)> 1 :
	for mu1 in goodMuonList :
	    for mu2 in goodMuonList :
		if mu1 == mu2 : continue
		dEta = abs(entry.Muon_eta[mu1] - entry.Muon_eta[mu2])
		if dEta > 0.3 : continue
		dPhi = abs(entry.Muon_phi[mu1] - entry.Muon_phi[mu2])
		if dPhi > 0.3 : continue
		if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
		if not (mu1 in badMuon) and entry.Muon_pt[mu1] < entry.Muon_pt[mu2] : badMuon.append(mu1)
		if not (mu2 in badMuon) and entry.Muon_pt[mu1] > entry.Muon_pt[mu2] : badMuon.append(mu2)

	    for e2 in goodElectronList :
		dEta = abs(entry.Muon_eta[mu1] - entry.Electron_eta[e2])
		if dEta > 0.3 : continue
		dPhi = abs(entry.Muon_phi[mu1] - entry.Electron_phi[e2])
		if dPhi > 0.3 : continue
		if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
		if not (mu1 in badMuon) and entry.Muon_pt[mu1] < entry.Electron_pt[e2] : badMuon.append(mu1)
		if not (e2 in badElectron) and entry.Muon_pt[mu1] > entry.Electron_pt[e2] : badElectron.append(e2)
    if len(goodElectronList)> 1 :        
	for e1 in goodElectronList :
	    for e2 in goodElectronList :
		if e1 == e2 : continue 
		dEta = abs(entry.Electron_eta[e1] - entry.Electron_eta[e2])
		if dEta > 0.3 : continue
		dPhi = abs(entry.Electron_phi[e1] - entry.Electron_phi[e2])
		if dPhi > 0.3 : continue
		if sqrt(dEta*dEta + dPhi*dPhi) > 0.3 : continue
		if not (e1 in badElectron) and entry.Electron_pt[e1] < entry.Electron_pt[e2] : badElectron.append(e1)
		if not (e2 in badElectron) and entry.Electron_pt[e1] > entry.Electron_pt[e2] : badElectron.append(e2)

    for bade in badElectron : goodElectronList.remove(bade)
    for badmu in badMuon : goodMuonList.remove(badmu)

    return goodElectronList, goodMuonList

def findETrigger(goodElectronList,entry,era):
    EltrigList =[]
    nElectron = len(goodElectronList)
    
    if nElectron > 1 :
	if era == '2016' and not entry.HLT_Ele27_WPTight_Gsf : return EltrigList
	if era == '2017' and not entry.HLT_Ele35_WPTight_Gsf : return EltrigList
        for i in range(nElectron) :
	    
            ii = goodElectronList[i]
            if era == '2016' and entry.Electron_pt[ii] < 29 : continue
            if era == '2017' and entry.Electron_pt[ii] < 37 : continue
            #print("Electron: pt={0:.1f} eta={1:.2f} phi={2:.2f}".format(entry.Electron_pt[ii], entry.Electron_eta[ii], entry.Electron_phi[ii]))
            #e1 = TLorentzVector()
            #e1.SetPtEtaPhiM(entry.Electron_pt[ii],entry.Electron_eta[ii],entry.Electron_phi[ii],0.0005)

            for iobj in range(0,entry.nTrigObj) :
	        dR = DRobj(entry.Electron_eta[ii],entry.Electron_phi[ii], entry.TrigObj_eta[iobj], entry.TrigObj_phi[iobj])
                #print("    Trg Obj: eta={0:.2f} phi={1:.2f} dR={2:.2f} bits={3:x}".format(
                    #entry.TrigObj_eta[iobj], entry.TrigObj_phi[iobj], dR, entry.TrigObj_filterBits[iobj]))
		if entry.TrigObj_filterBits[iobj] & 2  and dR < 0.5: ##that corresponds 0 WPTight
		    EltrigList.append(ii)
                    #print "======================= iobj", iobj, "entry.Trig",entry.TrigObj_id[iobj], "Bits", entry.TrigObj_filterBits[iobj]," dR", dR, "electron",i,"ii",ii,entry.TrigObj_id[iobj]

    return EltrigList


def findMuTrigger(goodMuonList,entry,era):
    MutrigList =[]
    nMuon = len(goodMuonList)
    
    if nMuon > 1 :
	if era == '2016' and not entry.HLT_IsoMu24 : return MutrigList
	if era == '2017' and not entry.HLT_IsoMu27 : return MutrigList
        for i in range(nMuon) :
	    

            ii = goodMuonList[i] 
	    if era == '2016' and entry.Muon_pt[ii] < 26 : continue
	    if era == '2017' and entry.Muon_pt[ii] < 29 : continue
            #print("Muon: pt={0:.1f} eta={1:.4f} phi={2:.4f}".format(entry.Muon_pt[ii], entry.Muon_eta[ii], entry.Muon_phi[ii]))
            for iobj in range(0,entry.nTrigObj) :
	        dR = DRobj(entry.Muon_eta[ii],entry.Muon_phi[ii], entry.TrigObj_eta[iobj], entry.TrigObj_phi[iobj])
                #print("    Trg Obj: eta={0:.4f} phi={1:.4f} dR={2:.4f} bits={3:x}".format(
                #    entry.TrigObj_eta[iobj], entry.TrigObj_phi[iobj], dR, entry.TrigObj_filterBits[iobj]))
		if entry.TrigObj_filterBits[iobj] & 8 or entry.TrigObj_filterBits[iobj] & 2 and dR < 0.5: ##that corresponds to Muon Trigger
		    MutrigList.append(ii)
                #print "======================= and === iobj", iobj, entry.TrigObj_id[iobj], "Bits", entry.TrigObj_filterBits[iobj]," dR", dR, "electron",i

    return MutrigList

def ComparepT(El, Mu, entry) :
    if entry.Electron_pt[El] > entry.Muon_pt[Mu] : return True
    else : return False


def findZ(goodElectronList, goodMuonList, entry) :
    mm = selections['mm'] # H->tau(mu)+tau(h) selections
    selpair,pairList, mZ, bestDiff = [],[], 91.19, 99999. 
    nElectron = len(goodElectronList)
    #print 'going in tauFun', goodElectronList, nElectron, entry.event, entry.luminosityBlock, entry.run, bestDiff
    if nElectron > 1 :
        for i in range(nElectron) :
            ii = goodElectronList[i] 
            e1 = TLorentzVector()
            e1.SetPtEtaPhiM(entry.Electron_pt[ii],entry.Electron_eta[ii],entry.Electron_phi[ii],0.0005)
            for j in range(i+1,nElectron) :
                jj = goodElectronList[j]
                #print 'going in tauFun masses', goodElectronList, nElectron, entry.event, entry.luminosityBlock, entry.run, 'for', jj, ii, entry.Electron_charge[ii],  entry.Electron_charge[jj]
                if entry.Electron_charge[ii] != entry.Electron_charge[jj] :
                    e2 = TLorentzVector()
                    e2.SetPtEtaPhiM(entry.Electron_pt[jj],entry.Electron_eta[jj],entry.Electron_phi[jj],0.0005)
                    cand = e1 + e2
                    mass = cand.M()
		    #if mass < 60 or mass > 120 : continue
                    #print 'going in tauFun masses', goodElectronList, nElectron, entry.event, entry.luminosityBlock, entry.run, bestDiff, 'is abs(mass-mZ > bestDiff', abs(mass-mZ), bestDiff, 'for', jj, ii
                    if abs(mass-mZ) < bestDiff :
                        bestDiff = abs(mass-mZ)
                        #print 'masses', bestDiff, mass, entry.Electron_charge[jj], entry.Electron_charge[ii], entry.event, entry.luminosityBlock, entry.run, 'elect', jj, ii, goodElectronList
                        if entry.Electron_charge[ii] > 0. :
                            pairList = [e1,e2]
                            selpair = [ii,jj]
                        else : 
                            pairList = [e2,e1]
                            selpair = [jj,ii]
                           
    nMuon = len(goodMuonList)
    if nMuon > 1 : 
        # find mass pairings
        for i in range(nMuon) :
            ii = goodMuonList[i]
            #if entry.Muon_pfRelIso04_all[ii] >  mm['mu_iso']: continue
            mu1 = TLorentzVector()
            mu1.SetPtEtaPhiM(entry.Muon_pt[ii],entry.Muon_eta[ii],entry.Muon_phi[ii],0.105)
            for j in range(i+1,nMuon) :
                jj = goodMuonList[j]
                if entry.Muon_charge[ii] != entry.Muon_charge[jj] :
                    mu2 = TLorentzVector()
                    mu2.SetPtEtaPhiM(entry.Muon_pt[jj],entry.Muon_eta[jj],entry.Muon_phi[jj],0.105)
                    cand = mu1 + mu2
                    mass = cand.M()
		    #if mass < 60 or mass > 120 : continue
                    if abs(mass-mZ) < bestDiff :
                        bestDiff = abs(mass-mZ)
                        if entry.Muon_charge[ii] > 0. :
                            pairList = [mu1,mu2]
                            selpair = [ii,jj]
                        else :
                            pairList = [mu2,mu1]
                            selpair = [jj,ii]

    # first particle of pair is positive
    #print 'returning', selpair,  'is muon', nMuon, goodMuonList, 'isEl', nElectron, goodElectronList, entry.event, entry.luminosityBlock, entry.run
    return pairList, selpair
                    
                    
def findZmumu(goodMuonList, entry) :
    pairList, mZ, bestDiff = [], 91.19, 99999.     
    nMuon = len(goodMuonList)
    if nMuon < 2 : return pairList 
    # find mass pairings
    for i in range(nMuon) :
        mu1 = TLorentzVector()
        mu1.SetPtEtaPhiM(entry.Muon_pt[i],entry.Muon_eta[i],entry.Muon_phi[i],0.105)
        for j in range(i+1,nMuon) :
            if entry.Muon_charge[i] != entry.Muon_charge[j] :
                mu2 = TLorentzVector()
                mu2.SetPtEtaPhiM(entry.Muon_pt[j],entry.Muon_eta[j],entry.Muon_phi[j],0.105)
                cand = mu1 + mu2
                mass = cand.M()
		#if mass < 60 or mass > 120 : continue
                if abs(mass-mZ) < bestDiff :
                    bestDiff = abs(mass-mZ)
                    pairList.append([mu1,mu2]) 

    return pairList

def findZee(goodElectronList, entry) :
    pairList, mZ, bestDiff = [], 91.19, 99999. 
    nElectron = len(goodElectronList)
    if nElectron < 2 : return pairList 
    # find mass pairings
    for i in range(nElectron) :
        e1 = TLorentzVector()
        e1.SetPtEtaPhiM(entry.Electron_pt[i],entry.Electron_eta[i],entry.Electron_phi[i],0.0005)
        for j in range(i+1,nElectron) :
            if entry.Electron_charge[i] != entry.Electron_charge[j] :
                e2 = TLorentzVector()
                e2.SetPtEtaPhiM(entry.Electron_pt[j],entry.Electron_eta[j],entry.Electron_phi[j],0.0005)
                cand = e1 + e2
                mass = cand.M()
		#if mass < 60 or mass > 120 : continue
                if abs(mass-mZ) < bestDiff :
                    bestDiff = abs(mass-mZ)
                    pairList.append([e1,e2]) 

    return pairList

def catToNumber(cat) :
    number = { 'eeet':1, 'eemt':2, 'eett':3, 'eeem':4, 'mmet':5, 'mmmt':6, 'mmtt':7, 'mmem':8, 'et':9, 'mt':10, 'tt':11 }
    return number[cat]

def numberToCat(number) :
    cat = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem', 9:'et', 10:'mt', 11:'tt' }
    return cat[number]
    

def catToNumber3L(cat) :
    #number = { 'eee':1, 'eem':2, 'eet':3, 'mme':4, 'mmm':5, 'mmt':6}
    #number = { 'ee':1, 'mm':2}
    number = { 'eeee':1, 'eemm':2 , 'mmee':3, 'mmmm':4, 'eee':5, 'eem':6, 'mme':7, 'mmm':8,'ee':9, 'mm':10 }
    return number[cat]

def numberToCat3L(number) :
    #cat = { 1:'eee', 2:'eem', 3:'eet', 4:'mme', 5:'mmm', 6:'mmt' }
    #cat = { 1:'ee', 2:'mm' }
    cat= { 1:'eeee', 2:'eemm' , 3:'mmee', 4:'mmmm', 5:'eee', 6:'eem', 7:'mme', 8:'mmm', 9:'ee', 10:'mm'}
    return cat[number]





    
    
    

    
