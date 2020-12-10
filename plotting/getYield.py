import ROOT 
from ROOT import TH1F, TH1D, TFile

fin='testFile.root'

Fin = TFile(fin,'read')

procs=['lep_PTV_0_75', 'lep_PTV_75_150', 'lep_PTV_150_250_0J','lep_PTV_150_250_GE1J', 'lep_PTV_GT250']

cats=['eeet','eemt','eett','mmet','mmmt','mmtt']

h={}

for cat in cats :
    hall=0
    for proc in procs :
        h[proc]=Fin.Get('hZH_{0:s}_{1:s}_htt125'.format(cat,proc))
        #h[proc]=Fin.Get('hHWW_{0:s}_{1:s}_htt125'.format(cat,proc))
        hall+=h[proc].GetSum()
        print h[proc].GetSum(),

    print cat,  'sum:', hall
