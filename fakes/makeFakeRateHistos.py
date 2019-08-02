#
# estimate fake rate for irreducilble backgrounds 
#

from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, TLatex, kRed
import tdrstyle 

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    parser.add_argument("-l","--LTcut",default=80.,type=float,help="LT cut")
    return parser.parse_args()

class dupeDetector() :
    
    def __init__(self):
        self.nCalls = 0 
        self.runEventList = []

    def checkEvent(self,entry) :
        self.nCalls += 1 
        runEvent = "{0:d}:{1:d}".format(entry.run,entry.evt)
        if runEvent in self.runEventList :
            #print("Event in list: runEventList={0:s}".format(str(self.runEventList)))
            return True
        else :
            self.runEventList.append(runEvent)
            #print("New event: runEventList={0:s}".format(str(self.runEventList)))
            return False

    def printSummary(self) :
        print("Duplicate Event Summary: Calls={0:d} Unique Events={1:d}".format(self.nCalls,len(self.runEventList)))
        return

args = getArgs()
era = str(args.year)
nBins, xMin, xMax = 10, 0., 200.
lumi = 1000.*41.8 
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
preCutOff = False  

# use this utility class to screen out duplicate events
DD = dupeDetector()

# open an output file
fOut = TFile('FakeRates.root', 'recreate' )

# create histograms
hBase, hTight = {}, {}
hList = ['e_et','m_mt','t_et','t_mt','t1_tt','t2_tt']
for h in hList :
    hName = "{0:s}Base".format(h)
    hBase[h] = TH1D(hName,hName,10,0.,100.)
    hName = "{0:s}Tight".format(h)
    hTight[h] = TH1D(hName,hName,10,0.,100.)
    
# loop over the data to fill the histograms
for era in ['2017B','2017C','2017D','2017E','2017F'] :
    for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
        inFileName = './data/{0:s}_Run{1:s}/{0:s}_Run{1:s}.root'.format(dataset,era)
        print("Opening {0:s}".format(inFileName)) 
        inFile = TFile.Open(inFileName)
        inFile.cd()
        inTree = inFile.Get("Events")
        nentries = inTree.GetEntries()
        for i, e in enumerate(inTree) :

            # impose any common selection criteria here
            # include only same sign events 
            if e.q_1*e.q_2 < 0. : continue
            if e.nbtag > 0 : continue
            
            # skip duplicate events
            if DD.checkEvent(e) : continue 

            cat = cats[e.cat]
            if cat[2:] == 'et' :
                # apply transverse mass cut on electron-MET system
                et = TLorentzVector()
                et.SetPtEtaPhiM(e.pt_1,0.,e.phi_1,0.000511)
                ptMiss = TLorentzVector() 
                ptMiss.SetPtEtaPhiM(e.met,0.,e.metphi,0.)
                eMET = et + ptMiss
                preCut = preCutOff or eMET.Mt() > 40.  
                if preCut : hBase['e_et'].Fill(e.pt_1)
                hBase['t_et'].Fill(e.pt_2)
                if e.iso_1 > 0.5 :
                    if preCut : hTight['e_et'].Fill(e.pt_1)
                if e.iso_2_ID > 15 :
                    hTight['t_et'].Fill(e.pt_2)
                    
            elif cat[2:] == 'mt' :
                # apply transverse mass cut on muon-MET system
                mut = TLorentzVector()
                mut.SetPtEtaPhiM(e.pt_1,0.,e.phi_1,0.102)
                ptMiss = TLorentzVector() 
                ptMiss.SetPtEtaPhiM(e.met,0.,e.metphi,0.)
                muMET = mut + ptMiss
                preCut = preCutOff or muMET.Mt() > 40. 
                if preCut : hBase['m_mt'].Fill(e.pt_1)
                hBase['t_mt'].Fill(e.pt_2)
                if e.iso_1 < 0.25 and e.iso_1_ID > 0 : 
                    if preCut : hTight['m_mt'].Fill(e.pt_1)
                if e.iso_2_ID > 15 :
                    hTight['t_mt'].Fill(e.pt_2)

            else :
                H_LT = e.pt_1 + e.pt_2
                if not preCutOff and H_LT < args.LTcut : continue
                hBase['t1_tt'].Fill(e.pt_1)
                hBase['t2_tt'].Fill(e.pt_2)
                if e.iso_1_ID > 15 :
                    hTight['t1_tt'].Fill(e.pt_1)
                if e.iso_2_ID > 15 : 
                    hTight['t2_tt'].Fill(e.pt_2)
            
        inFile.Close()

DD.printSummary()


# create a similar set of histograms for the MC
# dictionaries where the nickName is the key
xsec, totalWeight, sampleWeight = {}, {}, {}
nickNames = []

#       0                 1       2        3        4        5            6
# GluGluHToTauTau	Signal	48.58	9259000	198813970.4	 	/GluGluHToTauTau_...
# make a first pass to get the weights 
for line in open('MCsamples_'+era+'.csv','r').readlines() :
    vals = line.split(',')
    nickName = vals[0]
    group = vals[1]
    #if not group.lower() == 'reducible' : continue 
    nickNames.append(nickName) 
    xsec[nickName] = float(vals[2])
    totalWeight[nickName] = float(vals[4])
    sampleWeight[nickName]= lumi*xsec[nickName]/totalWeight[nickName]
    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

# Stitch the DYJets and WJets samples

for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i) 
    sampleWeight[nn] = lumi/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + totalWeight[nn]/xsec[nn])

for i in range(1,4) :
    nn = 'W{0:d}JetsToLNu'.format(i) 
    sampleWeight[nn] = lumi/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + totalWeight[nn]/xsec[nn])

# create histograms
hBasePrompt, hTightPrompt = {}, {}
for h in hList :
    hName = "{0:s}BasePrompt".format(h)
    hBasePrompt[h] = TH1D(hName,hName,10,0.,100.)
    hName = "{0:s}TightPrompt".format(h)
    hTightPrompt[h] = TH1D(hName,hName,10,0.,100.)

for nickName in nickNames :
    inFileName = './MC/{0:s}/{0:s}.root'.format(nickName)
    print("Opening {0:s}".format(inFileName)) 
    inFile = TFile.Open(inFileName)
    inFile.cd()
    inTree = inFile.Get("Events")
    nentries = inTree.GetEntries()
    
    nEvents, totalWeight = 0, 0.
    sWeight = sampleWeight[nickName]
    DYJets = (nickName == 'DYJetsToLL')
    WJets  = (nickName == 'WJetsToLNu')
        
    for i, e in enumerate(inTree) :
        # impose any common selection criteria here
        # include only same sign events 
        if e.q_1*e.q_2 < 0. : continue
        H_LT = e.pt_1 + e.pt_2
        if H_LT > args.LTcut : continue

        sw = sWeight
        if e.LHE_Njets > 0 :
            if DYJets : sw = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
            if WJets  : sw = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)] 
        weight = e.weight*sw
        
        cat = cats[e.cat]
        if cat[2:] == 'et' :
            if e.gen_match_1 == 1 or e.gen_match_1 == 15 :
                hBasePrompt['e_et'].Fill(e.pt_1,weight)
                if e.iso_1 > 0.5 : hTightPrompt['e_et'].Fill(e.pt_1,weight)
            if e.gen_match_2 == 5 :
                hBasePrompt['t_et'].Fill(e.pt_2,weight)
                if e.iso_2_ID > 15 : hTightPrompt['t_et'].Fill(e.pt_2,weight)
        elif cat[2:] == 'mt' :
            if e.gen_match_1 == 1 or e.gen_match_1 == 15 :
                hBasePrompt['m_mt'].Fill(e.pt_1,weight)
                if e.iso_1 < 0.25 and e.iso_1_ID > 0 : hTightPrompt['m_mt'].Fill(e.pt_1,weight)
            if e.gen_match_2 == 5 :
                hBasePrompt['t_mt'].Fill(e.pt_2,weight)
                if e.iso_2_ID > 15 : hTightPrompt['t_mt'].Fill(e.pt_2,weight)
        else :
            if e.gen_match_1 == 5 :
                hBasePrompt['t1_tt'].Fill(e.pt_1,weight)
                if e.iso_1_ID > 15 : hTightPrompt['t1_tt'].Fill(e.pt_1,weight)
            if e.gen_match_2 == 5 :
                hBasePrompt['t2_tt'].Fill(e.pt_2,weight)
                if e.iso_2_ID > 15 : hTightPrompt['t2_tt'].Fill(e.pt_2,weight)

 
    print("{0:30s} {1:7d} {2:10.6f} {3:5d} {4:8.3f}".format(nickName,nentries,sampleWeight[nickName],nEvents,totalWeight))
    inFile.Close()

fOut.cd()
for h in hList :
    hBase[h].Write()
    hTight[h].Write()
    hBasePrompt[h].Write()
    hTightPrompt[h].Write()
    
    
exit()

    
# use these histograms to calculate the fake rate factors
gFakeRate = {} 
for h in hList :
    gFakeRate[h] = hTight[h].Clone() 
    gFakeRate[h].SetName("{0:s}Ratio".format(h))
    gFakeRate[h].Sumw2()
    gFakeRate[h].Divide(hBase[h])

tdrstyle.setTDRStyle()

H = 600
W = 1000
H_ref = 600
W_ref = 100

# references for T, B, L, R
T = 0.08*H_ref
B = 0.12*H_ref 
L = 0.16*W_ref
R = 0.04*W_ref

c = TCanvas('c1','c1',50,50,W,H)
c.SetFillColor(0)
c.SetBorderMode(0)
c.SetFrameFillStyle(0)
c.SetFrameBorderMode(0)

c.SetLeftMargin(L/W)
c.SetRightMargin(R/W)
c.SetTopMargin(T/H)
c.SetBottomMargin(B/H)

c.Divide(3,2)
lTeX = {}
xMin, xMax, yMin, yMax = 0., 80., 0., 0.25
for i, h in enumerate(hList) :
    c.cd(i+1)
    gFakeRate[h].GetXaxis().SetRangeUser(xMin,xMax)
    gFakeRate[h].SetMinimum(yMin)
    gFakeRate[h].SetMaximum(yMax)
    gFakeRate[h].SetLineWidth(2)
    gFakeRate[h].SetMarkerStyle(20)
    gFakeRate[h].SetMarkerSize(1.0)
    gFakeRate[h].SetMarkerColor(kRed)
    gFakeRate[h].GetXaxis().SetTitle('p_t (GeV/c)')
    gFakeRate[h].GetXaxis().SetLabelSize(0.06)
    gFakeRate[h].GetXaxis().SetTitleSize(0.06)
    gFakeRate[h].GetYaxis().SetTitle('p_fake')
    gFakeRate[h].GetYaxis().SetLabelSize(0.06)
    gFakeRate[h].GetYaxis().SetTitleSize(0.06)
        
    gFakeRate[h].Draw('e')
    lTeX[h] = TLatex(0.8*xMax,0.9*yMax,h)
    lTeX[h].SetTextSize(0.06) 
    lTeX[h].Draw()
    c.Update()
    
c.Draw()
raw_input()

fOut.cd()
fOut.Write()
fOut.Close()        


