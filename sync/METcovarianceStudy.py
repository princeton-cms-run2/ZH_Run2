#
# study the MET covariance
#
from ROOT import TFile, TTree, TH1D, TH2D, TCanvas, TLorentzVector, kGreen, kRed, TLegend 

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

hCovXX = TH1D('covXX', 'covXX', 50, 0., 4000.)
hCovXX.GetXaxis().SetTitle('MET_covXX')
hCovXX.GetYaxis().SetTitle('Entries')

hCovYY = TH1D('covYY', 'covYY', 50, 0., 4000.)
hCovYY.GetXaxis().SetTitle('MET_covYY')
hCovYY.GetYaxis().SetTitle('Entries')

hCovXY = TH1D('covXY', 'covXY', 50, -1000., 1000.) 
hCovXY.GetXaxis().SetTitle('MET_covXY')
hCovXY.GetYaxis().SetTitle('Entries')

hCovVsPt = TH2D('CovVsPt','CovVsPt',50,0.,1000., 50,0.,4000.)
hCovVsPt.GetXaxis().SetTitle('MET_pt')
hCovVsPt.GetYaxis().SetTitle('covXX+covYY')

hCovRatioVsPhi = TH2D('CovRatioVsPhi','CovRatioVsPhi',50,-5.,5., 50, 0.,5.)
hCovRatioVsPhi.GetXaxis().SetTitle('MET_phi')
hCovRatioVsPhi.GetYaxis().SetTitle('covYY/covXX')

inFileName = args.inFileName
print("Opening {0:s} as input.".format(inFileName))
inFile = TFile.Open(inFileName)
inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()
nMax = nentries
print("nentries={0:d} nMax={1:d}".format(nentries,nMax))
if args.nEvents > 0 : nMax = min(args.nEvents,nentries)

for count, e in enumerate(inTree) :
    if count % 1000 == 0 :
        print("count={0:d}".format(count))
    if count > nMax : break
    for i in range(e.nElectron) :
        hCovXX.Fill(e.MET_covXX)
        hCovYY.Fill(e.MET_covYY)
        hCovXY.Fill(e.MET_covXY)
        hCovVsPt.Fill(e.MET_pt,e.MET_covXX+e.MET_covYY)
        hCovRatioVsPhi.Fill(e.MET_phi,e.MET_covYY/e.MET_covXX)
        
c1 = TCanvas("c1","c1",1000,750)
for h in [hCovXX,hCovYY,hCovXY,hCovVsPt,hCovRatioVsPhi] :
    h.Draw()
    c1.Update()
    c1.Draw()
    raw_input()







  
            

    
    


