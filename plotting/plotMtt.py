#
# read MC file root files and histogram by group 
#

from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, kBlack, TLatex, gStyle
import tdrstyle

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    parser.add_argument("-l","--LTcut",default=0.,type=float,help="H_LTcut")
    parser.add_argument("-s","--sign",default='OS',help="Opposite or same sign (OS or SS).")
    return parser.parse_args()

args = getArgs()
nBins, xMin, xMax = 10, 0., 200.
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }

tdrstyle.setTDRStyle()

outFileName = 'Mtt_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut)) 
print("Opening {0:s} as output.".format(outFileName))
fOut = TFile( outFileName, 'recreate' )
inFileName = './MC/ZHToTauTau/ZHToTauTau.root'
inFile = TFile.Open(inFileName)

inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
hMC = {}
for cat in cats.values()[0:6] :
    hName = 'h{0:s}_Mtt'.format(cat)
    hMC[cat] = TH1D(hName,hName,nBins,xMin,xMax)
        
for i, e in enumerate(inTree) :
    cat = cats[e.cat]
    # impose tight tau selection 
    if e.iso_2_ID < 16 : continue 
    if cat[2:] == 'tt' and e.iso_1_ID < 16 : continue
    if args.sign == 'SS':
        if e.q_1*e.q_2 < 0. : continue
    else :
        if e.q_1*e.q_2 > 0. : continue
            
    H_LT = e.pt_1 + e.pt_2
    if H_LT < args.LTcut : continue
    hMC[cat].Fill(e.m_sv,1.)

# plot histograms

gStyle.SetOptStat("mr")

for cat in cats.values():
    hMC[cat].SetMarkerStyle(20)
    hMC[cat].SetMarkerSize(1.0)
    hMC[cat].SetLineWidth(2)
    hMC[cat].SetLineColor(kBlack)
    #hMC[cat].SetOptStat("mr")
    c = TCanvas('c1','c1',400,50,600,600)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.cd()

    hMC[cat].Draw('e')
    hMC[cat].GetXaxis().SetTitle('Mtt (GeV)')
    hMC[cat].GetYaxis().SetTitle("Events")
    hMax = hMC[cat].GetMaximum()
    txt = TLatex(140.,.9*hMax,'{0:s}'.format(cat))
    txt.Draw() 
    raw_input()

#inFile.Close()
fOut.cd()
for cat in cats.values()[0:6] : hMC[cat].Write() 

fOut.cd()
fOut.Write()
fOut.Close()        


