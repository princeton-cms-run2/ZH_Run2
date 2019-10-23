#
# read MC file and histogram pileup
# write result to output file
# 
from ROOT import TFile, gROOT, TCanvas
import os
import os.path

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./MCsamples_2017.csv',help="File to be analyzed.")
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    return parser.parse_args()

args = getArgs()
era=str(args.year)

# get list of nickNames from input file
nickNames = []
dataset = {}
for line in open(args.inFileName,'r').readlines() :
    nickName = line.split(',')[0]
    ds = line.split(',')[6].strip()
    if len(ds) < 5 : continue 
    nickNames.append(nickName)
    dataset[nickName] = ds 
    
print("len(nickNames)={0:d}".format(len(nickNames)))
    
hIn, hW = {}, {}
for nickName in nickNames :
    cf = os.path.isfile("./{0:s}_{1:s}/temp.root".format(nickName,era))
    if not cf :
	#os.system("hadd -f -k ./{0:s}_{1:s}/temp.root ./{0:s}_{1:s}/{0:s}_*.root".format(nickName,era))
	os.system("hadd -f -k ./{0:s}_{1:s}/temp.root ./{0:s}_{1:s}/*_*.root".format(nickName,era))
    inFile = TFile.Open("./{0:s}_{1:s}/temp.root".format(nickName,era))
    inFile.cd()
    hh = inFile.Get("hMC")
    h2 = inFile.Get("hWeight")
    gROOT.cd() 
    hIn[nickName] = hh.Clone("hMC_{0:s}".format(nickName))
    hW[nickName]  = h2.Clone("hW_{0:s}".format(nickName))
    print("Before close: hIn[{0:s}]={1:s}".format(nickName,str(hIn[nickName])))
    hIn[nickName].Print() 
    inFile.Close()
    print(" After close: hIn[{0:s}]={1:s}".format(nickName,str(hIn[nickName])))
    print("hIn.keys()={0:s}".format(str(hIn.keys())))

if False :
    c1 = TCanvas("c1","c1",1000,750)
    for nickName in hIn.keys() :
        hIn[nickName].Draw()
        c1.Update() 
        c1.Draw()
        print("Drawing {0:s}".format(nickName))
        raw_input()

outLines = []
print("Before opening f.")
fOut= ("MC_{0:s}.root").format(args.year)
f = TFile(fOut, 'recreate' )
print("After opening f.")
for nickName in hIn.keys() :
    print("Adding {0:s} and {1:s} to output file.".format(str(hIn[nickName]),str(hW[nickName])))
    nEntries = hIn[nickName].GetEntries()
    totalWeight = hW[nickName].GetSumOfWeights()
    print("nickName = {0:30s} entries={1:9.1f} weight={2:12.1f}".format(nickName,nEntries,totalWeight))
    outLines.append("{0:s}, ,{1:.1f},{2:.1f}, ,{3:s}\n".format(nickName,nEntries,totalWeight,dataset[nickName])) 
    hIn[nickName].Write()
    hW[nickName].Write() 
f.Close()
open('temp.csv','w').writelines(outLines)

