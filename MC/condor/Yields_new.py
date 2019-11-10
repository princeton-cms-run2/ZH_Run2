__author__ = "Alexis Kalogeropoulos"
__description__ = "Simple script to make LaTex table from a given .root file - it needs 3 arguments 1:input file 2:channel (all is preferred) 3:scale to lumi (0, 1, True, False)"


import sys
from ROOT import TFile, TTree, TH1, TH1D, TCanvas, TLorentzVector
from array import *
import numpy as np
from decimal import *
getcontext().prec = 2
import csv


def column(matrix, i):
    return [row[i] for row in matrix]


def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFile",default='MCsamples_2016.csv',help="Input file name.")
    parser.add_argument("-y","--year",default=2016,type=str,help="Data taking period, 2016, 2017 or 2018")
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
groups = ['Signal','Reducible','Rare','ZZ4L','data']

for group in groups :
    nickNames[group] = []


#for line in open('./MCsamples_'+era+'_small.csv','r').readlines() :
for line in open('./MCsamples_'+era+'.csv','r').readlines() :
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
'''
# now add the data
#for eras in ['2017B','2017C','2017D','2017E','2017F'] :
for eras in ['2016'] :
    #for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
    #for dataset in ['SingleElectron','SingleMuon','DoubleEG','DoubleMuon'] :
    for dataset in ['SingleMuon'] :
        nickName = '{0:s}_Run{1:s}'.format(dataset,eras)
        totalWeight[nickName] = 1.
        sampleWeight[nickName] = 1.
        nickNames['data'].append(nickName)
#####################################3
'''


channel=args.category

for group in groups :
    for nickName in nickNames[group]:
        fIn = '{0:s}/{1:s}_{2:s}/{1:s}_{2:s}.root'.format(args.selection, nickName, era)
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

        if ScaleToLumi : print "Events scaled to {0:.2f}/fb for xsec = {1:.2f} pb".format(float(lumi[era]/1000),float(xsec[nickName]))


        rows, cols = (8, 9) 
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
	            #arr[count][i-1] = 1
	            if cat == 'mmmt' : cuts.append(htest.GetXaxis().GetBinLabel(i))
	        count+=1



     
        np.vstack([arr,cats])
        t_matrix = zip(*arr) 
        with open(nickName+'_'+group+'_'+era+"new_file.csv","w+") as my_csv:
            fieldnames = cats[1:]
            csvWriter = csv.DictWriter(my_csv, fieldnames=fieldnames)
            #x=np.array(cuts)
            #y=np.array(arr)
            #print cuts, len(cuts)
            #print y, len(y)
            #np.hstack((x,y))
            #np.append(x, y, axis=1)
            #fieldnames = cuts
            #csvWriter = csv.DictWriter(my_csv, fieldnames=fieldnames)
            csvWriter.writeheader()

            csvWriter = csv.writer(my_csv,delimiter=',')
            csvWriter.writerows(t_matrix)
            #csvWriter.writerows(x)

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
	    print >> f,'\\documentclass[10pt]{report}'
	    print >> f,'\\begin{document}'
	    print >> f,'\\begin{table}[htp]'
	    hh = nickName.replace('_','\\_')
	    
	    print >> f,'\\caption{' + '{0:s}'.format(hh) + '}'  
	    print >> f,'\\begin{center}'
	    print >> f,'\\begin{tabular}{l r r r r r r r r }  \hline'
	    line = cats[0]
	    for i in cats[1:] : line += ' & {}'.format(i) 
	    line += '\\'
	    line += '\\ \hline' 
	    print >> f,line
	    lines = []
	    for x in arr :
                line = []
                for i in range(len(x)) :
		    v = float(x[i])
		    if v > 99. :
                        line.append("{0:.0f} ".format(v))
		    else :
		        line.append("{0:.2f} ".format(v)) 
                lines.append(line)

	    for i in range(len(cuts)):
	        if len(cuts[i]) < 1 : continue 
	        line = cuts[i]
	        for j in range(8) : line += " & {0:s}".format(lines[i][j])
	        line += '\\\\ \\hline'
	        print >> f,line

	    print >> f,'\\end{tabular}'
	    print >> f,'\\end{center}'
	    print >> f,'\\end{table}'
	    print >> f,'\\end{document}'
 
        '''
		#np.savetxt('text.txt',arr, delimiter=' & ', fmt='%.2f', newline=' \n')
		#y = np.loadtxt('text.txt')
		#print y
