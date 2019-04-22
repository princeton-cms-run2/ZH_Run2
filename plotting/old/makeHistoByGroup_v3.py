#
# read MC file root files and histogram by group 
#

from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector  

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
groups = ['Signal','Reducible','Rare','ZZ4L','data']
lumi = 1000.*41.8 
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }

# dictionaries, where the group is the key
nickNames, xSecs, weights, hMC = {}, {}, {}, {}  
for group in groups :
    nickNames[group] = []
    weights[group] = {}

#       0                 1       2        3       4    5            6
# GluGluHToTauTau	Signal	48.58	9259000	 	 	/GluGluHToTauTau_M1...
for line in open('MCsamples.csv','r').readlines() :
    vals = line.split(',') 
    group = vals[1] 
    nickNames[group].append(vals[0])
    weights[group][vals[0]]= lumi*float(vals[2])/float(vals[3])
    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} nGen={3:10d} weight={4:10.6f}".format(
        group,vals[0],float(vals[2]),int(vals[3]),weights[group][vals[0]]))

# now add the data 
for era in ['2017B','2017C','2017D','2017E','2017F'] :
    for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
        nickName = '{0:s}_Run{1:s}'.format(dataset,era)
        nickNames['data'].append(nickName)
        weights['data'][nickName] = 1.
        
outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut)) 
print("Opening {0:s} as output.".format(outFileName))
fOut = TFile( outFileName, 'recreate' )
for group in groups :
    fOut.cd()
    hMC[group] = {}
    for cat in cats.values()[0:6] :
        hName = 'h{0:s}_{1:s}_Mtt'.format(group,cat)
        hMC[group][cat] = TH1D(hName,hName,nBins,xMin,xMax)
    print("\nInstantiating TH1D {0:s}".format(hName))
    print("      Nickname                 Entries    Wt/Evt  Ngood   Tot Wt")
    for nickName in nickNames[group] :
        if nickName == 'TTTo2L2Nu' : continue
        if nickName == 'TTToSemiLeptonic' : continue 
        inFileName = './MC/{0:s}/{0:s}.root'.format(nickName)
        if group == 'data' : inFileName = './data/{0:s}/{0:s}.root'.format(nickName)
        try :
            inFile = TFile.Open(inFileName)
            inFile.cd()
            inTree = inFile.Get("Events")
            nentries = inTree.GetEntries()
        except AttributeError :
            print("  Failure on file {0:s}".format(inFileName))
            exit()

        nEvents, totalWeight = 0, 0.
        for i, e in enumerate(inTree) :
            weight = e.weight*weights[group][nickName]
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
            if cat == 'eett' :
                totalWeight += weight
                nEvents += 1
            hMC[group][cat].Fill(e.m_sv,weight)

        print("{0:30s} {1:7d} {2:10.6f} {3:5d} {4:8.3f}".format(nickName,nentries,weights[group][nickName],nEvents,totalWeight))
        inFile.Close()
    fOut.cd()
    for cat in cats.values()[0:6] : hMC[group][cat].Write() 

fOut.cd()
fOut.Write()
fOut.Close()        


