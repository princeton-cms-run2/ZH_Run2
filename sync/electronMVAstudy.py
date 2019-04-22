#
# study the electron MVA iso variable
#
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, kGreen, kRed, TLegend 

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-c","--channel",default='tt',help="Category (tt, et, mt) to be analyzed.")
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    return parser.parse_args()

args = getArgs()
print("args={0:s}".format(str(args)))
maxPrint = 10

hWPL = TH1D('Loose', 'Loose', 50, -1., 1.) 
hWPL.GetXaxis().SetTitle('Electron_mvaFall17noIso')
hWPL.GetYaxis().SetTitle('Entries')

hWP80 = TH1D('WP80', 'WP80', 50, -1., 1.) 
hWP80.GetXaxis().SetTitle('Electron_mvaFall17noIso')
hWP80.GetYaxis().SetTitle('Entries')

hWP90 = TH1D('WP90', 'WP90', 50, -1., 1.) 
hWP90.GetXaxis().SetTitle('Electron_mvaFall17noIso')
hWP90.GetYaxis().SetTitle('Entries')

hNotWP90 = TH1D('WP90', 'WP90', 50, -1., 1.) 
hNotWP90.GetXaxis().SetTitle('Electron_mvaFall17noIso')
hNotWP90.GetYaxis().SetTitle('Entries')

inFileName = args.inFileName
print("Opening {0:s} as input.".format(inFileName))
inFile = TFile.Open(inFileName)
inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
nMax = nentries
print("nentries={0:d} nMax={1:d}".format(nentries,nMax))
if args.nEvents > 0 : nMax = min(args.nEvents,nentries)

channel = args.channel

for count, e in enumerate(inTree) :
    if count % 1000 == 0 :
        print("count={0:d}".format(count))
        print("Electrons                           Lost  \n # Q    Pt   Eta   Phi   Iso   Qual Hits  MVA   dxy     dz   MVA  Loose WP90  WP80")
    if count > nMax : break
    for i in range(e.nElectron) :
        if e.Electron_pt[i] < 25. : continue
        if abs(e.Electron_dxy[i]) > 0.045 : continue
        if abs(e.Electron_dz[i]) > 0.2 : continue

        if ord(e.Electron_lostHits[i]) > 1 : continue 
        if not e.Electron_convVeto[i] : continue
        if abs(e.Electron_eta[i]) > 2.1 : continue

        MVA = e.Electron_mvaFall17noIso[i] 
        if e.Electron_mvaFall17noIso_WPL[i] : hWPL.Fill(MVA)
        if e.Electron_mvaFall17noIso_WP90[i] : hWP90.Fill(MVA)
        if not e.Electron_mvaFall17noIso_WP90[i] : hNotWP90.Fill(MVA)
        if e.Electron_mvaFall17noIso_WP80[i] : hWP80.Fill(MVA)
        if not e.Electron_mvaFall17noIso_WP90[i] and MVA > 0.8 :
            eSign = '+'
            if e.Electron_charge[i] < 0 : eSign = '-'
            print("{0:2d} {1:2s}{2:5.1f}{3:6.2f}{4:6.2f}{5:7.3f}{6:6d}{7:5d}{8:8.3f}{9:7.3f}{10:7.3f} {11} {12} {13}".format(i,eSign,
            e.Electron_pt[i],e.Electron_eta[i],e.Electron_phi[i],e.Electron_miniPFRelIso_all[i],
            e.Electron_cutBased[i],ord(e.Electron_lostHits[i]),e.Electron_mvaFall17noIso[i],
            e.Electron_dxy[i],e.Electron_dz[i],e.Electron_mvaFall17noIso_WPL[i],e.Electron_mvaFall17noIso_WP90[i],e.Electron_mvaFall17noIso_WP80[i]))
            
c1 = TCanvas("c1","c1",1000,750)
c1.SetLogy()
hWP90.GetYaxis().SetRangeUser(0.5,200000.)
hWP90.SetLineColor(kGreen)
hWP90.SetLineWidth(2);
hWP90.Draw()
hNotWP90.SetLineColor(kRed)
hNotWP90.SetLineWidth(2);
hNotWP90.Draw("same")
legend = TLegend(0.2,0.8,0.40,0.90);
#legend.SetHeader("T","C"); // option "C" allows to center the header
legend.AddEntry(hWP90,"Tracks passing WP90")
legend.AddEntry(hNotWP90,"Tracks failing WP90") 
legend.Draw()
c1.Draw()
raw_input()







  
            

    
    


