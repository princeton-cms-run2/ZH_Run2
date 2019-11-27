__author__ = "Alexis Kalogeropoulos"
__description__ = "Simple script to make LaTex table from a given .root file - it needs arguments as described below. It will produce several txt a) per channel b) per process c) per group (ZZ4L, Reducible, etc). "

import os
import sys
from ROOT import TFile, TTree, TH1, TH1D, TCanvas, TLorentzVector
from array import *
import numpy as np
from decimal import *
#getcontext().prec = 3
from math import sqrt
import csv
import pandas as pn
import glob
import string

pn.set_option('display.float_format', lambda x: '%.2f' % x)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



def latex_with_lines(df, *args, **kwargs):
    kwargs['column_format'] = '|'.join([''] + ['l'] * df.index.nlevels
                                            + ['r'] * df.shape[1] + [''])
    res = df.to_latex(*args, **kwargs)
    res.replace('\\\\\n', '\\\\ \\hline\n')
    res.replace('bottomrule', 'hline')
    return res.replace('\\\\\n', '\\\\ \\hline\n')

def WriteLatexGroup (fileOut,array) :
    f = open(fileOut,'w')
    print >> f,'\\documentclass[10pt]{report}'
    print >> f,'\\usepackage{adjustbox}'
    print >> f,'\\begin{document}'
    print >> f,'\\begin{table}[htp]'
    print >> f,'\\caption{' + '{0:s} {1:s}'.format(args.selection, era) + '}'  
    print >> f,'\\begin{center}'
    #print >>f, cc.to_latex()
    f.write(array.to_latex(column_format = "l | " + " | ".join(["r"] * len(array.columns))))
    print >> f,'\\end{center}'
    print >> f,'\\end{table}'
    print >> f,'\\end{document}'
    f.write(fileOut)
    f.close()

    s = open(fileOut).read()
    s = s.replace('\\bottomrule','')
    s = s.replace('\\midrule','')
    s = s.replace('\\toprule','')
    s = s.replace('\\\\','\\\\ \\hline')
    fa = open(fileOut,'w')
    fa.write(s)
    fa.close()


def column(matrix, i):
    return [row[i] for row in matrix]


def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFile",default='MCsamples_2016.csv',help="Input file name.")
    parser.add_argument("-y","--year",default='2016',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="Select ZH or AZH")
    parser.add_argument("-c","--category",default='all',type=str,help="Categories")
    parser.add_argument("-n","--normalize",default='yes',type=str,help="scale to lumi, if no/0 then unsclaed yields, otherwise scale to 35.9/41.5/59.7 for 2016/2017/2018")
    parser.add_argument("-u","--usefromplots",default='no',type=str,help="what .root files to use. if is it yes, then it will look in the plotting dir for the file defined as with the -i argument")
    parser.add_argument("-i","--inplotsfile",default='allGroups_2016_OS_LT00.root',type=str,help="define the .root files to use for making the tables. Must be used with -u switch")
    return parser.parse_args()


args = getArgs()

incat=args.category

cats = [ 'eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
if incat !='all' : 
    cats =[]
    cats.append(incat)

cats.insert(0,'Cuts')

era=str(args.year)

command = "mkdir txt"
os.system(command)


if args.category not in cats and incat != 'all' : sys.exit("There is not such channel --> {0:s} <-- ...".format(incat))

fInplot = args.inplotsfile
usePlotFile= args.usefromplots



lumi = {'2016':35920, '2017':41530, '2018':59740}

nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}
#groups = ['Signal','Reducible','Rare','ZZ4L','data']
groups = ['Signal','ZZ4L','Reducible','Rare','data']

fIn=str(args.inFile)

if fIn == '' : fIn ='./MCsamples_'+era+'.csv'


for group in groups :
    nickNames[group] = []


#for line in open('./MCsamples_'+era+'_one.csv','r').readlines() :
for line in open(fIn,'r').readlines() :
    vals = line.split(',')
    nickName = vals[0]
    group = vals[1]
    nickNames[group].append(nickName)
    xsec[nickName] = float(vals[2])
    totalWeight[nickName] = float(vals[4])
    sampleWeight[nickName]= float(lumi[era])*xsec[nickName]/totalWeight[nickName]
    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

# Stitch the DYJets and WJets samples
'''
for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i)
    if 'DYJetsToLL' in totalWeight : sampleWeight[nn] = float(lumi[era])/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + totalWeight[nn]/xsec[nn])

for i in range(1,4) :
    nn = 'W{0:d}JetsToLNu'.format(i)
    if 'WJetsToLNu' in totalWeight : sampleWeight[nn] = float(lumi[era])/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + totalWeight[nn]/xsec[nn])
'''

# now add the data - presumably it should the merged data
#for eras in ['2017B','2017C','2017D','2017E','2017F'] :
    #for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
#for dataset in ['SingleMuon', 'SingleElectron'] :
for dataset in ['data'] :
    #nickName = '{0:s}_Run{1:s}'.format(dataset,era)
    nickName = '{0:s}_{1:s}'.format(dataset,era)
    totalWeight[nickName] = 1.
    sampleWeight[nickName] = 1.
    nickNames['data'].append(nickName)
    xsec[nickName] = 1.
#####################################3



channel=args.category
fIn=''
fIn_data = ''
fIn_mc = ''

b_usePlotFile = False

ccols=20 ##this must be equal to the nBins from the CutFlow histo
rrows=9


if usePlotFile.lower() == 'yes' : b_usePlotFile = True

for group in groups :
    rows, cols = (rrows, ccols) 
    yieldpergroup = [[0 for i in range(cols)] for j in range(rows)] 
    totalyield = [[0 for i in range(cols)] for j in range(rows)]
     

    for nickName in nickNames[group]:
        if b_usePlotFile:
            fIn_data = '../../plotting/'+fInplot
            fIn_mc = '../../plotting/'+fInplot
	else : 
	    fIn_data = '../../data/condor/{0:s}/{1:s}/{1:s}.root'.format(args.selection, nickName)
	    fIn_mc = '{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.selection, nickName, era)

        if group != 'data' : fIn = fIn_mc  #'{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.selection, nickName, era)
        else: fIn = fIn_data # '../../data/condor/{0:s}/{1:s}/{1:s}.root'.format(args.selection, nickName)
        inFile = TFile.Open(fIn)
        inFile.cd()
        #hW=''
        #if group != 'data' : hW = inFile.Get("hWeights")
        #inTree = inFile.Get("Events")
    
        header=nickName
        print ' opening ', fIn, nickName, group

        scale=str(args.normalize)
        ScaleToLumi= False

        if scale=="1" or scale.lower()=="true" or scale.lower() =="yes":  
            ScaleToLumi = True
            header=header+'_'+'{0:.3f}'.format(float(lumi[era]/1000))+'invfb'

        if ScaleToLumi : print "Events scaled to {0:.1f}/pb for xsec = {1:.3f} pb".format(float(lumi[era]),float(xsec[nickName]))
        if not ScaleToLumi : print "Events WILL NOT BE scaled to {0:.1f}/pb for xsec = {1:.3f} pb".format(float(lumi[era]),float(xsec[nickName]))



        arr = [[0 for i in range(cols)] for j in range(rows)] 
        cuts=[]
        cuts=['All', 'LeptonCount', 'Trigger', 'LeptonPair', 'FoundZ', 'GoodTauPair', 'VVtightTauPair']
	if  b_usePlotFile : cuts=[]

        result=[]
        product=1.
        if ScaleToLumi : product = float(sampleWeight[nickName])
			

        '''if 'all' not in channel :
	    if 'data' not in group and not b_usePlotFile : hist="hCutFlowWeighted_"+incat+'_'+nickName
	    else : hist="hCutFlow_"+incat
	    h1 = inFile.Get(hist)
	    
	    #for i in range(1,h1.GetNbinsX()) :
	    #    print h1.GetXaxis().GetBinLabel(i), h1.GetBinContent(i)*product
        else:
        '''
        count=0
	for cat in cats[1:]:
	    hist=''
	    if not b_usePlotFile :
	        if 'data' not in group : hist = "hCutFlowWeighted_"+cat
	        else : hist = "hCutFlow_"+cat

            else : 
	        hist = "hCutFlow_"+cat+'_'+nickName


	            #else : hist="hCutFlow_"+cat

	    htest = inFile.Get(hist)
	    for i in range(1,htest.GetNbinsX()) : 
	        #print ' test---------------', htest.GetXaxis().GetBinLabel(i), htest.GetBinContent(i), cat, nickName
	        arr[count][i-1] = '{:.2f}'.format(htest.GetBinContent(i)*product)
	        #print '===================',arr[count][i-1]
	        yieldpergroup[count][i-1] +=  float('{0:.2f}'.format(htest.GetBinContent(i)*product))
	        #arr[count][i-1] = 1
	        if len(cuts) == 0 :
	            for i in range(1,htest.GetNbinsX()) : cuts.append(htest.GetXaxis().GetBinLabel(i))
	    count+=1
       

        #### this part write a csv - commented out for the moment
        '''
        np.vstack([arr,cats])
        t_matrix = zip(*arr) 
        with open(nickName+'_'+group+'_'+era+"new_file.csv","w+") as my_csv:
            fieldnames = cats[1:]
            csvWriter = csv.DictWriter(my_csv, fieldnames=fieldnames)
            csvWriter.writeheader()

            csvWriter = csv.writer(my_csv,delimiter=',')
            csvWriter.writerows(t_matrix)

        with open(nickName+'_'+group+'_'+era+'_yields.txt', 'w') as f:
	    hh = nickName.replace('_','\\_')
	    print >> f,'\\documentclass[10pt]{report}'
	    print >> f,'\\usepackage{adjustbox}'
	    print >> f,'\\begin{document}'
	    print >> f,'\\begin{table}[htp]'
	    print >> f,'\\caption{' + '{0:s} {1:s}'.format(hh, era) + '}'  
	    print >> f,'\\begin{center}'
	    print >> f,'\\begin{adjustbox}{width=1\\textwidth}'
	    print >> f,'\\begin{tabular}{l r r r r r r r r }  \hline'
	    for i in cats : print >> f, '{} &'.format(i),
	    print >> f, '\hline'
        
	    lines = [' & \t'.join([str(x[i]) if len(x) > i else ' ' for x in arr]) for i in range(len(max(arr)))]
	    #lines = [' & \t'.join([str(x[i]) for x in arr]) for i in range(len(max(arr)))]
	    for i in range(len(cuts)):
	        if cuts[i] != '' : 
	            print >> f,'{} & {} \\\\ \\hline'.format(cuts[i], lines[i])



	    print >> f,'\\end{tabular}'
	    print >> f,'\\end{adjustbox}'
            print >> f,'\\end{center}'
            print >> f,'\\end{table}'
            print >> f,'\\end{document}'
         '''


    ### this is to create a .txt per group

    #print yieldpergroup, group
    #print len(yieldpergroup), group

    with open('txt/All_'+group+'_'+args.selection+'_'+era+'_yields.txt', 'w') as f:
        '''
	print >> f,'\\documentclass[10pt]{report}'
	print >> f,'\\usepackage{adjustbox}'
	print >> f,'\\begin{document}'
	print >> f,'\\begin{table}[htp]'
	print >> f,'\\caption{' + '{0:s} {1:s}'.format(group, era) + '}'  
	print >> f,'\\begin{center}'
	print >> f,'\\begin{adjustbox}{width=1\\textwidth}'
	print >> f,'\\begin{tabular}{l r r r r r r r r }  \hline'
	for i in cats : print >> f, '{} &'.format(i),
	print >> f, '\hline'
        '''
	#lines = [' & \t'.join([str(x[i]) if len(x) > i else ' ' for x in yieldpergroup]) for i in range(len(max(yieldpergroup)))]
	lines = ['  \t'.join([str(x[i]) if len(x) > i else ' ' for x in yieldpergroup]) for i in range(len(max(yieldpergroup)))]
	#for i in range(len(cuts)):
	for i in range(len(cuts)):
	    #if cuts[i] != '' : 
	    #    print >> f,'{} & {} \\\\ \\hline'.format(cuts[i], lines[i])
	    #if len(cuts[i]) != 0 : 
	    print >> f, '{}  {} '.format(cuts[i], lines[i])
        	

        '''
	print >> f,'\\end{tabular}'
	print >> f,'\\end{adjustbox}'
        print >> f,'\\end{center}'
        print >> f,'\\end{table}'
        print >> f,'\\end{document}'
	'''

    #for i in range(rows):
    #    for j in range(columns):

zz4l=[]
reducible=[]
rare=[]
signal=[]
Data=[]
cutlist=[]
allbkg=[]
e_allbkg=[]
  
cutlist.append( np.genfromtxt('txt/All_Signal_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=str,usecols=(0)))


for counter in range( len(cats[1:])) :
#for counter in range(1,len(cats)) :
    #print counter, cats[counter]
    zz4l.append( np.genfromtxt('txt/All_ZZ4L_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    reducible.append( np.genfromtxt('txt/All_Reducible_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    rare.append( np.genfromtxt('txt/All_Rare_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    Data.append( np.genfromtxt('txt/All_data_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    signal.append( np.genfromtxt('txt/All_Signal_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    allbkg.append(zz4l[counter] + reducible[counter] + rare[counter])
    #cutlist.append( np.genfromtxt('All_ZZ4L_{0:s}_yields.txt'.format(args.year), dtype=str,usecols=(0)))
    #allbkg = np.sum([counter-1] + zz4l[counter-1] + rare[counter-1] + reducible[counter-1], axis)
    #counter+=1


#data = {'names': cutlist, 'values': zz4l}

dfzz4l = pn.DataFrame(data=zz4l)
df2zz4l_t = dfzz4l.T
df2zz4l_t.index=[i for i in cutlist]
df2zz4l_t.columns=[i for i in cats[1:]]

dfrare = pn.DataFrame(data=rare)
df2rare_t = dfrare.T
df2rare_t.index=[i for i in cutlist]
df2rare_t.columns=[i for i in cats[1:]]
#df2rare_t.head()


dfreducible = pn.DataFrame(data=reducible)
df2reducible_t = dfreducible.T
df2reducible_t.index=[i for i in cutlist]
df2reducible_t.columns=[i for i in cats[1:]]
#df2reducible_t.head()

e_allbkg = pn.DataFrame(data=allbkg).pow(1./2)

e_dfallbkg = pn.DataFrame(data=e_allbkg)
e_df2allbkg_t = e_dfallbkg.T
e_df2allbkg_t.index=[i for i in cutlist]
e_df2allbkg_t.columns=[i for i in cats[1:]]


dfallbkg = pn.DataFrame(data=allbkg)
df2allbkg_t = dfallbkg.T
df2allbkg_t.index=[i for i in cutlist]
df2allbkg_t.columns=[i for i in cats[1:]]
#df2allbkg_t.head()

dfdata = pn.DataFrame(data=Data)
df2data_t = dfdata.T
df2data_t.index=[i for i in cutlist]
df2data_t.columns=[i for i in cats[1:]]
#df2data_t.head()

dfsignal = pn.DataFrame(data=signal)
df2signal_t = dfsignal.T
df2signal_t.index=[i for i in cutlist]
df2signal_t.columns=[i for i in cats[1:]]

df2zz4l_t.index=[i for i in cutlist]
df2zz4l_t.columns=[i for i in cats[1:]]
#df2zz4l_t.head()



c=pn.concat([df2zz4l_t, df2reducible_t, df2rare_t, df2allbkg_t, e_df2allbkg_t, df2data_t], axis=1)


#groups = ['Signal','Reducible','Rare','ZZ4L','data']
#print c

ngroup = groups
ngroup.insert(4,'All bkg')
ngroup.insert(5,'uncert bkg')

for cat in cats[1:] :
    cc=c[cat] 
    cc.to_latex()
    cc.columns=[i for i in groups[1:]]
    cc.index=[i for i in cutlist]

    fIn = 'txt/All_'+cat+'_'+args.selection+'_'+era+'yields.txt'

    with open(fIn, 'w') as f:
	print >> f,'\\documentclass[10pt]{report}'
	print >> f,'\\usepackage{adjustbox}'
	print >> f,'\\begin{document}'
	print >> f,'\\begin{table}[htp]'
	print >> f,'\\caption{' + '{0:s} {1:s} {2:s}'.format(cat, args.selection, era) +'}'  
	print >> f,'\\begin{center}'
        '''
	print >> f,'\\begin{adjustbox}{width=1\\textwidth}'
	#print >> f,'\\begin{tabular}{l r r r r r r r r }  \hline'
        f.write("\\begin{tabular}{l | " + " | ".join(["r"] * len(cc.columns)) + "} \\\hline \n")
        #f.write("\\begin{tabular}{l | " + " | ".join(["r"] * len(cc.head())) + "}\n")
        count=0
        for i, row in cc.iterrows():
            i_ = cc.index[count]
            f.write(" & ".join([str(x) for x in row.values]) + " \\\\\n")
            count+=1
	print >> f, '{} &'.format(i for i in cc.columns)
	print >> f, '\hline'
        '''
        f.write(cc.to_latex(column_format = "l | " + " | ".join(["r"] * len(cc.columns))))
        print >> f,'\\end{center}'
        print >> f,'\\end{table}'
        print >> f,'\\end{document}'

        '''
	print >> f,'\\end{tabular}'
	print >> f,'\\end{adjustbox}'
        '''


    s = open(fIn).read()
    s = s.replace('\\bottomrule','')
    s = s.replace('\\midrule','')
    s = s.replace('\\toprule','')
    s = s.replace('\\\\','\\\\ \\hline')
    f = open(fIn,'w')
    f.write(s)
    f.close()

WriteLatexGroup('txt/All_ZZ4L_'+args.selection+'_'+era+'_yields.txt',df2zz4l_t)
WriteLatexGroup('txt/All_Reducible_'+args.selection+'_'+era+'_yields.txt',df2reducible_t)
WriteLatexGroup('txt/All_Rare_'+args.selection+'_'+era+'_yields.txt',df2rare_t)
WriteLatexGroup('txt/All_data_'+args.selection+'_'+era+'_yields.txt',df2data_t)
WriteLatexGroup('txt/All_Allbkg_'+args.selection+'_'+era+'_yields.txt',df2allbkg_t)
WriteLatexGroup('txt/All_Signal_'+args.selection+'_'+era+'_yields.txt',df2signal_t)

command="sed -i '/0.0 &  /d' txt/*txt"
command1="sed -i 's/0.00 \\\\/0 \\\\/g' txt/*txt"
if  b_usePlotFile : 
    os.system(command)
os.system(command1)

print 'All txt files can be found in the ./txt dir....exiting'
