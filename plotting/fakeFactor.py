from ROOT import TFile

class fakeFactor() :

    def __init__(self, year, WP,tag, vertag, syst):
        #self.p1 = {'et':'e_et', 'mt':'m_mt', 'em':'e_em', 'tt':'t1_tt' }
        #self.p2 = {'et':'t_et', 'mt':'t_mt', 'em':'m_em', 'tt':'t2_tt' } 
        #vertag='v6'
        #vertag='v2'
        # the default one must v4
        vertag='v4'
	self.p1 = {'et':'e_', 'mt':'m_', 'em':'e_', 'tt':'t1_' }
	self.p2 = {'et':'t_', 'mt':'t_', 'em':'m_', 'tt':'t2_' } 
        if 'noL' in tag :
            #all leptons, all taus from 3L ?
            if 'v1' in vertag :      
		self.p1 = {'et':'e_e', 'mt':'m_m', 'em':'e_e', 'tt':'t_ll' }
		self.p2 = {'et':'t_ll', 'mt':'t_ll', 'em':'m_m', 'tt':'t_ll' } 

            #all leptons, separate taus from 3L ?
            if 'v2' in vertag :      

		self.p1 = {'et':'e_e', 'mt':'m_m', 'em':'e_e', 'tt':'t1_tt' }
		self.p2 = {'et':'t_et', 'mt':'t_mt', 'em':'m_m', 'tt':'t2_tt' } 

            #group lepton, group taus
            if 'v3' in vertag :      
		self.p1 = {'et':'e_ll', 'mt':'m_ll', 'em':'e_ll', 'tt':'t_ll' }
		self.p2 = {'et':'t_ll', 'mt':'t_ll', 'em':'m_ll', 'tt':'t_ll' } 

            #group lepton, separate taus
            if 'v4' in vertag :      
		self.p1 = {'et':'e_ll', 'mt':'m_ll', 'em':'e_ll', 'tt':'t1_tt' }
		self.p2 = {'et':'t_et', 'mt':'t_mt', 'em':'m_ll', 'tt':'t2_tt' } 

            #separate lepton, group taus
            if 'v5' in vertag :      
		self.p1 = {'et':'e_et', 'mt':'m_mt', 'em':'e_em', 'tt':'t_ll' }
		self.p2 = {'et':'t_ll', 'mt':'t_ll', 'em':'m_em', 'tt':'t_ll' } 

            #separate lepton, separe taus
            if 'v6' in vertag :      
		self.p1 = {'et':'e_et', 'mt':'m_mt', 'em':'e_em', 'tt':'t1_tt' }
		self.p2 = {'et':'t_et', 'mt':'t_mt', 'em':'m_em', 'tt':'t2_tt' } 


        
        filein = './FakesResult_{0:s}_SS_{1:s}WP_sys{2:s}.root'.format(str(year),str(WP),syst)
        print 'Will use ', filein, 'for fakes with vertag', tag, vertag
        print self.p1
        print self.p2

            
        self.fin = TFile.Open(filein,"READ")


    def getFakeWeightsvspTvsDM(self, ic, pt1, pt2, WP, DM1, DM2) :
        #print("Entering getFakeWeightsnvsTvsDM() ic={0:s} pt1={1:8.1f} pt2={2:8.1f} WP={3} DM1={4:4d} DM2={5:4d}".format(ic, pt1, pt2, WP, DM1, DM2))

        h1 = self.fin.Get('{0:s}_vspT'.format(self.p1[ic]))
        h2 = self.fin.Get('{0:s}_vspT'.format(self.p2[ic]))

        if ic == 'et' or ic =='mt' : 
	    h1 = self.fin.Get('{0:s}_vspT'.format(self.p1[ic]))
	    h2 = self.fin.Get('{0:s}_DM{1:s}_vspT'.format(self.p2[ic],str(DM2)))

        if ic == 'tt': 
	    h1 = self.fin.Get('{0:s}_DM{1:s}_vspT'.format(self.p1[ic],str(DM1)))
	    h2 = self.fin.Get('{0:s}_DM{1:s}_vspT'.format(self.p2[ic],str(DM2)))

        #print("h1.GetNbinsX()={0:d} h2.GetNbinsX()={1:d}".format(h1.GetNbinsX(), h2.GetNbinsX())) 
        xB1 = 1
        xB2 = 1
        if pt1 < 100 : xB1 = h1.FindBin(pt1)
        if pt1 > 100 : xB1 = h1.GetNbinsX()

        if pt2 < 100 : xB2 = h2.FindBin(pt2)
        if pt2 > 100 : xB2 = h2.GetNbinsX()

        f1 = h1.GetBinContent(xB1)
        f2 = h1.GetBinContent(xB2)
        #print '===========>', pt1, pt2, f1, f2, xB1, xB2
        w1, w2, w0 =0. ,0. ,0.
        w1 = float(f1/(1.-f1))
        w2 = float(f2/(1.-f2))
        w0 = w1*w2
        #print '================= now reading fake rate for data', pt1, pt2 ,' to be', f1, f2, 'actual fW1 etc', w1, w2, w0, 'is this false??? ', ist1, ist2
        return w1, w2, w0
