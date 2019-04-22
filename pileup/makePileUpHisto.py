#
# read MC file and histogram pileup
# write result to output file
# 
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector  
import numpy as np
import generalFunctions as GF 
import time

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./VBF_sync_input.root',help="File to be analyzed.")
    parser.add_argument("-o","--outFileName",default='',help="File to be used for output.")
    parser.add_argument("-n","--nEvents",default=0,type=int,help="Number of events to process.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    return parser.parse_args()

args = getArgs()

inFileName = args.inFileName
print("Opening {0:s} as input.".format(inFileName))
inFile = TFile.Open(inFileName)
inFile.cd()
inTree = inFile.Get("Events")
nentries = inTree.GetEntries()

outFileName = GF.getOutFileName(args)
print("Opening {0:s} as output.".format(outFileName))
fOut = TFile( outFileName, 'recreate' )

tStart = time.time()
fData = TFile('data_pileup_{0:d}.root'.format(args.year))
hData = fData.Get('pileup')
print("hData={0:s}".format(str(hData)))
binWidth = hData.GetBinWidth(1)
xMin = hData.GetBinLowEdge(1)
nBins = hData.GetNbinsX()
xMax = xMin + nBins*binWidth
bins = np.linspace(xMin+0.5*binWidth,xMax-0.5*binWidth,nBins)
print("nBins={0:d} binWidth={1:f} xMin={2:f} xMax={3:f}".format(nBins,binWidth,xMin,xMax))

hMC = TH1D("hMC","hMC",nBins,xMin,xMax)
hWeight = TH1D("hWeight","hWeight",nBins,xMin,xMax)

nentries = inTree.GetEntries()
nMax = nentries
if args.nEvents > 0 : nMax = min(nMax,args.nEvents) 
print("Entering pileup loop.  Number of entries={0:d} nMax={1:d}".format(nentries,nMax))
tStart = time.time()
for i, e in enumerate(inTree) :
    if i >= nMax : break
    hMC.Fill(e.Pileup_nPU)
    hWeight.Fill(e.Pileup_nPU,e.genWeight)
    
print("After pileup loop:  time={0:.1f} s   time/event={1:.1f} us".format(time.time()-tStart,1.e6*(time.time()-tStart)/nMax))
fOut.cd()
hMC.Write()
hWeight.Write() 
fOut.Write()
fOut.Close()        

