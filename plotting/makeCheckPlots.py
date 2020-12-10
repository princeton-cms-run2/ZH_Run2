from ROOT import gSystem, gStyle, gROOT, kTRUE, gDirectory, gPad
from ROOT import TCanvas, TH1D, TH1F, THStack, TFile, TPad, TLegend, TLatex, TLine, TAttMarker, TMarker, TColor
from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure, kRed, kGreen
from math import sqrt
import os
import sys

# cat = 'eeet', 'eemt', 'eett', 'mmet', 'mmmt', or 'mmtt'
# if cat = 'et', 'mt', or 'tt' plot Z.ee and Z.mumu combined
# if cat = 'all', plot combined ee+mm for each tau pair combination 



gROOT.SetBatch(kTRUE) # prevent displaying canvases
gStyle.SetOptStat(0)

def changetext(text):
    text = text.replace('tauideff','#tau_{id}')
    text = text.replace('pizero','#pi^{0}')
    text = text.replace('pt','p_{T}')
    text = text.replace('_2016','')
    text = text.replace('_2017','')
    text = text.replace('_2018','')
    #text = text.replace('scale_t_','')
    text = text.replace('scale_','scl_')
    text = text.replace('eta','#eta')
    text = text.replace('lt',' < ')
    text = text.replace('gt',' > ')
    text = text.replace('prong','h^{#pm}')
    text = text.replace('Down',' #downarrow')
    text = text.replace('Up',' #uparrow')
    text = text.replace('NLOWEK','ewk')
    text = text.replace('Jet','')
    text = text.replace('Flavour','Fl')
    text = text.replace('Absolute','Abs')
    text = text.replace('Relative','Rl')
    text = text.replace('Sample','Sml')
    text = text.replace('jes','')



    return text


def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-e","--extraTag",default='pow_noL',type=str,help="pow_noL or pow_wL")
    parser.add_argument("-o","--overideSyst",default='',type=str,help="overide systematics list")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)
tag= str(args.extraTag)





histos = { # [nBins,xMin,xMax,units]

        "m_sv_new_FMjall":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "lep_FWDH_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_0_75_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_75_150_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_0J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_GE1J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_GT250_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
}





scaleSyst = ["Central"]
scaleSyst=[]

#scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1', 'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']

scale = ['scale_e']



for i, sys in enumerate(scale) :
    scaleSyst.append(sys+'Up')
    scaleSyst.append(sys+'Down')

jes=['jesAbsolute', 'jesAbsolute_{0:s}'.format(str(era)), 'jesBBEC1', 'jesBBEC1_{0:s}'.format(str(era)), 'jesEC2', 'jesEC2_{0:s}'.format(str(era)), 'jesFlavorQCD', 'jesHF', 'jesHF_{0:s}'.format(str(era)), 'jesRelativeBal', 'jesRelativeSample_{0:s}'.format(str(era)), 'jesHEMIssue', 'jesTotal', 'jer']

jesSyst=[]
for i, sys in enumerate(jes) :
    jesSyst.append(sys+'Up')
    jesSyst.append(sys+'Down')

otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered'] 
otherS=['PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40'] 
otherS=['tauideff_ptgt40'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')

sysall = scaleSyst + jesSyst + OtherSyst


ssyscats=['scaleSyst']
ssyscats=['scaleSyst', 'jesSyst', 'OtherSyst']

syscats=[OtherSyst]


ssyscats=['OtherSyst']
sysall =  OtherSyst

print '--------------->', len(sysall)

#sysall=['Central', 'tauideff_pt25to30Up', 'tauideff_pt30to35Down']
#sysall=['tauideff_pt25to30Up', 'tauideff_pt30to35Down', 'tauideff_pt35to40Up']

if str(args.overideSyst) != '' : sysall=[str(args.overideSyst)]



groups=['Signal']

colour={0:kBlue,2:kRed, 4:kGreen, 6:kMagenta, 8:kOrange, 10:kAzure, 12:kGreen+1, 1:kBlue,3:kRed, 5:kGreen, 7:kMagenta, 9:kOrange, 11:kAzure, 13:kGreen+1,}


groups = ['Other','ZZ','data', 'Reducible', 'ggZH_lep', 'ZH_lep', 'ZH_hww125', 'Triboson']



h={}

cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}
cats = [ 'eeet', 'eemt', 'eett', 'mmet', 'mmmt', 'mmtt']

#dirs=['llet','llmt','lltt','llem','all']
#dirs=['llet','llmt','lltt','llem', 'eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
dirs=['eeet', 'eemt', 'eett', 'mmet', 'mmmt', 'mmtt']

#dirs = [ 'mmet', 'mmmt', 'mmtt','eeet', 'eemt', 'eett']

tag='pow_noL'


H = 800
W = 1600
H_ref = 600
W_ref = 600

# references for T, B, L, R
T = 0.08*H_ref
B = 0.12*H_ref
L = 0.16*W_ref
R = 0.04*W_ref

#margins for inbetween the pads in a ratio plot
B_ratio = 0.1*H_ref
T_ratio = 0.03*H_ref

#margin required for lebal on bottom of raito plot
B_ratio_label = 0.3*H_ref




xR=0.1   #legend parameters
#xR=0.2    #legend parameters


cT={}
cP={}
cPr={}
groups=['data','ZH']
groups = ['ZZ','data', 'Reducible', 'ggZH_lep', 'ZH_lep_htt125', 'ZH_hww125', 'Triboson']
groups = ['data_obs', 'ZZ', 'ZH_hww125','ZH_htt125', 'ggZH_hww125', 'ggZH_htt125', 'Reducible', 'Triboson']
#groups = ['ZZ']


for group in groups : 
    cP[group]={}
    cPr[group]={}

    cT[group] = TCanvas('c_{0:s}'.format(group),'c',90,90,W,H)
    cT[group].SetFillColor(0)
    cT[group].SetBorderMode(0)
    cT[group].SetFrameFillStyle(0)
    cT[group].SetFrameBorderMode(0)

    cT[group].SetLeftMargin(L/W)
    cT[group].SetRightMargin(R/W)
    cT[group].SetTopMargin(T/H)
    cT[group].SetBottomMargin(B/H)

    cT[group].Divide(3,2) 

    for icat, cat in enumerate(cats) :
	cP[group][cat]={}
	cP[group][cat] = TPad('pad_{0:s}_{1:s}'.format(group,cat),"",0.0,0.25,1.0,1.0)
	cP[group][cat].SetLeftMargin(L/W)
	cP[group][cat].SetRightMargin(R/W)
	cP[group][cat].SetTopMargin(T/H)
        cP[group][cat].SetLogy()
	#cP[group][cat].SetBottomMargin(B/H)
	cT[group].cd(icat+1)
	cP[group][cat].Draw()

	cPr[group][cat]={}
	cPr[group][cat] = TPad('padr_{0:s}_{1:s}'.format(group,cat),"",0.0,0.0,1.0,0.23)
	cPr[group][cat].SetLeftMargin(L/W)
	cPr[group][cat].SetRightMargin(R/W)
	#cPr[group][cat].SetTopMargin(T/H)
	#cPr[group][cat].SetBottomMargin(B/H)
	cPr[group][cat].Draw()


inFileName='zh{0:s}_NoRedSub.root'.format(era)

fIn = TFile( inFileName, 'read' )


lg={}
for isys, sys  in enumerate(ssyscats) : 
    lg[sys] = TLegend(xR,0.7,xR+0.8,0.95)
    lg[sys].SetBorderSize(0)
    lg[sys].SetFillColor(0)
    lg[sys].SetFillStyle (0)
    lg[sys].SetTextSize(0.035)
    lg[sys].SetNColumns(4)


    #aprint sys

h={}
for group in groups : 
    h[group]={}
    for icat, cat in enumerate(cats) :
	h[group][cat]={}
	cT[group].cd(icat+1)
        #print group, cat
	h[group][cat] = fIn.Get('{0:s}/{1:s}'.format(str(cat),group))
	h[group][cat].SetLineColor(kBlack)
	h[group][cat].SetMarkerColor(kBlack)
        #if icat == 0 and group == groups[0] : 
        #    for isys, sys  in enumerate(sysall) :  lg[sys].AddEntry(h[group][cat],'Central','l')

	cT[group].SetTitle(group)

	h[group][cat].SetTitle(cat)
	h[group][cat].SetMaximum(h[group][cat].GetMaximum()*2)
        h[group][cat].SetFillColor(0)
	h[group][cat].SetStats(000000)
        h[group][cat].SetMarkerSize(0.25)
	h[group][cat].GetYaxis().SetTitle('systematic/Central')
	h[group][cat].GetYaxis().SetTitleOffset(0.75)
	h[group][cat].GetXaxis().SetTitleOffset(0.8)
	h[group][cat].GetXaxis().SetTitle('m_sv in ZpT bins')
        cP[group][cat].cd()
	h[group][cat].Draw('hist')
        #print 'nominal', h[group][cat].GetName(), cat, h[group][cat].GetSum()
	#hh2.Draw( "hist p")


h1={}
h2={}
#for isyscat, syscat  in enumerate(sysall) : 

    #h2[syscat]={}
    #OutFileName='zh{0:s}_{1:s}_plots.root'.format(era,str(ssyscats[isyscat]))
for isys, sys in enumerate(sysall) : 

    labelSys='scaleSyst'
    if sys in jesSyst : labelSys='jesSyst'
    if sys in OtherSyst : labelSys='OtherSyst'
    
    if 'Central' in sys : 
	sys=''
    else :  
	group = group+'_CMS_'+sys

    if sys in scale or 'tauid' in sys or 'scale_e' in sys or 'scale_m' in sys: 
	sys = sys.replace('Up','_{0:s}Up'.format(era))
	sys = sys.replace('Down','_{0:s}Down'.format(era))

    if 'PreFire' in sys : sys = sys.replace('PreFire', 'prefiring')
    if 'jes' in sys : sys = sys.replace('jes', 'Jet')
    if 'jer' in sys : sys = sys.replace('jer', 'JER_{0:s}'.format(era))

    h1[sys]={}
    fIn.cd()
    for group in groups : 
	h1[sys][group]={}

	for icat, cat in enumerate(cats) :
            histname= group+'_CMS_'+sys
            

	    h1[sys][group][cat]={}
	    h1[sys][group][cat]=fIn.Get('{0:s}/{1:s}'.format(str(dirs[icat]), histname))
	    cT[group].cd(icat+1)
	    cT[group].SetTitle(group)
	    sysl = changetext(sys)
	    if icat==0 and group ==groups[0] :lg[ labelSys   ].AddEntry(h1[sys][group][cat],sysl,'p')
	    

for isys, sys in enumerate(sysall) : 
    
    if 'Central' in sys : 
	sys=''
    else :  
	group = group+'_CMS_'+sys

    if sys in scale or 'tauid' in sys or 'scale_e' in sys or 'scale_m' in sys: 
	sys = sys.replace('Up','_{0:s}Up'.format(era))
	sys = sys.replace('Down','_{0:s}Down'.format(era))

    if 'PreFire' in sys : sys = sys.replace('PreFire', 'prefiring')
    if 'jes' in sys : sys = sys.replace('jes', 'Jet')
    if 'jer' in sys : sys = sys.replace('jer', 'JER_{0:s}'.format(era))

    if isys == 0 : 
	marker = 24
    fIn.cd()
    for group in groups : 
	for icat, cat in enumerate(cats) :
	    if  'PTV' not in h1[sys][group][cat].GetName() and 'FWD' not in h1[sys][group][cat].GetName() :

		h1[sys][group][cat].SetTitle(cat)
		h1[sys][group][cat].SetFillColor(0)
		h1[sys][group][cat].SetStats(000000)

		h1[sys][group][cat].SetLineColor(colour[isys])
		h1[sys][group][cat].SetFillColor(colour[isys])
		h1[sys][group][cat].SetLineStyle(1+isys)
		h1[sys][group][cat].SetMarkerColor(colour[isys])
		h1[sys][group][cat].SetMarkerStyle(marker+isys)
		h1[sys][group][cat].SetMarkerSize(0.3)

		cP[group][cat].cd()
		h1[sys][group][cat].Draw("hist same p")


for isys, sys in enumerate(sysall) : 
    
    if 'Central' in sys : 
	sys=''
    else :  
	group = group+'_CMS_'+sys

    if sys in scale or 'tauid' in sys or 'scale_e' in sys or 'scale_m' in sys: 
	sys = sys.replace('Up','_{0:s}Up'.format(era))
	sys = sys.replace('Down','_{0:s}Down'.format(era))

    if 'PreFire' in sys : sys = sys.replace('PreFire', 'prefiring')
    if 'jes' in sys : sys = sys.replace('jes', 'Jet')
    if 'jer' in sys : sys = sys.replace('jer', 'JER_{0:s}'.format(era))

    if isys == 0 : 
	marker = 24
    fIn.cd()
    for group in groups : 
	for icat, cat in enumerate(cats) :
	    if  'PTV' not in h1[sys][group][cat].GetName() and 'FWD' not in h1[sys][group][cat].GetName() :

                h2r=h1[sys][group][cat].Clone()
                h2r.Divide(h[group][cat])

		cPr[group][cat].cd()
                
		if isys ==0 : 
		    h2r.SetTitle("")
		    h2r.GetYaxis().SetTitle("Ratio")
		    h2r.GetYaxis().SetNdivisions(4)
		    h2r.GetYaxis().SetTitleSize(0.01)
		    h2r.GetYaxis().SetLabelSize(0.15)
		    h2r.GetYaxis().SetTitleOffset(0.75)
		    h2r.GetYaxis().SetRangeUser(0.95,1.05)
		    #h2r.GetYaxis().SetRangeUser(0.5,1.5)
                    #h2r.Divide(h[group][cat])
		    h2r.Draw("hist  p")
		    #h1[sys][group][cat].Draw("hist  p")
                    #h[group][cat].Draw("hist same")

                else : 
		    #h1[sys][group][cat].Draw("hist  same p")
                    #h[group][cat].Draw("hist same")
		    h2r.Draw("hist  same p")

		cPr[group][cat].Update()


for group in groups:
    cT[group].cd(1)
    lg[labelSys].Draw()   

    cT[group].SaveAs('{0:s}_{1:s}_{2:s}_sanity.pdf'.format(group,era,labelSys))

    command='cp {0:s}_{1:s}_*sanity.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/'.format(group,era)
    os.system(command)  


