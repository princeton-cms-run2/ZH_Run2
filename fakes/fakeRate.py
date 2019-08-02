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
    parser.add_argument("-l","--LTcut",default=75.,type=float,help="LT cut")
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
era=str(args.year)
nBins, xMin, xMax = 10, 0., 200.
lumi = 1000.
if era == '2016' : lumi *= 35.92
if era == '2017' : lumi *= 41.53
if era == '2018' : lumi *= 59.74
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }

# use this utility class to screen out duplicate events
DD = dupeDetector()


# open an output file
fOut = TFile('FakeRates_'+era+.'root', 'recreate' )

# create histograms
hBase, hTight = {}, {}
hList = ['e_et','m_mt','t_et','t_mt','t1_tt','t2_tt']
for h in hList :
    hName = "{0:s}Base".format(h)
    hBase[h] = TH1D(hName,hName,14,0.,140.)
    hName = "{0:s}Tight".format(h)
    hTight[h] = TH1D(hName,hName,14,0.,140.)
    
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
            H_LT = e.pt_1 + e.pt_2
            if H_LT > args.LTcut : continue

            # skip duplicate events
            if DD.checkEvent(e) : continue 

            cat = cats[e.cat]
            if cat[2:] == 'et' :
                hBase['e_et'].Fill(e.pt_1)
                hBase['t_et'].Fill(e.pt_2)
                if e.iso_1 > 0.5 :
                    hTight['e_et'].Fill(e.pt_1)
                if e.iso_2_ID > 15 :
                    hTight['t_et'].Fill(e.pt_2)
                    
            elif cat[2:] == 'mt' :
                hBase['m_mt'].Fill(e.pt_1)
                hBase['t_mt'].Fill(e.pt_2)
                if e.iso_1 < 0.25 and e.iso_1_ID > 0 : 
                    hTight['m_mt'].Fill(e.pt_1)
                if e.iso_2_ID > 15 :
                    hTight['t_mt'].Fill(e.pt_2)

            else :
                hBase['t1_tt'].Fill(e.pt_1)
                hBase['t2_tt'].Fill(e.pt_2)
                if e.iso_1_ID > 15 :
                    hTight['t1_tt'].Fill(e.pt_1)
                if e.iso_2_ID > 15 : 
                    hTight['t2_tt'].Fill(e.pt_2)
            
        inFile.Close()

DD.printSummary()
fOut.cd()

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
    
    gFakeRate[h].Draw('e')
    lTex1 = TLatex(0.5*xMax,0.5*yMax,'test')
    lTex1.SetTextSize(0.04) 
    lTex1.Draw()
    
c.Draw()
raw_input()

fOut.cd()
fOut.Write()
fOut.Close()        


