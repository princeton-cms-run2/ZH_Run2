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
    parser.add_argument("--MConly",action='store_true',help="MC only") 
    parser.add_argument("--looseCuts",action='store_true',help="Loose cuts")
    parser.add_argument("--unBlind",action='store_true',help="Unblind signal region for OS")
    
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

def getFakeWeights(f1,f2) :
    w1 = f1/(1.-f1)
    w2 = f2/(1.-f2)
    w0 = w1*w2
    return w1, w2, w0

def trigweight(e,cat)
    trigw = 1.
    if cat == 'eeet' or cat == 'mmmt' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. : trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T1_MC) ))

	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. : trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ))

	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ))

    if cat == 'eemt' or cat == 'mmet' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC = 0. : trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC != 0. : trigw = float(   (e.trig_Lp_Data/e.trig_Lp_MC) * (e.trig_Lp_Data/e.trig_Lp_MC)   )
	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC = 0. : trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC != 0. : trigw = float(   (e.trig_Lm_Data/e.trig_Lm_MC) * (e.trig_Lm_Data/e.trig_Lm_MC)   )
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ) )
	    if trig_T1_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) )  * float(e.trig_T1_Data/e.trig_T1_MC) )

    if cat == 'eeem' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0.: trigw = float(e.trig_Lp_Data/e.trig_Lp_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T1_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T1_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))

	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0.: trigw = float(e.trig_Lm_Data/e.trig_Lm_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))

	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ))
	    if trig_T1_MC == 0. and trig_T2_MC != 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ) 
	    if trig_T1_MC != 0. and trig_T2_MC != 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T1_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T1_MC) ) * float(e.trig_T2_Data/e.trig_T2_MC))

    if cat == 'mmem' :
	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC == 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lp_Data/e.trig_Lp_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lp_Data/e.trig_Lp_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T2_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lp_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_T2_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))

	if e.trig_Lp_MC == 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lm_Data/e.trig_Lm_MC)
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(e.trig_Lm_Data/e.trig_Lm_MC) * float(e.trig_T2_Data/e.trig_T2_MC)
	    if trig_T1_MC == 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC != 0. : trigw = float(      (1 - (1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))

	if e.trig_Lp_MC != 0. and  e.trig_Lm_MC != 0. : 
	    if trig_T1_MC == 0. and trig_T2_MC == 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ))
	    if trig_T1_MC != 0. and trig_T2_MC == 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))
	    if trig_T1_MC == 0. and trig_T2_MC != 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ) 
	    if trig_T1_MC != 0. and trig_T2_MC != 0.: trigw = float(  (1 - (1-e.trig_Lp_Data)*(1-e.trig_Lm_Data)*(1-e.trig_T2_Data)) /  (1 - (1-e.trig_Lp_MC)*(1-e.trig_Lm_MC)*(1-e.trig_T2_MC) ) * float(e.trig_T1_Data/e.trig_T1_MC))

    return trigw





args = getArgs()
nBins, xMin, xMax = 10, 0., 200.
groups = ['Signal','Reducible','Rare','ZZ4L','data']
lumi = 1000.*41.8 
#cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem', 9:'et', 10:'mt', 11:'tt' }
groups = ['Signal','Reducible','Rare','ZZ4L','data']
tightCuts = not args.looseCuts 
dataDriven = not args.MConly

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
for line in open('./MC/MCsamples.csv','r').readlines() :
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
    if args.MConly :
        print("args.MConly is TRUE")
        outFileName = outFileName.replace('.root','_MC.root') 
else :
    outFileName = 'allGroups_{0:d}_{1:s}_LT{2:02d}_loose.root'.format(args.year,args.sign,int(args.LTcut))
    
print("Opening {0:s} as output.".format(outFileName))
fOut = TFile( outFileName, 'recreate' )

#fe, fm, ft_et, ft_mt, f1_tt, f2_tt   = 0.0456, 0.0935, 0.1391, 0.1284, 0.0715, 0.0609
# values with nbtag = 0 cut 
fe, fm, ft_et, ft_mt, f1_tt, f2_tt   = 0.0390, 0.0794, 0.1397, 0.1177, 0.0756, 0.0613
fW1, fW2, fW0 = {}, {}, {}
fW1['et'], fW2['et'], fW0['et'] = getFakeWeights(fe,ft_et)
fW1['mt'], fW2['mt'], fW0['mt'] = getFakeWeights(fm,ft_mt)
fW1['tt'], fW2['tt'], fW0['tt'] = getFakeWeights(f1_tt,f2_tt)
fW1['em'], fW2['em'], fW0['em'] = getFakeWeights(fe,fm)

global getsf,sf
for group in groups :
    fOut.cd()
    hMC[group] = {}
    for cat in cats.values()[0:8] :
        hName = 'h{0:s}_{1:s}_Mtt'.format(group,cat)
        hMC[group][cat] = TH1D(hName,hName,nBins,xMin,xMax)
    print("\nInstantiating TH1D {0:s}".format(hName))
    print("      Nickname                 Entries    Wt/Evt  Ngood   Tot Wt")
    for nickName in nickNames[group] :
        isData = False 
        inFileName = './MC/condor/{0:s}/{0:s}.root'.format(nickName)
        if group == 'data' :
            isData = True
            inFileName = './data/{0:s}/{0:s}.root'.format(nickName)
        try :
            inFile = TFile.Open(inFileName)
            inFile.cd()
            inTree = inFile.Get("Events")
            nentries = inTree.GetEntries()
        except AttributeError :
            print("  Failure on file {0:s}".format(inFileName))
            exit()

        # resume here
        nEvents, trigw, totalWeight = 0, 1., 0.
        sWeight = sampleWeight[nickName]
        DYJets = (nickName == 'DYJetsToLL')
        WJets  = (nickName == 'WJetsToLNu')

        for i, e in enumerate(inTree) :
            hGroup = group
            #if e.nbtag > 0 : continue
            sw = sWeight
            if e.LHE_Njets > 0 :
                if DYJets : sw = sampleWeight['DY{0:d}JetsToLL'.format(e.LHE_Njets)]
                if WJets  : sw = sampleWeight['W{0:d}JetsToLNu'.format(e.LHE_Njets)] 
            weight = e.weight*sw

            ww = weight
            #s = sf.checkFile()

            cat = cats[e.cat]
            if tightCuts :
                if cat[2:] == 'et' : tight1 = e.iso_1 > 0.5 
                if cat[2:] == 'mt' : tight1 = e.iso_1 < 0.25 and e.iso_1_ID > 0.5
                if cat[2:] == 'tt' : tight1 = e.iso_1_ID > 15
                tight2 = e.iso_2_ID > 15
                if cat[2:] == 'em' :
                    tight1 = e.iso_1 > 0.5
                    tight2 = e.iso_2 < 0.25 and e.iso_2_ID > 0.5
                    
                if group == 'data' :
                    if dataDriven :
                        hGroup = 'Reducible'
                        if not tight1 and tight2 : ww = fW1[cat[2:]]
                        elif tight1 and not tight2 : ww = fW2[cat[2:]]
                        elif not (tight1 or tight2) : ww = -fW0[cat[2:]]
                        else :
                            ww = 1.
                            hGroup = 'data'
                    else :
                        hGroup = 'data'
                        #print("group = data  cat={0:s} tight1={1} tight2={2} ww={3:f}".format(cat,tight1,tight2,ww))
                        if not (tight1 and tight2) : continue 
                        
                else : 
                    if not (tight1 and tight2) : continue
                    #print("Good MC event: group={0:s} nickName={1:s} cat={2:s} gen_match_1={3:d} gen_match_2={4:d}".format(
                    #    group,nickName,cat,e.gen_match_1,e.gen_match_2))
                    if dataDriven :   # include only events with MC matching
                        if cat[2] == 'e' or cat[2] == 'm':
                            if not (e.gen_match_1 == 1 or e.gen_match_1 == 15) : continue
                        else :
                            if not e.gen_match_1 == 5 : continue
                        if cat[3] == 'e' or cat[3] == 'm' :
                            if not (e.gen_match_2 == 1 or e.gen_match_2 == 15) : continue
                        else : 
                            if not e.gen_match_2 == 5 : continue
                                        
                #elif group == 'Rare' or group == 'ZZ4L' or group == 'Signal' :
                #    if not (tight1 and tight2) : continue         
                                        
            if args.sign == 'SS':
                if e.q_1*e.q_2 < 0. : continue
            else :
                if e.q_1*e.q_2 > 0. : continue
                if hGroup == 'data' and not args.unBlind and e.m_sv > 80. and e.m_sv < 140. : continue                 
            H_LT = e.pt_1 + e.pt_2
            if H_LT < args.LTcut : continue
            if group == 'data' :
                if DD[cat].checkEvent(e) : continue 
            if cat == 'mmtt' :
                totalWeight += ww
                nEvents += 1


            trigw_ = trigweight(e,cat)

            if e.is_trig ==1 :  hMC[hGroup][cat].Fill(e.m_sv,ww*trigw_)

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


