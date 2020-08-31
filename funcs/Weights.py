# !/usr/bin/env python

""" tauFun.py: apply selection sequence to four-lepton final state """

import io
import yaml
import subprocess
from ROOT import TLorentzVector
from math import sqrt, sin, cos, pi
import os
import os.path
import sys

__author__ = "Alexis Kalogeropoulos"


electronMass = 0.0005
muonMass  = 0.105

class Weights() :
    def __init__(self,year):
        campaign = {2016:'2016Legacy', 2017:'2017ReReco', 2018:'2018ReReco'}
	self.weights_muToTauFR={''}
	self.weights_elToTauFR={''}
	self.weights_mujToTauFR={''}
	self.weights_eljToTauFR={''}
	self.weights_muTotauES={''}
	self.weights_elTotauES={''}
	self.weights_tauTotauES={''}
        self.tauV = TLorentzVector()
        self.tauVcor = TLorentzVector()
        self.MetV = TLorentzVector()
        self.MetVcor = TLorentzVector()
	
	if year == 2016 : 

	    self.weights_mujToTauFR = {'DM1' : 0.85, 'lt0p4' : 1.21, '0p4to0p8' : 1.11, '0p8to1p2' : 1.20, '1p2to1p7' : 1.16, '1p7to2p3' : 2.25 }
	    self.weights_muToTauFR = {'DM1' : 1.38, 'lt0p4' : 0.80, '0p4to0p8' : 0.81, '0p8to1p2' : 0.79, '1p2to1p7' : 0.68, '1p7to2p3' : 1.34 }
	    self.weights_eljToTauFR = {'lt1p479_DM0' : 1.18, 'gt1p479_DM0' : 0.93, 'lt1p479_DM1' : 1.18, 'gt1p479_DM1' : 1.07 }
	    self.weights_elToTauFR = {'lt1p479_DM0' : 0.80, 'gt1p479_DM0' : 0.72, 'lt1p479_DM1' : 1.14, 'gt1p479_DM1' : 0.64 }



	    self.weights_tauTotauES = {'DM0' :-0.9, 'DM1' : -0.1, 'DM10' : 0.3, 'DM11' : -0.2}
	    self.weights_elTotauES = {'DM0' :-0.5, 'DM1' : 6, 'DM10' : 0, 'DM11' :0}
	    self.weights_muTotauES = {'DM0' :0., 'DM1' : -0.5, 'DM10' : 0, 'DM11' :0}


	if year == 2017 : 

	    self.weights_mujToTauFR = {'DM1' : 0.77, 'lt0p4' : 1.23, '0p4to0p8' : 1.07, '0p8to1p2' : 1.21, '1p2to1p7' : 1.21, '1p7to2p3' : 2.74 }
	    self.weights_muToTauFR = {'DM1' : 0.69, 'lt0p4' : 1.14, '0p4to0p8' : 1., '0p8to1p2' : 0.87, '1p2to1p7' : 0.52, '1p7to2p3' : 1.47 }
	    self.weights_eljToTauFR = {'lt1p479_DM0' : 1.09, 'gt1p479_DM0' : 0.86, 'lt1p479_DM1' : 1.10, 'gt1p479_DM1' : 1.03 }
	    self.weights_elToTauFR = {'lt1p479_DM0' : 0.98, 'gt1p479_DM0' : 0.80, 'lt1p479_DM1' : 1.07, 'gt1p479_DM1' : 0.64 }


	    self.weights_tauTotauES = {'DM0' :0.4, 'DM1' : 0.2, 'DM10' : 0.1, 'DM11' : -1.3}
	    self.weights_elTotauES = {'DM0' :0.3, 'DM1' : 3.6, 'DM10' : 0, 'DM11' :0}
	    self.weights_muTotauES = {'DM0' :0., 'DM1' : -0.5, 'DM10' : 0, 'DM11' :0}

	if year == 2018 : 

	    self.weights_mujToTauFR = {'DM1' : 0.79, 'lt0p4' : 1.11, '0p4to0p8' : 1.05, '0p8to1p2' : 1.18, '1p2to1p7' : 1.06, '1p7to2p3' : 1.79 }
	    self.weights_muToTauFR = {'DM1' : 0.55, 'lt0p4' : 1.08, '0p4to0p8' : 0.78, '0p8to1p2' : 0.77, '1p2to1p7' : 0.75, '1p7to2p3' : 2.02 }
	    self.weights_eljToTauFR = {'lt1p479_DM0' : 1.21, 'gt1p479_DM0' : 0.92, 'lt1p479_DM1' : 1.18, 'gt1p479_DM1' : 1.04 }
	    self.weights_elToTauFR = {'lt1p479_DM0' : 1.09, 'gt1p479_DM0' : 0.80, 'lt1p479_DM1' : 0.85, 'gt1p479_DM1' : 0.49 }

	    self.weights_tauTotauES = {'DM0' :-1.6, 'DM1' : -0.4, 'DM10' : -1.2, 'DM11' : -0.4}
	    self.weights_elTotauES = {'DM0' :-3.2, 'DM1' : 2.6, 'DM10' : 0, 'DM11' :0}
	    self.weights_muTotauES = {'DM0' :-0.2, 'DM1' : -1., 'DM10' : 0, 'DM11' :0}



	''' 
	for reco tauh matched to gen tauh at gen level in the format (dm0, dm1, dm10, dm11): for 2016 (-0.9%, -0.1%, +0.3%, -0.2%), for 2017 (+0.4%, +0.2%, +0.1%, -1.3%), for 2018 (-1.6%, -0.4%, -1.2%, -0.4%)

	for reco tauh matched to electrons at gen level in the format (dm0, dm1): for 2016 (-0.5%, +6.0%), for 2017 (+0.3%, +3.6%), for 2018 (-3.2%, +2.6%)
	for reco tauh matched to muons at gen level in the format (dm0, dm1): for 2016 (+0.0%, -0.5%), for 2017 (+0.0%, +0.0%), for 2018 (-0.2%, -1.0%)
	'''

    def applyES(self,entry, year, printOn=False) :


        self.MetVcor.SetPx(entry.MET_pt * cos (entry.MET_phi))
        if year==2017 : 
            self.MetVcor.SetPx(entry.METFixEE2017_pt * cos (entry.METFixEE2017_phi))
            entry.MET_pt = entry.METFixEE2017_pt
            entry.MET_phi = entry.METFixEE2017_phi
            entry.MET_covXX = entry.METFixEE2017_covXX
            entry.MET_covXY = entry.METFixEE2017_covXY
            entry.MET_covYY = entry.METFixEE2017_covYY

        self.MetV = self.MetVcor

	for j in range(entry.nTau):    
	   
	   
	    dm = entry.Tau_decayMode[j]
            dmm='DM{0:d}'.format(dm)  
            pt= entry.Tau_pt[j]
            eta= entry.Tau_eta[j]

	    if dm != 0 and dm != 1 and dm!=10 and dm!=11 : continue


            self.tauV.SetPtEtaPhiM(entry.Tau_pt[j], entry.Tau_eta[j], entry.Tau_phi[j], entry.Tau_mass[j])
            self.tauVcor = self.tauV

	    gen_match = ord(entry.Tau_genPartFlav[j]) 
            #print ''
            #print 'before------------', entry.Tau_pt[j], entry.Tau_mass[j], 'met_pt', entry.MET_pt, 'phi', entry.MET_phi, entry.Tau_eta[j], 'match', gen_match, dm
	    if gen_match == 5 :
		self.tauVcor *=  (1 + self.weights_tauTotauES[dmm]*0.01)
		#self.MetVcor +=  self.tauV*(1 + self.weights_tauTotauES[dmm]*0.01)
                entry.Tau_mass[j] = self.tauVcor.M()
                entry.Tau_pt[j] = self.tauVcor.Pt()
                entry.Tau_phi[j] = self.tauVcor.Phi()

		if dm == 1 :
		    entry.Tau_mass[j] = 0.1396
                    self.tauVcor.SetE(0.1396) ##is this legit ?

            if gen_match == 2 or gen_match == 4 :


		self.tauVcor *=  (1 + self.weights_muTotauES[dmm]*0.01)
		#self.MetVcor +=  self.tauV*(1 + self.weights_muTotauES[dmm]*0.01)
		entry.Tau_mass[j] = self.tauVcor.M()
		entry.Tau_pt[j] = self.tauVcor.Pt()


                # leptons faking taus // electron->tau
	    if gen_match == 1 or gen_match == 3 :

		self.tauVcor *=  (1 + self.weights_elTotauES[dmm]*0.01)
		#self.MetVcor +=  self.tauV*(1 + self.weights_elTotauES[dmm]*0.01)
		entry.Tau_mass[j] = self.tauVcor.M()
		entry.Tau_pt[j] = self.tauVcor.Pt()

	    self.MetVcor +=   self.tauV - self.tauVcor
	    entry.MET_pt = self.MetVcor.Pt()
	    entry.MET_phi = self.MetVcor.Phi()
	    #print 'after------------', entry.Tau_pt[j], entry.Tau_mass[j], 'met_pt', entry.MET_pt, 'phi', entry.MET_phi, entry.Tau_eta[j], self.tauVcor.Eta()

