__author__ = "Alexis Kalogeropoulos"
__description__ = "Simple script to make LaTex table from a given .root file - it needs 3 arguments 1:input file 2:channel (all is preferred) 3:scale to lumi (0, 1, True, False)"


import sys
from ROOT import TFile, TTree, TH1, TH1D, TCanvas, TLorentzVector
from array import *
import numpy as np
from decimal import *
getcontext().prec = 2

def column(matrix, i):
    return [row[i] for row in matrix]

cats = [ 'eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
cat=str(sys.argv[2])

xsec=0.01
lumi=37.8

inFile = TFile.Open(sys.argv[1])
inFile.cd()


hW = inFile.Get("hWeights")
inTree = inFile.Get("Events")

nentries = inTree.GetEntries()

channel=str(sys.argv[2])

header=sys.argv[1]

if '/' in header : header=header.split("/",1)[1]
if '.root' in header : header=header.split(".",1)[0]

scale=str(sys.argv[3])

ScaleToLumi=False

if scale=="1" or scale=="true" or scale=="True" : 
    ScaleToLumi = True
    header=header+'_'+str(lumi)+'invfb'

if ScaleToLumi : print "Events scaled to {0:.2f}/fb for xsec = {1:.2f} pb".format(float(lumi),float(xsec))


rows, cols = (8, 9) 
arr = [[0 for i in range(cols)] for j in range(rows)] 
cuts=[]
result=[]

product=1.
if ScaleToLumi : product = xsec*lumi*1000/hW.GetSumOfWeights()
        
#print 'The weight will be', product, xsec, lumi, hW.GetSumOfWeights()

if 'all' not in channel :
    hist="hCutFlow_"+cat
    h1 = inFile.Get(hist)


    for i in range(1,h1.GetNbinsX()) :
        print h1.GetXaxis().GetBinLabel(i), h1.GetBinContent(i)*product

else:


    
    count=0
    for cat in cats:
    
        hist="hCutFlow_"+cat
       
        htest = inFile.Get(hist)
        for i in range(1,htest.GetNbinsX()) : 
            arr[count][i-1] = '{0:.2f}'.format(htest.GetBinContent(i)*product)
            if cat == 'mmmt' : cuts.append(htest.GetXaxis().GetBinLabel(i))
        count+=1


cats.insert(0,'Cuts')

np.vstack([arr,cats])



with open(header+'_yields.txt', 'w') as f:


	print >> f,'  \\begin{table}[htdp]'
	print >> f,'  \caption{'+header+'}'
	print >> f,'  \\begin{center}'
	print >> f,'  \\begin{tabular}{l l l l l l l l l }  \hline'
	for i in cats : print >> f, '{} &'.format(i),
	print >> f, ''
        
	lines = [' & \t'.join([str(x[i]) if len(x) > i else ' ' for x in arr]) for i in range(len(max(arr)))]
	#lines = [' & \t'.join([str(x[i]) for x in arr]) for i in range(len(max(arr)))]
	for i in range(len(cuts)):
	    print >> f,'{} & {} \hline'.format(cuts[i], lines[i])



	print >> f,'  \\end{tabular}  \hline'
	print >> f,'  \\end{table}  \hline'


	#np.savetxt('text.txt',arr, delimiter=' & ', fmt='%.2f', newline=' \n')
	#y = np.loadtxt('text.txt')
	#print y

