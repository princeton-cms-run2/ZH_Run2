__author__ = "Alexis Kalogeropoulos"
__description__ = "Simple script to make LaTex table from a given .root file - it needs arguments as described below. It will produce several txt a) per channel b) per process c) per group (ZZ4L, Reducible, etc). "


import sys
from ROOT import TFile, TTree, TH1, TH1D, TCanvas, TLorentzVector
from array import *
import numpy as np
from decimal import *
getcontext().prec = 2
import csv
import pandas as pn
import glob
import string


def latex_with_lines(df, *args, **kwargs):
    kwargs['column_format'] = '|'.join([''] + ['l'] * df.index.nlevels
                                            + ['r'] * df.shape[1] + [''])
    res = df.to_latex(*args, **kwargs)
    res.replace('\\\\\n', '\\\\ \\hline\n')
    res.replace('bottomrule', 'hline')
    return res.replace('\\\\\n', '\\\\ \\hline\n')




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
    parser.add_argument("-n","--normalize",default='no',type=str,help="scale to lumi, if no/0 then unsclaed yields, otherwise scale to 35.9/41.5/59.7 for 2016/2017/2018")
    return parser.parse_args()


args = getArgs()


cats = [ 'eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
cats.insert(0,'Cuts')

era=str(args.year)

lumi = {'2016':35920, '2017':41530, '2018':59740}

nickNames, xsec, totalWeight, sampleWeight = {}, {}, {}, {}
#groups = ['Signal','Reducible','Rare','ZZ4L','data']
groups = ['Signal','ZZ4L','Reducible','Rare','data']

for group in groups :
    nickNames[group] = []


for line in open('./MCsamples_'+era+'_one.csv','r').readlines() :
#for line in open('./MCsamples_'+era+'.csv','r').readlines() :
    vals = line.split(',')
    nickName = vals[0]
    group = vals[1]
    nickNames[group].append(nickName)
    xsec[nickName] = float(vals[2])
    totalWeight[nickName] = float(vals[4])
    sampleWeight[nickName]= lumi[era]*xsec[nickName]/totalWeight[nickName]
    print("group={0:10s} nickName={1:20s} xSec={2:10.3f} totalWeight={3:11.1f} sampleWeight={4:10.6f}".format(
        group,nickName,xsec[nickName],totalWeight[nickName],sampleWeight[nickName]))

# Stitch the DYJets and WJets samples

for i in range(1,5) :
    nn = 'DY{0:d}JetsToLL'.format(i)
    if 'DYJetsToLL' in totalWeight : sampleWeight[nn] = lumi[era]/(totalWeight['DYJetsToLL']/xsec['DYJetsToLL'] + totalWeight[nn]/xsec[nn])

for i in range(1,4) :
    nn = 'W{0:d}JetsToLNu'.format(i)
    if 'WJetsToLNu' in totalWeight : sampleWeight[nn] = lumi[era]/(totalWeight['WJetsToLNu']/xsec['WJetsToLNu'] + totalWeight[nn]/xsec[nn])

# now add the data - presumably it should the merged data
#for eras in ['2017B','2017C','2017D','2017E','2017F'] :
#for eras in ['2016'] :
    #for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
for dataset in ['SingleMuon'] :
    nickName = '{0:s}_Run{1:s}'.format(dataset,era)
    totalWeight[nickName] = 1.
    sampleWeight[nickName] = 1.
    nickNames['data'].append(nickName)
#####################################3



channel=args.category
fIn=''
for group in groups :
    rows, cols = (8, 9) 
    yieldpergroup = [[0 for i in range(cols)] for j in range(rows)] 
    totalyield = [[0 for i in range(cols)] for j in range(rows)] 

    for nickName in nickNames[group]:
        if group != 'data' : fIn = '{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.selection, nickName, era)
        else: fIn = '../../data/condor/{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.selection, nickName, era)
        inFile = TFile.Open(fIn)
        inFile.cd()
    
        hW = inFile.Get("hWeights")
        inTree = inFile.Get("Events")
    
        nentries = inTree.GetEntries()

        header=nickName
        print ' opening ', fIn, nickName, group, nentries, hW.GetSumOfWeights()

        scale=str(args.normalize)
        ScaleToLumi=False

        if scale=="1" or scale=="true" or scale=="True" or scale == "No" or scale == "no": 
            ScaleToLumi = True
            header=header+'_'+'{0:.2f}'.format(float(lumi[era]/1000))+'invfb'

        if ScaleToLumi : print "Events scaled to {0:.2f}/fb for xsec = {1:.3f} pb".format(float(lumi[era]/1000),float(xsec[nickName]))


        arr = [[0 for i in range(cols)] for j in range(rows)] 
        cuts=[]
        result=[]
        product=1.
        if ScaleToLumi : product = float(sampleWeight[nickName])
			
	    #print 'The weight will be', product, xsec, lumi, hW.GetSumOfWeights()

        if 'all' not in channel :
	    hist="hCutFlow_"+cat
	    h1 = inFile.Get(hist)
	    
	    for i in range(1,h1.GetNbinsX()) :
	        print h1.GetXaxis().GetBinLabel(i), h1.GetBinContent(i)*product

        else:
            count=0
	    for cat in cats[1:]:
	        hist="hCutFlow_"+cat
	        htest = inFile.Get(hist)
	        for i in range(1,htest.GetNbinsX()) : 
	            arr[count][i-1] = '{0:.2f}'.format(htest.GetBinContent(i)*product)
		    #print '===================',arr[count][i-1]
	            yieldpergroup[count][i-1] +=  float( '{0:.2f}'.format(htest.GetBinContent(i)*product))
	            #arr[count][i-1] = 1
		cuts=['All', 'LeptonCount', 'Trigger', 'LeptonPair', 'FoundZ', 'GoodTauPair', 'VVtightTauPair']
	        count+=1
       

        #### this part write a csv - commented for the moment
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

    with open('All_'+group+'_'+args.selection+'_'+era+'_yields.txt', 'w') as f:
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
	    #if cuts[i] != '' : 
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
data=[]
cutlist=[]
allbkg=[]
  
cutlist.append( np.genfromtxt('All_Signal_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=str,usecols=(0)))


for counter in range( len(cats[1:])) :
#for counter in range(1,len(cats)) :
    #print counter, cats[counter]
    zz4l.append( np.genfromtxt('All_ZZ4L_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    reducible.append( np.genfromtxt('All_Reducible_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    rare.append( np.genfromtxt('All_Rare_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    data.append( np.genfromtxt('All_data_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    signal.append( np.genfromtxt('All_Signal_{0:s}_{1:s}_yields.txt'.format(args.selection, args.year), dtype=None,usecols=(counter+1)))
    allbkg.append(zz4l[counter] + reducible[counter] + rare[counter])
    #cutlist.append( np.genfromtxt('All_ZZ4L_{0:s}_yields.txt'.format(args.year), dtype=str,usecols=(0)))
    #allbkg = np.sum([counter-1] + zz4l[counter-1] + rare[counter-1] + reducible[counter-1], axis)
    #counter+=1


data = {'names': cutlist, 'values': zz4l}

dfzz4l = pn.DataFrame(data=zz4l)
df2zz4l_t = dfzz4l.T

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

dfallbkg = pn.DataFrame(data=allbkg)
df2allbkg_t = dfallbkg.T
df2allbkg_t.index=[i for i in cutlist]
df2allbkg_t.columns=[i for i in cats[1:]]
#df2allbkg_t.head()

dfdata = pn.DataFrame(data=rare)
df2data_t = dfdata.T
df2data_t.index=[i for i in cutlist]
df2data_t.columns=[i for i in cats[1:]]
#df2data_t.head()


df2zz4l_t.index=[i for i in cutlist]
df2zz4l_t.columns=[i for i in cats[1:]]
#df2zz4l_t.head()


print df2zz4l_t


print df2rare_t




c=pn.concat([df2zz4l_t, df2rare_t, df2reducible_t, df2allbkg_t,df2data_t], axis=1)


#groups = ['Signal','Reducible','Rare','ZZ4L','data']
#print c

ngroup = groups
ngroup.insert(4,'All bkg')

for cat in cats[1:] :
    cc=c[cat] 
    cc.to_latex()
    cc.columns=[i for i in groups[1:]]
    cc.index=[i for i in cutlist]

    with open('All_'+cat+'_'+args.selection+'_'+era+'yields.txt', 'w') as f:
	print >> f,'\\documentclass[10pt]{report}'
	print >> f,'\\usepackage{adjustbox}'
	print >> f,'\\begin{document}'
	print >> f,'\\begin{table}[htp]'
	print >> f,'\\caption{' + '{0:s} {1:s} {2:s}'.format(cat, args.selection, era) + '}'  
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
        
    s = open('All_'+cat+'_'+args.selection+'_'+era+'yields.txt').read()
    s = s.replace('\\bottomrule','')
    s = s.replace('\\midrule','')
    s = s.replace('\\toprule','')
    s = s.replace('\\\\','\\\\ \\hline')
    f = open('All_'+cat+'_'+args.selection+'_'+era+'yields.txt','w')
    f.write(s)
    f.close()
 
