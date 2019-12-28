# output ntuple for H->tautau analysis for CMSSW_10_2_X

from ROOT import TLorentzVector, TH1
from math import sqrt, sin, cos, pi
import tauFun 
import ROOT
import os
import sys
import generalFunctions as GF

class outTuple() :
    
    def __init__(self,fileName, era):
        from array import array
        from ROOT import TFile, TTree

        # Tau Decay types
        self.kUndefinedDecayType, self.kTauToHadDecay,  self.kTauToElecDecay, self.kTauToMuDecay = 0, 1, 2, 3    
        ROOT.gInterpreter.ProcessLine(".include .")
        for baseName in ['MeasuredTauLepton','svFitAuxFunctions','FastMTT'] : 
            if os.path.isfile("{0:s}_cc.so".format(baseName)) :
                ROOT.gInterpreter.ProcessLine(".L {0:s}_cc.so".format(baseName))
            else :
                ROOT.gInterpreter.ProcessLine(".L {0:s}.cc++".format(baseName))   
                # .L is not just for .so files, also .cc
        

        self.f = TFile( fileName, 'recreate' )
        self.t = TTree( 'Events', 'Output tree' )

        self.entries          = 0 
        self.run              = array('l',[0])
        self.lumi             = array('l',[0])
        self.is_trig          = array('l',[0])
        self.is_trigH         = array('l',[0])
        self.is_trigZ         = array('l',[0])
        self.is_trigZH        = array('l',[0])
        self.evt              = array('l',[0])
        self.cat              = array('l',[0])
        self.weight           = array('f',[0])
        self.LHEweight        = array('f',[0])
        self.Generator_weight = array('f',[0])
        self.LHE_Njets        = array('l',[0])
        
        self.pt_3        = array('f',[0])
        self.pt_3_tr     = array('f',[0])
        self.phi_3       = array('f',[0])
        self.phi_3_tr    = array('f',[0])
        self.eta_3       = array('f',[0])
        self.eta_3_tr    = array('f',[0])
        self.m_3         = array('f',[0])
        self.q_3         = array('f',[0])
        self.d0_3        = array('f',[0])
        self.dZ_3        = array('f',[0])
        self.mt_3        = array('f',[0])
        self.pfmt_3      = array('f',[0])
        self.puppimt_3   = array('f',[0])
        self.iso_3       = array('f',[0])
        self.gen_match_3 = array('l',[0])
        self.mediumId_3       = array('f',[0])
        self.mediumPromptId_3       = array('f',[0])
        self.looseId_3       = array('f',[0])
        self.isGlobal_3       = array('f',[0])
        self.isTracker_3       = array('f',[0])
        self.ip3d_3       = array('f',[0])
        self.inTimeMuon_3       = array('f',[0])

        self.idDecayModeNewDMs_3 = array('f',[0])
        self.idDeepTau2017v2p1VSe_3 = array('f',[0])
        self.idDeepTau2017v2p1VSjet_3 = array('f',[0])
        self.idDeepTau2017v2p1VSmu_3 = array('f',[0])
        self.idMVAnewDM2017v2_3 = array('f',[0])
        self.rawMVAnewDM2017v2_3 = array('f',[0])


        self.trigweight_3  = array('f',[0])
        self.idisoweight_3 = array('f',[0])
        self.decayMode_3   = array('l',[0])

        self.pt_4        = array('f',[0])
        self.pt_4_tr     = array('f',[0])
        self.phi_4       = array('f',[0])
        self.phi_4_tr    = array('f',[0])
        self.eta_4       = array('f',[0])
        self.eta_4_tr    = array('f',[0])
        self.m_4         = array('f',[0])
        self.q_4         = array('f',[0])
        self.d0_4        = array('f',[0])
        self.dZ_4        = array('f',[0])
        self.mt_4        = array('f',[0])
        self.pfmt_4      = array('f',[0])
        self.puppimt_4   = array('f',[0])
        self.iso_4       = array('f',[0])
        self.gen_match_4 = array('l',[0])
        self.mediumId_4       = array('f',[0])
        self.mediumPromptId_4       = array('f',[0])
        self.looseId_4       = array('f',[0])
        self.isGlobal_4       = array('f',[0])
        self.isTracker_4       = array('f',[0])
        self.ip3d_4       = array('f',[0])
        self.inTimeMuon_4       = array('f',[0])


        self.idDecayModeNewDMs_4 = array('f',[0])
        self.idDeepTau2017v2p1VSe_4 = array('f',[0])
        self.idDeepTau2017v2p1VSjet_4 = array('f',[0])
        self.idDeepTau2017v2p1VSmu_4 = array('f',[0])
        self.idMVAnewDM2017v2_4 = array('f',[0])
        self.rawMVAnewDM2017v2_4 = array('f',[0])


        self.trigweight_4  = array('f',[0])
        self.idisoweight_4 = array('f',[0])
        self.decayMode_4   = array('l',[0])

        # di-tau variables
        self.pt_tt  = array('f',[0])
        self.mt_tot = array('f',[0])
        self.m_vis  = array('f',[0])
        self.m_sv   = array('f',[0])
        self.mt_sv  = array('f',[0])
        self.H_DR  = array('f',[0])
        self.AMass   = array('f',[0])



        # di-lepton variables.   1 and 2 refer to plus and minus charge
        # ll_lmass is mass of decay lepton 
        self.mll       = array('f',[0])
        self.Z_Pt       = array('f',[0])
        self.Z_DR       = array('f',[0])
        self.Z_SS       = array('f',[0])
        self.pt_1      = array('f',[0])
        self.pt_1_tr   = array('f',[0])
        self.phi_1     = array('f',[0])
        self.phi_1_tr  = array('f',[0])
        self.eta_1     = array('f',[0])
        self.eta_1_tr  = array('f',[0])
        self.pt_2      = array('f',[0])
        self.pt_2_tr   = array('f',[0])
        self.phi_2     = array('f',[0])
        self.phi_2_tr  = array('f',[0])
        self.eta_2     = array('f',[0])
        self.eta_2_tr  = array('f',[0])
        self.iso_1       = array('f',[0])
        self.q_1       = array('f',[0])
        
        # MET variables
        self.met         = array('f',[0])
        self.metphi      = array('f',[0])
        self.puppimet    = array('f',[0])
        self.puppimetphi = array('f',[0])
        self.metcov00    = array('f',[0])
        self.metcov01    = array('f',[0])
        self.metcov10    = array('f',[0])
        self.metcov11    = array('f',[0])

        # trigger info
        self.isTrig_2   = array('f',[0])
        self.isTrig_1   = array('f',[0])


        # jet variables
        self.njetspt20 = array('f',[0])
        self.njets     = array('f',[0])
        self.nbtag     = array('f',[0])

        self.jpt_1     = array('f',[0])
        self.jpt_1_tr  = array('f',[0])
        self.jeta_1    = array('f',[0])
        self.jeta_1_tr = array('f',[0])
        self.jphi_1    = array('f',[0])
        self.jphi_1_tr = array('f',[0])
        self.jcsv_1    = array('f',[0])
        self.jcsvfv_1    = array('f',[0])
        self.jpt_2     = array('f',[0])
        self.jpt_2_tr  = array('f',[0])
        self.jeta_2    = array('f',[0])
        self.jeta_2_tr = array('f',[0])
        self.jphi_2    = array('f',[0])
        self.jphi_2_tr = array('f',[0])
        self.jcsv_2    = array('f',[0])
        self.jcsvfv_2    = array('f',[0])
        self.iso_2       = array('f',[0])
        self.q_2       = array('f',[0])

        self.bpt_1     = array('f',[0])
        self.bpt_1_tr  = array('f',[0])
        self.beta_1    = array('f',[0])
        self.beta_1_tr = array('f',[0])
        self.bphi_1    = array('f',[0])
        self.bphi_1_tr = array('f',[0])
        self.bcsv_1    = array('f',[0])
        self.bcsvfv_1    = array('f',[0])
        self.bpt_2     = array('f',[0])
        self.bpt_2_tr  = array('f',[0])
        self.beta_2    = array('f',[0])
        self.beta_2_tr = array('f',[0])
        self.bphi_2    = array('f',[0])
        self.bphi_2_tr = array('f',[0])
        self.bcsv_2    = array('f',[0])
        self.bcsvfv_2    = array('f',[0])
      
        self.t.Branch('run',              self.run,               'run/l' )
        self.t.Branch('lumi',             self.lumi,              'lumi/I' )
        self.t.Branch('is_trig',          self.is_trig,           'is_trig/I' )
        self.t.Branch('is_trigH',         self.is_trigH,          'is_trigH/I' )
        self.t.Branch('is_trigZ',         self.is_trigZ,          'is_trigZ/I' )
        self.t.Branch('is_trigZH',        self.is_trigZH,         'is_trigZH/I' )
        self.t.Branch('evt',              self.evt,               'evt/I' )
        self.t.Branch('cat',              self.cat,               'cat/I' )
        self.t.Branch('weight',           self.weight,            'weight/F' )
        self.t.Branch('LHEweight',        self.LHEweight,         'LHEweight/F' )
        self.t.Branch('LHE_Njets',        self.LHE_Njets,         'LHE_Njets/I' )
        self.t.Branch('Generator_weight', self.Generator_weight,  'Generator_weight/F' )

        self.t.Branch('pt_3',        self.pt_3,        'pt_3/F')
        self.t.Branch('pt_3_tr',     self.pt_3_tr,     'pt_3_tr/F')
        self.t.Branch('phi_3',       self.phi_3,       'phi_3/F')
        self.t.Branch('phi_3_tr',    self.phi_3_tr,    'phi_3_tr/F')
        self.t.Branch('eta_3',       self.eta_3,       'eta_3/F')
        self.t.Branch('eta_3_tr',    self.eta_3_tr,    'eta_3_tr/F')
        self.t.Branch('m_3',         self.m_3,         'm_3/F')
        self.t.Branch('q_3',         self.q_3,         'q_3/F')
        self.t.Branch('d0_3',        self.d0_3,        'd0_3/F')
        self.t.Branch('dZ_3',        self.dZ_3,        'dZ_3/F')
        self.t.Branch('mt_3',        self.mt_3,        'mt_3/F')
        self.t.Branch('pfmt_3',      self.pfmt_3,      'pfmt_3/F')
        self.t.Branch('puppimt_3',   self.puppimt_3,   'puppimt_3/F')
        self.t.Branch('iso_3',       self.iso_3,       'iso_3/F')
        self.t.Branch('gen_match_3', self.gen_match_3, 'gen_match_3/l')
        self.t.Branch('mediumId_3', self.mediumId_3, 'mediumId_3/F')
        self.t.Branch('mediumPromptId_3', self.mediumPromptId_3, 'mediumPromptId_3/F')
        self.t.Branch('looseId_3', self.looseId_3, 'looseId_3/F')
        self.t.Branch('isGlobal_3', self.isGlobal_3, 'isGlobal_3/F')
        self.t.Branch('isTracker_3', self.isTracker_3, 'isTracker_3/F')
        self.t.Branch('ip3d_3', self.ip3d_3, 'ip3d_3/F')
        self.t.Branch('inTimeMuon_3', self.inTimeMuon_3, 'inTimeMuon_3/F')


        self.t.Branch('idDecayModeNewDMs_3', self.idDecayModeNewDMs_3, 'idDecayModeNewDMs_3/F')
        self.t.Branch('idDeepTau2017v2p1VSe_3', self.idDeepTau2017v2p1VSe_3, 'idDeepTau2017v2p1VSe_3/F')
        self.t.Branch('idDeepTau2017v2p1VSjet_3', self.idDeepTau2017v2p1VSjet_3, 'idDeepTau2017v2p1VSjet_3/F')
        self.t.Branch('idDeepTau2017v2p1VSmu_3', self.idDeepTau2017v2p1VSmu_3, 'idDeepTau2017v2p1VSmu_3/F')
        self.t.Branch('idMVAnewDM2017v2_3', self.idMVAnewDM2017v2_3, 'idMVAnewDM2017v2_3/F')
        self.t.Branch('rawMVAnewDM2017v2_3', self.rawMVAnewDM2017v2_3, 'rawMVAnewDM2017v2_3/F')

        self.t.Branch('trigweight_3',  self.trigweight_3,  'trigweight_3/F')
        self.t.Branch('idisoweight_3', self.idisoweight_3, 'idisoweight_3/F')
        self.t.Branch('decayMode_3',   self.decayMode_3,   'decayMode_3/I')

        self.t.Branch('pt_4',        self.pt_4,        'pt_4/F')
        self.t.Branch('pt_4_tr',     self.pt_4,        'pt_4_tr/F')
        self.t.Branch('phi_4',       self.phi_4,       'phi_4/F')
        self.t.Branch('phi_4_tr',    self.phi_4_tr,    'phi_4_tr/F')
        self.t.Branch('eta_4',       self.eta_4,       'eta_4/F')
        self.t.Branch('eta_4_tr',    self.eta_4_tr,    'eta_4_tr/F')
        self.t.Branch('m_4',         self.m_4,         'm_4/F')
        self.t.Branch('q_4',         self.q_4,         'q_4/F')
        self.t.Branch('d0_4',        self.d0_4,        'd0_4/F')
        self.t.Branch('dZ_4',        self.dZ_4,        'dZ_4/F')
        self.t.Branch('mt_4',        self.mt_4,        'mt_4/F')
        self.t.Branch('pfmt_4',      self.pfmt_4,      'pfmt_4/F')
        self.t.Branch('puppimt_4',   self.puppimt_4,   'puppimt_4/F')
        self.t.Branch('iso_4',       self.iso_4,       'iso_4/F')
        self.t.Branch('gen_match_4', self.gen_match_4, 'gen_match_4/l')
        self.t.Branch('mediumId_4', self.mediumId_4, 'mediumId_4/F')
        self.t.Branch('mediumPromptId_4', self.mediumPromptId_4, 'mediumPromptId_4/F')
        self.t.Branch('looseId_4', self.looseId_4, 'looseId_4/F')
        self.t.Branch('isGlobal_4', self.isGlobal_4, 'isGlobal_4/F')
        self.t.Branch('isTracker_4', self.isTracker_4, 'isTracker_4/F')
        self.t.Branch('ip3d_4', self.ip3d_4, 'ip3d_4/F')
        self.t.Branch('inTimeMuon_4', self.inTimeMuon_4, 'inTimeMuon_4/F')


        self.t.Branch('idDecayModeNewDMs_4', self.idDecayModeNewDMs_4, 'idDecayModeNewDMs_4/F')
        self.t.Branch('idDeepTau2017v2p1VSe_4', self.idDeepTau2017v2p1VSe_4, 'idDeepTau2017v2p1VSe_4/F')
        self.t.Branch('idDeepTau2017v2p1VSjet_4', self.idDeepTau2017v2p1VSjet_4, 'idDeepTau2017v2p1VSjet_4/F')
        self.t.Branch('idDeepTau2017v2p1VSmu_4', self.idDeepTau2017v2p1VSmu_4, 'idDeepTau2017v2p1VSmu_4/F')
        self.t.Branch('idMVAnewDM2017v2_4', self.idMVAnewDM2017v2_4, 'idMVAnewDM2017v2_4/F')
        self.t.Branch('rawMVAnewDM2017v2_4', self.rawMVAnewDM2017v2_4, 'rawMVAnewDM2017v2_4/F')

        self.t.Branch('trigweight_4',  self.trigweight_4,  'trigweight_4/F')
        self.t.Branch('idisoweight_4', self.idisoweight_4, 'idisoweight_4/F')
        self.t.Branch('decayMode_4',   self.decayMode_4,   'decayMode_4/I')

        # di-tau variables
        self.t.Branch('pt_tt', self.pt_tt, 'pt_tt/F')
        self.t.Branch('mt_tot', self.mt_tot, 'mt_tot/F')
        self.t.Branch('m_vis', self.m_vis, 'm_vis/F')
        self.t.Branch('m_sv', self.m_sv, 'm_sv/F')
        self.t.Branch('mt_sv', self.mt_sv, 'mt_sv/F') 
        self.t.Branch('H_DR', self.H_DR, 'H_DR/F')
        self.t.Branch('AMass', self.AMass, 'AMass/F')

        # di-lepton variables. 
        self.t.Branch('mll',         self.mll,         'mll/F')   
        self.t.Branch('Z_Pt',       self.Z_Pt,       'Z_Pt/F')   
        self.t.Branch('Z_DR',       self.Z_DR,       'Z_DR/F')   
        self.t.Branch('Z_SS',       self.Z_SS,       'Z_SS/F')   
        self.t.Branch('pt_1',        self.pt_1,        'pt_1/F')
        self.t.Branch('pt_1_tr',     self.pt_1_tr,     'pt_1_tr/F')
        self.t.Branch('phi_1',       self.phi_1,       'phi_1/F')  
        self.t.Branch('phi_1_tr',    self.phi_1_tr,    'phi_1_tr/F')
        self.t.Branch('eta_1',       self.eta_1,       'eta_1/F')    
        self.t.Branch('eta_1_tr',    self.eta_1_tr,    'eta_1_tr/F')
        self.t.Branch('pt_2',        self.pt_2,        'pt_2/F')      
        self.t.Branch('pt_2_tr',     self.pt_2_tr,     'pt_2_tr/F')
        self.t.Branch('phi_2',       self.phi_2,       'phi_2/F')    
        self.t.Branch('phi_2_tr',    self.phi_2_tr,    'phi_2_tr/F')
        self.t.Branch('eta_2',       self.eta_2,       'eta_2/F')      
        self.t.Branch('eta_2_tr',    self.eta_2_tr,    'eta_2_tr/F')
        self.t.Branch('iso_1',       self.iso_1,       'iso_1/F')
        self.t.Branch('iso_2',       self.iso_2,       'iso_2/F')
        self.t.Branch('q_1',       self.q_1,       'q_1/F')
        self.t.Branch('q_2',       self.q_2,       'q_2/F')
        
        
        # MET variables
        self.t.Branch('met', self.met, 'met/F')
        self.t.Branch('metphi', self.metphi, 'metphi/F')
        self.t.Branch('puppimet', self.puppimet, 'puppimet/F')
        self.t.Branch('puppimetphi', self.puppimetphi, 'puppimetphi/F')
        self.t.Branch('metcov00', self.metcov00, 'metcov00/F')
        self.t.Branch('metcov01', self.metcov01, 'metcov01/F')
        self.t.Branch('metcov10', self.metcov10, 'metcov10/F')
        self.t.Branch('metcov11', self.metcov11, 'metcov11/F')

        # trigger sf
        self.t.Branch('isTrig_2',  self.isTrig_2, 'isTrig_2/F' )
        self.t.Branch('isTrig_1',  self.isTrig_1, 'isTrig_1/F' )


        # jet variables
        self.t.Branch('njetspt20', self.njetspt20, 'njetspt20/F') 
        self.t.Branch('njets', self.njets, 'njets/F')
        self.t.Branch('nbtag', self.nbtag, 'nbtag/F')

        self.t.Branch('jpt_1',     self.jpt_1,     'jpt_1/F' )
        self.t.Branch('jpt_1_tr',  self.jpt_1_tr,  'jpt_1_tr/F' )
        self.t.Branch('jeta_1',    self.jeta_1,    'jeta_1/F' ) 
        self.t.Branch('jeta_1_tr', self.jeta_1_tr, 'jeta_1_tr/F' )
        self.t.Branch('jphi_1',    self.jphi_1,    'jphi_1/F' )
        self.t.Branch('jphi_1_tr', self.jphi_1_tr, 'jphi_1_tr/F' )
        self.t.Branch('jcsv_1',    self.jcsv_1,    'jcsv_1/F' )
        self.t.Branch('jcsvfv_1', self.jcsvfv_1, 'jcsvfv_1/F' )
        self.t.Branch('jpt_2',     self.jpt_2,     'jpt_2/F' )
        self.t.Branch('jpt_2_tr',  self.jpt_2_tr,  'jpt_2_tr/F' )
        self.t.Branch('jeta_2',    self.jeta_2,    'jeta_2/F' ) 
        self.t.Branch('jeta_2_tr', self.jeta_2_tr, 'jeta_2_tr/F' )
        self.t.Branch('jphi_2',    self.jphi_2,    'jphi_2/F' )
        self.t.Branch('jphi_2_tr', self.jphi_2_tr, 'jphi_2_tr/F' )
        self.t.Branch('jcsv_2',    self.jcsv_2,    'jcsv_2/F' )
        self.t.Branch('jcsvfv_2', self.jcsvfv_2, 'jcsvfv_2/F' )

        self.t.Branch('bpt_1',     self.bpt_1,     'bpt_1/F' )
        self.t.Branch('bpt_1_tr',  self.bpt_1_tr,  'bpt_1_tr/F' )
        self.t.Branch('beta_1',    self.beta_1,    'beta_1/F' ) 
        self.t.Branch('beta_1_tr', self.beta_1_tr, 'beta_1_tr/F' )
        self.t.Branch('bphi_1',    self.bphi_1,    'bphi_1/F' )
        self.t.Branch('bphi_1_tr', self.bphi_1_tr, 'bphi_1_tr/F' )
        self.t.Branch('bcsv_1',    self.bcsv_1,    'bcsv_1/F' )
        self.t.Branch('bcsvfv_1', self.bcsvfv_1, 'bcsvfv_1/F' )
        self.t.Branch('bpt_2',     self.bpt_2,     'bpt_2/F' )
        self.t.Branch('bpt_2_tr',  self.bpt_2_tr,  'bpt_2_tr/F' )
        self.t.Branch('beta_2',    self.beta_2,    'beta_2/F' )
        self.t.Branch('beta_2_tr', self.beta_2_tr, 'beta_2_tr/F' )
        self.t.Branch('bphi_2',    self.bphi_2,    'bphi_2/F' )
        self.t.Branch('bphi_2_tr', self.bphi_2_tr, 'bphi_2_tr/F' )
        self.t.Branch('bcsv_2',    self.bcsv_2,    'bcsv_2/F' )
        self.t.Branch('bcsvfv_2', self.bcsvfv_2, 'bcsvfv_2/F' )

    def get_mt(self,METtype,entry,tau) :
        if METtype == 'MVAMet' :
            # temporary choice 
            dphi = tau.Phi() - entry.MET_phi
            return sqrt(2.*tau.Pt()*entry.MET_pt*(1. - cos(dphi)))
        elif METtype == 'PFMet' :
            dphi = tau.Phi() - entry.MET_phi
            return sqrt(2.*tau.Pt()*entry.MET_pt*(1. - cos(dphi)))
        elif METtype == 'PUPPIMet' :
            dphi = tau.Phi() - entry.PuppiMET_phi
            return sqrt(2.*tau.Pt()*entry.PuppiMET_pt*(1. - cos(dphi)))
        else :
            print("Invalid METtype={0:s} in outTuple.get_mt().   Exiting".format(METtype))

    def getPt_tt(self,entry,tau1,tau2) :
        ptMiss = TLorentzVector() 
        ptMiss.SetPtEtaPhiM(entry.MET_pt,0.,entry.MET_phi,0.)
        return (tau1+tau2+ptMiss).Pt()

    def getMt_tot(self,entry,tau1,tau2) :
        pt1, pt2, met = tau1.Pt(), tau2.Pt(), entry.MET_pt
        phi1, phi2, metphi = tau1.Phi(), tau2.Phi(), entry.MET_phi
        arg = 2.*(pt1*met*(1. - cos(phi1-metphi)) + pt2*met*(1. - cos(phi2-metphi)) + pt1*pt2*(1. - cos(phi2-phi1)))
        return sqrt(arg)

    def getDR(self,entry, v1,v2) :

        dPhi = min(abs(v2.Phi()-v1.Phi()),2.*pi-abs(v2.Phi()-v1.Phi()))
        DR = sqrt(dPhi**2 + (v2.Eta()-v1.Eta())**2)
	return DR

    def getM_vis(self,entry,tau1,tau2) :
        return (tau1+tau2).M()

    def getJets(self,entry,tau1,tau2,era) :
	nJet30, jetList, bJetList, bJetListFlav = 0, [], [], []
        phi2_1, eta2_1 = tau1.Phi(), tau1.Eta() 
        phi2_2, eta2_2 = tau2.Phi(), tau2.Eta() 
        for j in range(entry.nJet) :
            if entry.Jet_pt[j] < 20. : break
            if abs(entry.Jet_eta[j]) > 4.7 : continue
            phi1, eta1 = entry.Jet_phi[j], entry.Jet_eta[j]
            dPhi = min(abs(phi2_1-phi1),2.*pi-abs(phi2_1-phi1))
            DR = sqrt(dPhi**2 + (eta2_1-eta1)**2)
            dPhi = min(abs(phi2_2-phi1),2.*pi-abs(phi2_2-phi1))
            DR = min(DR,sqrt(dPhi**2 + (eta2_2-eta1)**2))
            if DR < 0.5 : continue
            bjet_discr = 0.6321
	    bjet_discrFlav = 0.0614
            if str(era) == 2017 : bjet_discr = 0.4941
            if str(era) == 2018 : bjet_discr = 0.4184
            if True  and abs(entry.Jet_eta[j]) < 2.5 and entry.Jet_btagDeepB[j] > bjet_discr : bJetList.append(j)
	    if True  and abs(entry.Jet_eta[j]) < 2.5 and entry.Jet_btagDeepFlavB[j] > bjet_discrFlav : bJetListFlav.append(j)
            #if True and abs(entry.Jet_eta[j]) < 2.4 and entry.Jet_btagCSVV2[j] > 0.800 and entry.Jet_pt[j] > 30. : bJetList.append(j)
	    jj = entry.Jet_jetId[j] & 2 ==0
	    #print '==================',entry.Jet_jetId[j], entry.Jet_pt[j], jj, entry.Jet_puId[j] 
            if entry.Jet_jetId[j]  <2  : continue
            if entry.Jet_pt[j] < 30. : continue
            nJet30 += 1
            jetList.append(j) 

        return nJet30, jetList, bJetList,bJetListFlav

    def runSVFit(self, entry, channel, jt1, jt2, tau1, tau2 ) :
                      
        measuredMETx = entry.MET_pt*cos(entry.MET_phi)
        measuredMETy = entry.MET_pt*sin(entry.MET_phi)

        #define MET covariance
        covMET = ROOT.TMatrixD(2,2)
        covMET[0][0] = entry.MET_covXX
        covMET[1][0] = entry.MET_covXY
        covMET[0][1] = entry.MET_covXY
        covMET[1][1] = entry.MET_covYY
        #covMET[0][0] = 787.352
        #covMET[1][0] = -178.63
        #covMET[0][1] = -178.63
        #covMET[1][1] = 179.545

        #self.kUndefinedDecayType, self.kTauToHadDecay,  self.kTauToElecDecay, self.kTauToMuDecay = 0, 1, 2, 3

        if channel == 'et' :
            measTau1 = ROOT.MeasuredTauLepton(self.kTauToElecDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.000511) 
        elif channel == 'mt' :
            measTau1 = ROOT.MeasuredTauLepton(self.kTauToMuDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.106) 
        elif channel == 'tt' :
            measTau1 = ROOT.MeasuredTauLepton(self.kTauToHadDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), entry.Tau_mass[jt1])
                        
	if channel != 'em' :
            measTau2 = ROOT.MeasuredTauLepton(self.kTauToHadDecay, tau2.Pt(), tau2.Eta(), tau2.Phi(), entry.Tau_mass[jt2])

	if channel == 'em' :
            measTau1 = ROOT.MeasuredTauLepton(self.kTauToElecDecay, tau1.Pt(), tau1.Eta(), tau1.Phi(), 0.000511)
            measTau2 = ROOT.MeasuredTauLepton(self.kTauToMuDecay, tau2.Pt(), tau2.Eta(), tau2.Phi(), 0.106)

        VectorOfTaus = ROOT.std.vector('MeasuredTauLepton')
        instance = VectorOfTaus()
        instance.push_back(measTau1)
        instance.push_back(measTau2)

        FMTT = ROOT.FastMTT()
        FMTT.run(instance, measuredMETx, measuredMETy, covMET)
        ttP4 = FMTT.getBestP4()
        return ttP4.M(), ttP4.Mt() 
    
    def Fill(self, entry, SVFit, cat, jt1, jt2, LepP, LepM, lepList, isMC, era) :
        ''' - jt1 and jt2 point to the selected tau candidates according to the table below.
            - if e.g., channel = 'et', the jt1 points to the electron list and jt2 points to the tau list.
            - LepP and LepM are TLorentz vectors for the positive and negative members of the dilepton pair
        '''

        is_trig_1, is_trig_2 = 0., 0.
        TrigListLep = []
        TrigListTau = []
        hltListLep  = []

        #channel_ll = 'mm' or 'ee'
        channel_ll = cat[:-2]

	TrigListLep, hltListLep  = GF.findLeptTrigger(lepList, entry, channel_ll, era)

	TrigListLep = list(dict.fromkeys(TrigListLep))


        if len(TrigListLep) == 1 :

	    if lepList[0] == TrigListLep[0] :
	        is_trig_1 = 1.
	    if lepList[1] == TrigListLep[0] :
	        is_trig_1 = -1.


        if len(TrigListLep) == 2 :
            if 'DoubleLept' in hltListLep :
	        is_trig_1 = 1.
	        is_trig_2 = 1.


        #if len(TrigListLep) == 1 : print 'TrigerList ===========>', TrigListLep, lepList, hltListLep, channel_ll, is_trig_1, is_trig_2, LepP.Pt(), LepM.Pt()
        

        # channel = 'mt', 'et', 'tt', or 'em'
        channel = cat[-2:]
        
        self.entries += 1

        self.run[0]  = entry.run
        self.lumi[0] = entry.luminosityBlock 
        self.evt[0]  = entry.event
        self.cat[0]  = tauFun.catToNumber(cat)
        self.iso_1[0]  = -99
        self.iso_2[0]  = -99
        self.q_1[0]  = -99
        self.q_2[0]  = -99

        
        try :
            self.weight[0]           = entry.genWeight
            self.LHEweight[0]        = entry.LHEWeight_originalXWGTUP
            self.Generator_weight[0] = entry.Generator_weight
            self.LHE_Njets[0]        = ord(entry.LHE_Njets) 
                        
        except AttributeError :
            self.weight[0]           = 1. 
            self.LHEweight[0]        = 1. 
            self.Generator_weight[0] = 1.
            self.LHE_Njets[0] = -1
            
        self.decayMode_3[0]        = -1
        self.idDecayModeNewDMs_3[0]= -1
        self.idDeepTau2017v2p1VSe_3[0] = -1
        self.idDeepTau2017v2p1VSjet_3[0] = -1
        self.idDeepTau2017v2p1VSmu_3[0] = -1
        self.idMVAnewDM2017v2_3[0] = -1
        self.rawMVAnewDM2017v2_3[0] = -1
        self.mediumId_3[0]       = -1 
        self.mediumPromptId_3[0]   = -1
        self.looseId_3[0]       = -1
        self.isGlobal_3[0]      = -1
        self.isTracker_3[0]     = -1
        self.ip3d_3[0]          = -1
        self.inTimeMuon_3[0]    = -1

        self.decayMode_4[0]      = -1
        self.idDecayModeNewDMs_4[0] = -1
        self.idDeepTau2017v2p1VSe_4[0] = -1
        self.idDeepTau2017v2p1VSjet_4[0] = -1
        self.idDeepTau2017v2p1VSmu_4[0] = -1
        self.idMVAnewDM2017v2_4[0] = -1
        self.rawMVAnewDM2017v2_4[0] = -1
        self.mediumId_4[0]       = -1 
        self.mediumPromptId_4[0]   = -1
        self.looseId_4[0]       = -1
        self.isGlobal_4[0]      = -1
        self.isTracker_4[0]     = -1
        self.ip3d_4[0]          = -1
        self.inTimeMuon_4[0]    = -1


        tauMass = 1.7768 
        tau1, tau2 = TLorentzVector(), TLorentzVector()

        # Fill variables for Leg3, where 3->tau(ele) and 4->tau(had)
        if channel == 'et' :
            self.pt_3[0]   = entry.Electron_pt[jt1]
            self.phi_3[0]  = entry.Electron_phi[jt1]
            self.eta_3[0]  = entry.Electron_eta[jt1]
            self.m_3[0]    = entry.Electron_mass[jt1]
            self.q_3[0]    = entry.Electron_charge[jt1]
            self.d0_3[0]   = entry.Electron_dxy[jt1]
            self.dZ_3[0]   = entry.Electron_dz[jt1]
            self.iso_3[0]  = entry.Electron_pfRelIso03_all[jt1]

            
            # Fill genMatch variables for tau(ele)
            if isMC:
                idx_genEle = entry.Electron_genPartIdx[jt1]

                # if idx_genMu = -1, no match was found
                if idx_genEle >= 0:
                    idx_genEle_mom      = entry.GenPart_genPartIdxMother[idx_genEle]
                    self.pt_3_tr[0]     = entry.GenPart_pt[idx_genEle]
                    self.phi_3_tr[0]    = entry.GenPart_phi[idx_genEle]
                    self.eta_3_tr[0]    = entry.GenPart_eta[idx_genEle]

            try: self.gen_match_3[0] = ord(entry.Electron_genPartFlav[jt1])
            except AttributeError: self.gen_match_3[0] = -1
            
            tau1.SetPtEtaPhiM(entry.Electron_pt[jt1],entry.Electron_eta[jt1], entry.Electron_phi[jt1], tauMass)
            tau2.SetPtEtaPhiM(entry.Tau_pt[jt2],entry.Tau_eta[jt2],entry.Tau_phi[jt2],tauMass)
            
            tauListE=[jt1]
	   
            '''TrigListETau=[]
	    TrigListETau = GF.findETrigger(tauListE, entry, era)

            if isMC: 
                if len(TrigListETau) == 1 :
		    sf_T1_MC = self.sf_EleTrig35.get_EfficiencyMC(entry.Electron_pt[jt1],entry.Electron_eta[jt1])
		    sf_T1_Data = self.sf_EleTrig35.get_EfficiencyData(entry.Electron_pt[jt1],entry.Electron_eta[jt1])
  
            '''

        # Fill variables for Leg3 and Leg4, where 3->tau(ele) and 4->tau(mu)
	elif channel == 'em':
            self.pt_3[0]   = entry.Electron_pt[jt1]
            self.phi_3[0]  = entry.Electron_phi[jt1]
            self.eta_3[0]  = entry.Electron_eta[jt1]
            self.m_3[0]    = entry.Electron_mass[jt1]
            self.q_3[0]    = entry.Electron_charge[jt1]
            self.d0_3[0]   = entry.Electron_dxy[jt1]
            self.dZ_3[0]   = entry.Electron_dz[jt1]
            self.iso_3[0]  = entry.Electron_pfRelIso03_all[jt1]
            
            try : self.gen_match_3[0] = ord(entry.Electron_genPartFlav[jt1])
            except AttributeError : self.gen_match_3[0] = -1
            
            tau1.SetPtEtaPhiM(entry.Electron_pt[jt1], entry.Electron_eta[jt1], entry.Electron_phi[jt1], tauMass)
                                                                                                        #???
            # fill genMatch for tau(ele)
            if isMC:
                idx_genEle = entry.Electron_genPartIdx[jt1]

                # if idx_genEle = -1, no match was found
                if idx_genEle >= 0:
                    idx_genEle_mom      = entry.GenPart_genPartIdxMother[idx_genEle]
                    self.pt_3_tr[0]     = entry.GenPart_pt[idx_genEle]
                    self.phi_3_tr[0]    = entry.GenPart_phi[idx_genEle]
                    self.eta_3_tr[0]    = entry.GenPart_eta[idx_genEle]

            self.pt_4[0]     = entry.Muon_pt[jt2]
            self.phi_4[0]    = entry.Muon_phi[jt2]
            self.eta_4[0]    = entry.Muon_eta[jt2]
            self.m_4[0]      = entry.Muon_mass[jt2]
            self.q_4[0]      = entry.Muon_charge[jt2]
            self.d0_4[0]     = entry.Muon_dxy[jt2]
            self.dZ_4[0]     = entry.Muon_dz[jt2]
            self.iso_4[0]    = entry.Muon_pfRelIso04_all[jt2]
            self.mediumId_4[0]      = entry.Muon_mediumId[jt2]
            self.mediumPromptId_4[0]   = entry.Muon_mediumPromptId[jt2]
            self.looseId_4[0]       = entry.Muon_looseId[jt2]
            self.isGlobal_4[0]      = entry.Muon_isGlobal[jt2]
            self.isTracker_4[0]     = entry.Muon_isTracker[jt2]
            self.ip3d_4[0]       = entry.Muon_ip3d[jt2]
            self.inTimeMuon_4[0]    = entry.Muon_inTimeMuon[jt2]
            try : self.gen_match_4[0] = ord(entry.Muon_genPartFlav[jt2]) 
            except AttributeError : self.gen_match_4[0] = -1
            
            tau2.SetPtEtaPhiM(entry.Muon_pt[jt2], entry.Muon_eta[jt2], entry.Muon_phi[jt2], tauMass) 

            # fill genMatch for tau(mu)
            if isMC:
                idx_genMu = entry.Muon_genPartIdx[jt2]
                
                # if idx_genMu = -1, no match was found
                if idx_genMu >= 0:
                    idx_genMu_mom       = entry.GenPart_genPartIdxMother[idx_genMu]
                    self.pt_4_tr[0]     = entry.GenPart_pt[idx_genMu]
                    self.phi_4_tr[0]    = entry.GenPart_phi[idx_genMu]
                    self.eta_4_tr[0]    = entry.GenPart_eta[idx_genMu]

	    '''tauListMu=[]
	    tauListE=[jt1]
	    tauListMu=[jt2]
	    TrigListETau=[]
	    TrigListETau = GF.findETrigger(tauListE, entry, era)
	    TrigListMuTau=[]
	    TrigListMuTau = GF.findETrigger(tauListMu, entry, era)

            if isMC :

	        if len(TrigListETau) == 1 :
		    sf_T1_MC = self.sf_EleTrig35.get_EfficiencyMC(entry.Electron_pt[jt1],entry.Electron_eta[jt1])
		    sf_T1_Data = self.sf_EleTrig35.get_EfficiencyData(entry.Electron_pt[jt1],entry.Electron_eta[jt1])
	        if len(TrigListMuTau) == 1 :
		    sf_T2_MC = self.sf_MuonTrigIso27.get_EfficiencyMC(entry.Muon_pt[jt2],entry.Muon_eta[jt2])
		    sf_T2_Data = self.sf_MuonTrigIso27.get_EfficiencyData(entry.Muon_pt[jt2],entry.Muon_eta[jt2])
            '''

        # Fill variables for Leg3, where 3->tau(mu) and 4->tau(had)
        elif channel == 'mt' :
            self.pt_3[0]     = entry.Muon_pt[jt1]
            self.phi_3[0]    = entry.Muon_phi[jt1]
            self.eta_3[0]    = entry.Muon_eta[jt1]
            self.m_3[0]      = entry.Muon_mass[jt1]
            self.q_3[0]      = entry.Muon_charge[jt1]
            self.d0_3[0]     = entry.Muon_dxy[jt1]
            self.dZ_3[0]     = entry.Muon_dz[jt1]
            self.iso_3[0]    = entry.Muon_pfRelIso04_all[jt1]
            self.mediumId_3[0]       = entry.Muon_mediumId[jt1]
            self.mediumPromptId_3[0]   = entry.Muon_mediumPromptId[jt1]
            self.looseId_3[0]       = entry.Muon_looseId[jt1]
            self.isGlobal_3[0]      = entry.Muon_isGlobal[jt1]
            self.isTracker_3[0]     = entry.Muon_isTracker[jt1]
            self.ip3d_3[0]       = entry.Muon_ip3d[jt1]
            self.inTimeMuon_3[0]    = entry.Muon_inTimeMuon[jt1]
            
            try : self.gen_match_3[0] = ord(entry.Muon_genPartFlav[jt1])
            except AttributeError : self.gen_match_1[0] = -1
            
            tau1.SetPtEtaPhiM(entry.Muon_pt[jt1], entry.Muon_eta[jt1], entry.Muon_phi[jt1], tauMass)
            tau2.SetPtEtaPhiM(entry.Tau_pt[jt2],  entry.Tau_eta[jt2],  entry.Tau_phi[jt2],  tauMass) 
            
            # fill genMatch for tau(mu)
            if isMC:
                idx_genMu = entry.Muon_genPartIdx[jt1]
                
                # if idx_genMu = -1, no match was found
                if idx_genMu >= 0:
                    idx_genMu_mom       = entry.GenPart_genPartIdxMother[idx_genMu]
                    self.pt_3_tr[0]     = entry.GenPart_pt[idx_genMu]
                    self.phi_3_tr[0]    = entry.GenPart_phi[idx_genMu]
                    self.eta_3_tr[0]    = entry.GenPart_eta[idx_genMu]
                    
 	    '''tauListMu=[]
	    tauListMu=[jt1]
	    TrigListMuTau=[]
	    TrigListMuTau = GF.findETrigger(tauListMu, entry, era)

            if isMC :

		    if len(TrigListMuTau) == 1 :
			sf_T1_MC = self.sf_MuonTrigIso27.get_EfficiencyMC(entry.Muon_pt[jt1],entry.Muon_eta[jt1])
			sf_T1_Data = self.sf_MuonTrigIso27.get_EfficiencyData(entry.Muon_pt[jt1],entry.Muon_eta[jt1])


            '''
        
        # Fill variables for Leg3 and Leg4, where 3->tau(had) and 4->tau(had)
        elif channel == 'tt' :
            self.pt_3[0]     = entry.Tau_pt[jt1]
            self.phi_3[0]    = entry.Tau_phi[jt1]
            self.eta_3[0]    = entry.Tau_eta[jt1]
            self.m_3[0]      = entry.Tau_mass[jt1]
            self.q_3[0]      = entry.Tau_charge[jt1]
            self.d0_3[0]     = entry.Tau_dxy[jt1]
            self.dZ_3[0]     = entry.Tau_dz[jt1]
 

            self.idDecayModeNewDMs_3[0] = entry.Tau_idDecayModeNewDMs[jt1]
            self.idDeepTau2017v2p1VSe_3[0] = ord(entry.Tau_idDeepTau2017v2p1VSe[jt1])
            self.idDeepTau2017v2p1VSjet_3[0] = ord(entry.Tau_idDeepTau2017v2p1VSjet[jt1])
            self.idDeepTau2017v2p1VSmu_3[0] = ord(entry.Tau_idDeepTau2017v2p1VSmu[jt1])
            self.idMVAnewDM2017v2_3[0] = ord(entry.Tau_idMVAnewDM2017v2[jt1])
            self.rawMVAnewDM2017v2_3[0] = entry.Tau_rawMVAnewDM2017v2[jt1]

    
            # genMatch the hadronic tau candidate
            idx_t1_gen = GF.genMatchTau(entry, jt1, 'had')
            if idx_t1_gen >= 0:
                self.pt_3_tr[0]  = entry.GenVisTau_pt[idx_t1_gen]
                self.phi_3_tr[0] = entry.GenVisTau_phi[idx_t1_gen]
                self.eta_3_tr[0] = entry.GenVisTau_eta[idx_t1_gen]
            else:
                self.pt_3_tr[0]  = 1.2*entry.Tau_pt[jt1]
                self.phi_3_tr[0] = 1.2*entry.Tau_phi[jt1]
                self.eta_3_tr[0] = 1.2*entry.Tau_eta[jt1]

            try : self.gen_match_3[0] = ord(entry.Tau_genPartFlav[jt1])
            except AttributeError : self.gen_match_3[0] = -1

            try : self.decayMode_3[0] = int(entry.Tau_decayMode[jt1])
            except AttributeError : self.decayMode_3[0] = -1

            tau1.SetPtEtaPhiM(entry.Tau_pt[jt1], entry.Tau_eta[jt1], entry.Tau_phi[jt1], tauMass)
            tau2.SetPtEtaPhiM(entry.Tau_pt[jt2], entry.Tau_eta[jt2], entry.Tau_phi[jt2], tauMass)
            
        else :
            print("Invalid channel={0:s} in outTuple(). Exiting.".format(channel))
            exit()
            
        self.mt_3[0]      = self.get_mt('MVAMet',   entry,tau1)
        self.pfmt_3[0]    = self.get_mt('PFMet',    entry,tau1)
        self.puppimt_3[0] = self.get_mt('PUPPIMet', entry,tau1)

        self.trigweight_3[0]  = -999.   
        self.idisoweight_3[0] = -999.   
	
        # Fill variables for Leg4, where 4->tau(had)
        if channel != 'em':
	    self.pt_4[0]  = entry.Tau_pt[jt2]
            self.phi_4[0] = entry.Tau_phi[jt2]
            self.eta_4[0] = entry.Tau_eta[jt2]
            self.m_4[0]   = entry.Tau_mass[jt2]
            self.q_4[0]   = entry.Tau_charge[jt2]
            self.d0_4[0]  = entry.Tau_dxy[jt2]
            self.dZ_4[0]  = entry.Tau_dz[jt2]

            self.idDecayModeNewDMs_4[0] = entry.Tau_idDecayModeNewDMs[jt2]
            self.idDeepTau2017v2p1VSe_4[0] = ord(entry.Tau_idDeepTau2017v2p1VSe[jt2])
            self.idDeepTau2017v2p1VSjet_4[0] = ord(entry.Tau_idDeepTau2017v2p1VSjet[jt2])
            self.idDeepTau2017v2p1VSmu_4[0] = ord(entry.Tau_idDeepTau2017v2p1VSmu[jt2])
            self.idMVAnewDM2017v2_4[0] = ord(entry.Tau_idMVAnewDM2017v2[jt2])
            self.rawMVAnewDM2017v2_4[0] = entry.Tau_rawMVAnewDM2017v2[jt2]
            
            phi, pt = entry.Tau_phi[jt2], entry.Tau_pt[jt2]
            
            self.mt_4[0]      = self.get_mt('MVAMet',   entry, tau2) 
            self.pfmt_4[0]    = self.get_mt('PFMet',    entry, tau2)
            self.puppimt_4[0] = self.get_mt('PUPPIMet', entry, tau2) 


            # genMatch the hadronic tau candidate
            idx_t2_gen = GF.genMatchTau(entry, jt2, 'had')
            if idx_t2_gen >= 0:
                self.pt_4_tr[0]  = entry.GenVisTau_pt[idx_t2_gen]
                self.phi_4_tr[0] = entry.GenVisTau_phi[idx_t2_gen]
                self.eta_4_tr[0] = entry.GenVisTau_eta[idx_t2_gen]
            else:
                self.pt_4_tr[0]  = 1.2*entry.Tau_pt[jt2]
                self.phi_4_tr[0] = 1.2*entry.Tau_phi[jt2]
                self.eta_4_tr[0] = 1.2*entry.Tau_eta[jt2]

	    try : self.gen_match_4[0] = ord(entry.Tau_genPartFlav[jt2])
	    except AttributeError: self.gen_match_4[0] = -1

            try : self.decayMode_4[0] = int(entry.Tau_decayMode[jt2])
            except AttributeError: self.decayMode_4[0] = -1

            self.trigweight_4[0]  = -999.   # requires sf need help from Sam on these
            self.idisoweight_4[0] = -999.   # requires sf need help from Sam on these

        # di-tau variables
        self.pt_tt[0]  = self.getPt_tt( entry, tau1, tau2)
        self.H_DR[0] = self.getDR(entry,tau1,tau2)
        self.mt_tot[0] = self.getMt_tot(entry, tau1, tau2)
        self.m_vis[0]  = self.getM_vis( entry, tau1, tau2)
            
        if SVFit :
            fastMTTmass, fastMTTtransverseMass = self.runSVFit(entry, channel, jt1, jt2, tau1, tau2) 
        else :
            fastMTTmass, fastMTTtransverseMass = -999., -999.
            
        self.m_sv[0] = fastMTTmass 
        self.mt_sv[0] = fastMTTtransverseMass  


        # Sort the di-lepton system by Pt
        Lep1, Lep2 = TLorentzVector(), TLorentzVector()
        if (LepP.Pt() > LepM.Pt()): 
            Lep1 = LepP
            Lep2 = LepM
        else:
            Lep1 = LepM
            Lep2 = LepP


        # di-lepton variables.   _p and _m refer to plus and minus charge
        self.AMass[0]       = (Lep1 + Lep2 + tau1 + tau2).M() 
        self.mll[0]       = (Lep1 + Lep2).M()
        self.Z_DR[0]       = self.getDR(entry,Lep1,Lep2)
           
        self.pt_1[0]   = Lep1.Pt()
        self.phi_1[0]  = Lep1.Phi()
        self.eta_1[0]  = Lep1.Eta()
        self.pt_2[0]   = Lep2.Pt()
        self.phi_2[0]  = Lep2.Phi()
        self.eta_2[0]  = Lep2.Eta()

	#relIso 
	if channel_ll == 'ee' : 
	   if (LepP.Pt() > LepM.Pt()):
                self.iso_1[0]  = entry.Electron_pfRelIso03_all[lepList[0]]
                self.iso_2[0]  = entry.Electron_pfRelIso03_all[lepList[1]]
                self.q_1[0]  = entry.Electron_charge[lepList[0]]
                self.q_2[0]  = entry.Electron_charge[lepList[1]]
	   else : 
                self.iso_1[0]  = entry.Electron_pfRelIso03_all[lepList[1]]
                self.iso_2[0]  = entry.Electron_pfRelIso03_all[lepList[0]]
                self.q_1[0]  = entry.Electron_charge[lepList[1]]
                self.q_2[0]  = entry.Electron_charge[lepList[0]]

	if channel_ll == 'mm' : 
	   if (LepP.Pt() > LepM.Pt()):
                self.iso_1[0]  = entry.Muon_pfRelIso04_all[lepList[0]]
                self.iso_2[0]  = entry.Muon_pfRelIso04_all[lepList[1]]
                self.q_1[0]  = entry.Muon_charge[lepList[0]]
                self.q_2[0]  = entry.Muon_charge[lepList[1]]
	   else : 
                self.iso_1[0]  = entry.Muon_pfRelIso04_all[lepList[1]]
                self.iso_2[0]  = entry.Muon_pfRelIso04_all[lepList[0]]
                self.q_1[0]  = entry.Muon_charge[lepList[1]]
                self.q_2[0]  = entry.Muon_charge[lepList[0]]
        
        # genMatch the di-lepton variables
        idx_Lep1, idx_Lep2 = -1, -1
        idx_Lep1_tr, idx_Lep2_tr = -1, -1
        if (Lep1.M() > 0.05 and Lep2.M() > 0.05): # muon mass 
            idx_Lep1 = GF.getLepIdxFrom4Vec(entry, Lep1, 'm')
            idx_Lep2 = GF.getLepIdxFrom4Vec(entry, Lep2, 'm')
            try :
                idx_Lep1_tr = entry.Muon_genPartIdx[idx_Lep1]
                idx_Lep2_tr = entry.Muon_genPartIdx[idx_Lep2]
            except IndexError : pass 
                
        elif (Lep1.M() < 0.05 and Lep2.M() < 0.05): # electron mass
            idx_Lep1 = GF.getLepIdxFrom4Vec(entry, Lep1, 'e')
            idx_Lep2 = GF.getLepIdxFrom4Vec(entry, Lep2, 'e')
            try :
                idx_Lep1_tr = entry.Electron_genPartIdx[idx_Lep1]
                idx_Lep2_tr = entry.Electron_genPartIdx[idx_Lep2]
            except IndexError : pass 
                
        if idx_Lep1_tr >= 0 and idx_Lep2_tr >= 0:
            self.pt_1_tr[0]  = entry.GenPart_pt[idx_Lep1_tr]
            self.pt_2_tr[0]  = entry.GenPart_pt[idx_Lep2_tr]
            self.eta_1_tr[0] = entry.GenPart_eta[idx_Lep1_tr]
            self.eta_2_tr[0] = entry.GenPart_eta[idx_Lep2_tr]
            self.phi_1_tr[0] = entry.GenPart_phi[idx_Lep1_tr]
            self.phi_2_tr[0] = entry.GenPart_phi[idx_Lep2_tr]
        
        # MET variables
        self.met[0]         = entry.MET_pt    
        self.metphi[0]      = entry.MET_phi
        self.puppimet[0]    = entry.PuppiMET_pt
        self.puppimetphi[0] = entry.PuppiMET_phi
        
        self.metcov00[0] = entry.MET_covXX
        self.metcov01[0] = entry.MET_covXY
        self.metcov10[0] = entry.MET_covXY	
        self.metcov11[0] = entry.MET_covYY


        # trig
	self.isTrig_1[0]   = is_trig_1
        self.isTrig_2[0]   = is_trig_2

        # jet variables
        nJet30, jetList, bJetList, bJetListFlav = self.getJets(entry,tau1,tau2,era) 
        self.njetspt20[0] = len(jetList)
        self.njets[0] = nJet30
        self.nbtag[0] = len(bJetList)
        
        self.jpt_1[0], self.jeta_1[0], self.jphi_1[0], self.jcsv_1[0], self.jcsvfv_1[0]= -9.99, -9.99, -9.99, -9.99, -9.99 
        if len(jetList) > 0 :
            jj1 = jetList[0]
            self.jpt_1[0]  = entry.Jet_pt[jj1]
            self.jeta_1[0] = entry.Jet_eta[jj1]
            self.jphi_1[0] = entry.Jet_phi[jj1]
            self.jcsv_1[0] = entry.Jet_btagDeepB[jj1]
            self.jcsvfv_1[0] = entry.Jet_btagDeepFlavB[jj1]
            
            # genMatch jet1
            idx_genJet = entry.Jet_genJetIdx[jj1]
            if idx_genJet >= 0:
                try :
                    self.jpt_1_tr[0]  = entry.GenJet_pt[idx_genJet]
                    self.jeta_1_tr[0] = entry.GenJet_eta[idx_genJet]
                    self.jphi_1_tr[0] = entry.GenJet_phi[idx_genJet]
                except IndexError : pass
                
        self.jpt_2[0], self.jeta_2[0], self.jphi_2[0], self.jcsv_2[0],self.jcsvfv_2[0] = -9.99, -9.99, -9.99, -9.99, -9.99
        if len(jetList) > 1 :
            jj2 = jetList[1] 
            self.jpt_2[0]  = entry.Jet_pt[jj2]
            self.jeta_2[0] = entry.Jet_eta[jj2]
            self.jphi_2[0] = entry.Jet_phi[jj2]
            self.jcsv_2[0] = entry.Jet_btagDeepB[jj2]
            self.jcsvfv_2[0] = entry.Jet_btagDeepFlavB[jj2]
            
            # genMatch jet2
            idx_genJet = entry.Jet_genJetIdx[jj2]
            if idx_genJet >= 0:
	        try: 
                   self.jpt_2_tr[0]  = entry.GenJet_pt[idx_genJet]
                   self.jeta_2_tr[0] = entry.GenJet_eta[idx_genJet]
                   self.jphi_2_tr[0] = entry.GenJet_phi[idx_genJet]
                except IndexError : pass 

        self.bpt_1[0], self.beta_1[0], self.bphi_1[0], self.bcsv_1[0], self.bcsvfv_1[0] = -9.99, -9.99, -9.99, -9.99, -9.99
        if len(bJetList) > 0 :
            jbj1 = bJetList[0]
            self.bpt_1[0] = entry.Jet_pt[jbj1]
            self.beta_1[0] = entry.Jet_eta[jbj1]
            self.bphi_1[0] = entry.Jet_phi[jbj1]
            self.bcsv_1[0] = entry.Jet_btagDeepB[jbj1] 
            self.bcsvfv_1[0] = entry.Jet_btagDeepFlavB[jbj1]
            
            # genMatch bjet1
            '''idx_genJet = entry.Jet_genJetIdx[jbj1]
            if idx_genJet >= 0:
                self.bpt_1_tr[0] = entry.GenJet_pt[idx_genJet]
                self.beta_1_tr[0] =entry.GenJet_eta[idx_genJet]
                self.bphi_1_tr[0] =entry.GenJet_phi[idx_genJet]
            '''
        self.bpt_2[0], self.beta_2[0], self.bphi_2[0], self.bcsv_2[0], self.bcsvfv_2[0] = -9.99, -9.99, -9.99, -9.99, -9.99
        if len(bJetList) > 1 :
            jbj2 = bJetList[1] 
            self.bpt_2[0] = entry.Jet_pt[jbj2]
            self.beta_2[0] = entry.Jet_eta[jbj2]
            self.bphi_2[0] = entry.Jet_phi[jbj2]
            self.bcsv_2[0] = entry.Jet_btagDeepB[jbj2]
            self.bcsvfv_2[0] = entry.Jet_btagDeepFlavB[jbj2]

            # genMatch bjet1
            idx_genJet = entry.Jet_genJetIdx[jbj2]
            if idx_genJet >= 0:
                try :
                    self.bpt_2_tr[0]  = entry.GenJet_pt[idx_genJet]
                    self.beta_2_tr[0] = entry.GenJet_eta[idx_genJet]
                    self.bphi_2_tr[0] = entry.GenJet_phi[idx_genJet]
                except IndexError : pass
        self.t.Fill()
        #self.weight[0] = 1.
        return

    def setWeight(self,weight) :
        self.weight[0] = weight
        #print("outTuple.setWeight() weight={0:f}".format(weight))
        return

    def writeTree(self) :
        print("In outTuple.writeTree() entries={0:d}".format(self.entries)) 
        self.f.Write()
        self.f.Close()
        return

    


