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
    parser.add_argument("--looseCuts",action='store_true',help="Loose cuts") 
    
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
nBins, xMin, xMax = 10, 0., 200.
groups = ['Signal','Reducible','Rare','ZZ4L','data']
lumi = 1000.*41.8 
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
groups = ['Signal','Reducible','Rare','ZZ4L','data']
tightCuts = not args.looseCuts 

# use this utility class to screen out duplicate events
DD = {}
for cat in cats.values() :
    DD[cat] = dupeDetector()

# dictionary where the group is the key
hMC = {}

# dictionary where the nickName is the key
nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}

for group in groups :
    nickNames[group] = []

#       0                 1       2        3        4        5            6
# GluGluHToTauTau	Signal	48.58	9259000	198813970.4	 	/GluGluHToTauTau_...

# make a first pass to get the weights 
for line in open('MCsamples.csv','r').readlines() :
    vals = line.split(',')
    nickName = vals[0]
    group = vals[1]
    nickNames[group].append(nickName) 
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
    
# now add the data 
for era in ['2017B','2017C','2017D','2017E','2017F'] :
    for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
        nickName = '{0:s}_Run{1:s}'.format(dataset,era)
        totalWeight[nickName] = 1.
        sampleWeight[nickName] = 1.
        nickNames['data'].append(nickName) 


print("tightCuts={0}".format(tightCuts))
if tightCuts :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}.root'.format(args.year,args.sign,int(args.LTcut))
else :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_loose.root'.format(args.year,args.sign,int(args.LTcut))
    
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
        #if nickName == 'TTTo2L2Nu' : continue
        #if nickName == 'TTToSemiLeptonic' : continue 
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

        # resume here 
        nEvents, totalWeight = 0, 0.
        sWeight = sampleWeight[nickName]
        DYJets = (nickName == 'DYJetsToLL')
        WJets  = (nickName == 'WJetsToLNu')
        
        for i, e in enumerate(inTree) :
            sw = sWeight
            if e.LHE_Njets > 0 :
                if DYJets : sw = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
                if WJets  : sw = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)] 
            weight = e.weight*sw
            cat = cats[e.cat]

            if tightCuts :
                # for 'et' modes, tighten electron selection
           
                if cat[2:] == 'et' and e.iso_1 < 0.5 : continue
            
                # for 'mt' modes, tighten muon selection
                if cat[2:] == 'mt' :
                    if e.iso_1 > 0.25 : continue
                    if e.iso_1_ID < 1 : continue
                
                # impose tight tau selection 
                if e.iso_2_ID < 16 : continue 
                if cat[2:] == 'tt' and e.iso_1_ID < 16 : continue
            
            if args.sign == 'SS':
                if e.q_1*e.q_2 < 0. : continue
            else :
                if e.q_1*e.q_2 > 0. : continue
                
            H_LT = e.pt_1 + e.pt_2
            if H_LT < args.LTcut : continue
            if group == 'data' :
                if DD[cat].checkEvent(e) : continue 
            if cat == 'mmtt' :
                totalWeight += weight
                nEvents += 1
                #if nickName == 'TTTo2L2Nu' :
                #    print("Good event e.weight={0:f} sw={1:f} weight={2:f}".format(e.weight,sw,weight))
                    
            hMC[group][cat].Fill(e.m_sv,weight)

        print("{0:30s} {1:7d} {2:10.6f} {3:5d} {4:8.3f}".format(nickName,nentries,sampleWeight[nickName],nEvents,totalWeight))
        inFile.Close()
    fOut.cd()
    for cat in cats.values()[0:6] : hMC[group][cat].Write() 

for cat in cats.values():
    print("Duplicate summar for {0:s}".format(cat))
    DD[cat].printSummary()
    
fOut.cd()
fOut.Write()
fOut.Close()        


