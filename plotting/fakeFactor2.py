from ROOT import TFile

# fake factors using Cecile's WH values

class fakeFactor2() :

    def __init__(self, year, WP):

        self.printOn = False 
        eleFileName = '../fakes/WH/FitHistograms_eleFR_{0:s}.root'.format(str(year))
        fIn = TFile.Open(eleFileName,"READ")
        gEle = fIn.Get("efr_numerator_efr_denominator")
        self.ptEleHigh = [] 
        pTs = gEle.GetX()
        self.FFele = gEle.GetY()
        for i, pT in enumerate(pTs) :
            self.ptEleHigh.append(pT + gEle.GetErrorX(i))
            print("highEdge={0:6.1f} FFele={1:8.3f}".format(self.ptEleHigh[i],self.FFele[i]))
        fIn.Close()
        
        muFileName  = '../fakes/WH/FitHistograms_muFR_{0:s}.root'.format(str(year))
        fIn = TFile.Open(muFileName,"READ")
        gMu = fIn.Get("mufr_numerator_mufr_denominator")
        self.ptMuHigh = [] 
        pTs = gMu.GetX()
        self.FFmu = gMu.GetY() 
        for i, pT in enumerate(pTs) :
            self.ptMuHigh.append(pT + gMu.GetErrorX(i))
            print("highEdge={0:6.1f} FFele={1:8.3f}".format(self.ptMuHigh[i],self.FFmu[i]))
        fIn.Close()

        '''
        2  hpt_dm0_deepveryveryloose_hpt_dm0_deepveryveryveryloose
        4  hpt_dm0_deepveryloose_hpt_dm0_deepveryveryveryloose
        8  hpt_dm0_deeploose_hpt_dm0_deepveryveryveryloose
        16 hpt_dm0_deepmedium_hpt_dm0_deepveryveryveryloose	
        32 hpt_dm0_deeptight_hpt_dm0_deepveryveryveryloose	
        64 hpt_dm0_deepverytight_hpt_dm0_deepveryveryveryloose	
        '''
        WPdict = { 2:'veryveryloose', 4:'veryloose', 8:'loose', 16:'medium', 32:'tight', 64:'verytight' }
        tauFileName = '../fakes/WH/FitHistograms_tauFR_{0:s}.root'.format(str(year))
        fIn = TFile.Open(tauFileName,"READ")
        self.ptTauHigh = {}
        self.FFtau = {} 
        for DM in [0, 1, 10, 11] :
            print("DM={0:d}".format(DM))
            gName = "hpt_dm{0:d}_deep{1:s}_hpt_dm{0:d}_deepveryveryveryloose".format(DM,WPdict[WP])
            print("gName={0:s}".format(gName))
            gTau = fIn.Get(gName) 
            self.ptTauHigh[DM] = [] 
            pTs = gTau.GetX()
            ffTau = gTau.GetY()
            self.FFtau[DM] = []
            for i, pT in enumerate(pTs) :
                self.ptTauHigh[DM].append(pT + gTau.GetErrorX(i))
                self.FFtau[DM].append(float(ffTau[i])) 
                print("highEdge={0:6.1f} FFele={1:8.3f}".format(self.ptTauHigh[DM][i],self.FFtau[DM][i]))
        fIn.Close()

    def getF(self, pT, FFs, highEdges) :
        nBins = len(FFs) 
        for i in range(nBins) :
            lowEdge, highEdge = 0., 99999.
            if i > 0 : lowEdge = highEdges[i-1] 
            if i < (nBins - 1) : highEdge = highEdges[i]
            if self.printOn : print("   in getF(): i={0:d} pT={1:8.1f} lowEdge={2:8.1f} highEdge{3:8.1f} FF={4:8.4f}".format(i,pT,lowEdge,highEdge,FFs[i]))
            if pT > lowEdge and pT < highEdge : return FFs[i]

        print("Error in fakeFactor2.getF().   Value not found.")
        exit() 

            
    def getFakeWeightsvspTvsDM(self, ic, pt1, pt2, WP, DM1, DM2) :
        if self.printOn : print("Entering getFakeWeightsnvsTvsDM() ic={0:s} pt1={1:8.1f} pt2={2:8.1f} WP={3} DM1={4:4d} DM2={5:4d}".format(
            ic, pt1, pt2, WP, DM1, DM2))

        if ic == 'em' :
            f1 = self.getF(pt1,self.FFele,self.ptEleHigh) 
            f2 = self.getF(pt2,self.FFmu,self.ptMuHigh)
        elif ic == 'et' :
            f1 = self.getF(pt1,self.FFele,self.ptEleHigh) 
            f2 = self.getF(pt2,self.FFtau[DM2],self.ptTauHigh[DM2])
        elif ic == 'mt' :
            f1 = self.getF(pt1,self.FFmu,self.ptMuHigh) 
            f2 = self.getF(pt2,self.FFtau[DM2],self.ptTauHigh[DM2])
        else :
            f1 = self.getF(pt1,self.FFtau[DM1],self.ptTauHigh[DM1])
            f2 = self.getF(pt2,self.FFtau[DM2],self.ptTauHigh[DM2])
        
        #print '===========>', pt1, pt2, f1, f2, xB1, xB2
        w1, w2, w0 =0. ,0. ,0.
        w1 = float(f1/(1.-f1))
        w2 = float(f2/(1.-f2))
        w0 = w1*w2
        if self.printOn : print("Exiting w1={0:10.4f} w2={1:10.4f} w0={2:10.4f}".format(w1,w2,w0)) 
        return w1, w2, w0
