import tdrstyle
import CMS_lumi
from ROOT import gSystem, gStyle, gROOT, kTRUE, gDirectory, gPad
from ROOT import TCanvas, TH1D, TH1F, THStack, TFile, TPad, TLegend, TLatex, TLine, TAttMarker, TMarker, TColor, TGraphErrors
from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure, kRed, kGreen, kCyan, TPie, kGray, kTeal, kYellow
from math import sqrt
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import array
import plotting
import os
import gc
from array import array

# cat = 'eeet', 'eemt', 'eett', 'mmet', 'mmmt', or 'mmtt'
# if cat = 'et', 'mt', or 'tt' plot Z.ee and Z.mumu combined
# if cat = 'all', plot combined ee+mm for each tau pair combination 

gROOT.SetBatch(kTRUE) # prevent displaying canvases



def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFile",default='./allGroups_2017_OS_LT00.root',help="File to be analyzed.")
    #parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    #parser.add_argument("-l","--LTcut",default=0.,type=float,help="H_LTcut")
    #parser.add_argument("-s","--sign",default='OS',help="Opposite or same sign (OS or SS).")
    parser.add_argument("-c","--cat",default='all',help="Category")
    parser.add_argument("-L","--setlog",default='yes',help="Set log scale")
    parser.add_argument("-u","--unBlind",default='yes',help="Unblind data")
    parser.add_argument("-w","--workingPoint",default=16, type=int,help="Unblind data")
    parser.add_argument("-b","--bruteworkingPoint",default=16, type=int,help="Unblind data")
    parser.add_argument("-j", "--inSystematics",type=str, default='',help='systematic variation - choose from nom, jesTotalUp, jesTotalDown, jerUp, jerDown')
    
    return parser.parse_args()


def CreateTransparentColor(color, alpha) :
    adapt = gROOT.GetColor(color);
    new_idx = gROOT.GetListOfColors().GetSize() + 1;
    trans = TColor(new_idx, adapt.GetRed(), adapt.GetGreen(), adapt.GetBlue(), "", alpha);
    trans.SetName("userColor%i".format(new_idx))
    return new_idx



def makePie( sizes, labels, cat, colours,savename):
    print sizes, labels, cat, colours, savename
    #colorsA = array('i', colours)
    c1 = TCanvas('c1_{0:s}'.format(cat),'c1_{0:s}'.format(cat),90,90,800,800)
    vals = array ('d', sizes)
    cols = array ('i', colours)
    pie = TPie("pie", cat, len(sizes), vals, cols)
    total=sum(vals)
    for i, il in enumerate(labels) :

    	#pie.SetEntryLabel(i, "#splitline{"+il+"}{%val (%perc)}")
    	#pie.SetEntryLabel(i, "#splitline{"+il+"}{ (%perc)}")
    	#pie.SetEntryLabel(i, il+"(%perc)")
    	pie.SetEntryLabel(i, il+"{0:10.3f}%".format(sizes[i]/total))
        pie.SetEntryLineColor(i,kBlack)

    c1.cd()
    pie.SetTextSize(0.025)
    pie.SetLabelsOffset(.015)
    lTex2a = TLatex()
    tt1 = TLatex() 
    tt1.SetNDC() 
    pie.SetRadius(0.3)
    pie.SetName(cat)
    #pie.Draw("")
    #pieleg.SetY1(.56) 
    #pieleg.SetY2(.86);
    pie.SortSlices(1,0.)
    pie.Draw("3d")
    lTex2a.DrawLatexNDC(0.4, 0.9, cat)
    pie.MakeLegend(0.7,0.95,0.95,0.7)
    c1.SaveAs("./plots/"+savename+'_pie_'+cat+".png")
    del pie
    del lTex2a
    del c1



def makePiee( sizes, labels, cat, colours,savename):
    #print sizess, sizes, labels, colors, cat


    # Pie chart
    #add colors
    #colors =['#ffcc66','#58d885','#d88558', '#99ccff']
    #ngroup=['Other', 'Top', 'DY' ,'WZ', 'ZZ']
    #groups = ['bfl', 'ljfl', 'cfl','jfl','jft1', 'jft2','Other','Top','DY','WZ','ZZ']
    
    #fig1, ax1 = plt.subplots(figsize=(2, 4), subplot_kw=dict(aspect="equal"))
    fig1, ax1 = plt.subplots()
    explode=()
    #patches, texts, autotexts = ax1.pie(sizes, colors = colours, lab els=labels, radius=0.8, autopct='%1.1f%%', startangle=90, textprops={'fontsize' : 15})
    ax1.pie(sizes, colors = colours, labels=labels, radius=0.8, autopct='%1.1f%%', startangle=90, textprops={'fontsize' : 15})
    #ax1.pie(sizes, labels=labels, autopct='%1.1f%%',  shadow=True, startangle=90)
    '''
    for text in texts:
	text.set_color('black')
    for autotext in autotexts:
	autotext.set_color('white')
    '''
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')  
    #plt.tight_layout()
    #plt.show() 
    #fig = plt.gcf()
    #fig1.set_size_inches(6,6)
    #ax = fig1.set_axes((0.,0.,0,0))
    #ax1.set_title(cat)
    #plt.title(cat, bbox={'facecolor':'0.8', 'pad':5})
    ##props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ##ax1.text(0.75, 0.95, cat, transform=ax1.transAxes, fontsize=16,
    ##    verticalalignment='top', bbox=props)
    #plt.savefig('./plots/'+savename+'_pie_'+cat+'.png')  
    plt.savefig('./plots/'+savename+'_pie_'+cat+'.png')  
    #del fig1,ax1
    print 'done with pie....'



def applyStyle( h, fill, line, fillStyle) :
    h.SetFillColor(fill)
    h.SetLineColor(line)
    h.SetFillStyle(fillStyle)
    h.SetLineWidth(2)

def applySignalStyle(h) :
    h.SetLineWidth(3)
    h.SetFillColor(0)
    h.SetLineColor(kRed+1)
    h.SetLineStyle(2)
    h.SetMarkerSize(1.5);
    h.SetMarkerColor(kRed+1);



def applyDATAStyle(h) :
    #print("In applyDATAStyle: h={0:s} type(h)={1:s}".format(str(h),type(h)))
    h.SetMarkerStyle(20)
    h.SetMarkerSize(1.0)
    h.SetLineWidth(2)
    h.SetLineColor(kBlack)

def convertToDNDM( histo) :
    for i in range(1,histo.GetNbinsX(),1) :
	histo.SetBinContent(i,histo.GetBinContent(i)/histo.GetXaxis().GetBinWidth(i))
	histo.SetBinError(i,histo.GetBinError(i)/histo.GetXaxis().GetBinWidth(i))




#groups = ['Signal','fakes', 'f1', 'f2','bfl', 'ljfl',  'cfl','jfl','jft1', 'jft2','Other','Top','DY','WZ','ZZ','data']
#groups = ['Signal','Other','Top','DY','WZ','ZZ','data']
groups = ['Signal','bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1','f2',  'Other','Top','DY','WZ','ZZ', 'ZZ2L2Nu', 'ZZ2L2Q','ZZ2Q2Nu','data']
groups = ['Signal','bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1','f2', 'Other','Top','DY','WZ','ZZ','data']
groupss = ['Signal','Other','Top','DY','WZ','ZZ','data']

groupsZZincl = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1','f2',  'Signal','Other','Top','DY','WZ', 'ZZincl','data']
groupsZZ4L = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1','f2', 'Signal','Other','Top','DY','WZ','ZZ4L','data']
#groups = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','data','Signal']
fakegroup = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2']


#fgroups = ['bfl', 'ljfl',  'cfl','jfl','jft1', 'jft2']
#ngroups = ['fakes','f1', 'f2','Signal','Other','Top','DY','WZ','ZZ','data']

kTop = TColor.GetColor("#ffcc66")
kTop = TColor.GetColor("#ff8066")
kDY = TColor.GetColor("#58d885")
kWZ = TColor.GetColor('#d88558')
kVVV = TColor.GetColor('#3e80db')
colors = {'bfl':kCyan, 'ljfl':kRed+1,  'cfl':kCyan+2,'jfl':kGreen-3 ,  'data':0,'fakes':kMagenta-10,'f1':kMagenta-7, 'f2':kMagenta-5, 'WJets':kMagenta-10,'Other':kOrange,'ZZ':kAzure-9,'Top':kTop,'DY':kDY,'Signal':kRed+1, 'ZZ4L':kAzure-8, 'Topp':kTop, 'WZincl':kBlue-8, 'WZ':kWZ, 'WWincl':kBlue-8, 'WW':kRed-8, 'VVV':kVVV, 'TTX':kTop, 'jft1':41, 'jft2':38, 'bfl1':7, 'ljfl1':8,  'cfl1':29,'jfl1':50, 'bfl2':93, 'ljfl2':9,  'cfl2':226,'jfl2':207}

kfake = TColor.GetColor('#c34bb2')
kf1 = TColor.GetColor('#d886c9')
kf2 = TColor.GetColor('#a4c5b4')
colors = {'bfl':kCyan, 'ljfl':kRed+1,  'cfl':kCyan+2,'jfl':kGreen-3 ,  'data':0, 'fakes':kfake,'f1':kf1, 'f2':kf2, 'WJets':kMagenta-10,'Other':kOrange,'ZZ':kAzure-9,'Top':kTop,'DY':kDY,'Signal':kRed+1, 'ZZ4L':kAzure-8, 'Topp':kTop, 'WZincl':kBlue-8, 'WZ':kWZ, 'WWincl':kBlue-8, 'WW':kRed-8, 'VVV':kVVV, 'TTX':kTop, 'jft1':41, 'jft2':38, 'bfl1':7, 'ljfl1':8,  'cfl1':29,'jfl1':50, 'bfl2':93, 'ljfl2':9,  'cfl2':226,'jfl2':207}


'''
for i,f in enumerate(fgroups) :
    for g in groupss :
        #groups.insert(0,g+'_'+f)
        #ngroups.insert(0,g+'_'+f)
        #colors.insert(0, g+'_'+f:colors[g]+i)
        #print '----', colors[g], i
        colors[g+'_'+f] = (colors[g]+i)

print colors
'''
hW = {}
hsW={}
#for group in groups : 
plotSettings={}
plotSettings = { # [nBins,xMin,xMax,units]
        #"w_fm_new":[3,0.5,3.5,"","w1,w2,w0"],
        "m_sv":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"mt_sv":[10,0,200,"[Gev]","mT(#tau#tau)(SV)"],
        #"mt_sv_FM":[10,0,200,"[Gev]","mT(#tau#tau)(SV)"],
        "m_sv_FM":[10,0,200,"[Gev]","m(#tau#tau)FM(SV)"],
        "m_sv_new":[10,0,200,"[Gev]","m(#tau#tau_new)(SV)"],
        "m_sv_new_FM":[10,0,200,"[Gev]","m(#tau#tau_new_FM)(SV)"],
        "mt_sv_new_FM":[10,0,200,"[Gev]","mT(#tau#tau_new_FM)(SV)"],

        "mll":[40,50,130,"[Gev]","m(l^{+}l^{-})"],
        #"H_LT_FM":[10,0,200,"[Gev]","H_LT_FM(#tau#tau)"],
        "H_LT":[10,0,200,"[Gev]","H_LT(#tau#tau FM)"],

        #"cat":[10,-0.5,9.5,"","cat"], 
        "met":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        "met_FM":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        #"pt_1":[40,0,200,"[Gev]","P_{T}(#tau_{1})"],
        "pt_3":[40,0,200,"[Gev]","P_{T}(#tau_{3})"],
        "pt_4":[40,0,200,"[Gev]","P_{T}(#tau_{4})"],
        #"CutFlow":[15,0.5,15.5,"","Cutflow"],
        #"CutFlowFM":[15,0.5,15.5,"","Cutflow"],
        "gen_match_3":[30,-0.5,29.5,"","gen_match_3"],
        "gen_match_4":[30,-0.5,29.5,"","gen_match_4"],
        "gen_match_3_FM":[30,-0.5,29.5,"","gen_match_3"],
        "gen_match_4_FM":[30,-0.5,29.5,"","gen_match_4"],
        "iso_1":[20,0,1,"","relIso(l_{1})"],
        "iso_2":[20,0,1,"","relIso(l_{2})"],
	"iso_3":[20,0,1,"","relIso(l_{3})"],
        "iso_4":[20,0,1,"","relIso(l_{4})"],
        "dZ_3":[10,0,0.2,"[cm]","d_{z}(l_{3})"],
        "dZ_4":[10,0,0.2,"[cm]","d_{z}(l_{4})"],
        "d0_3":[10,0,0.2,"[cm]","d_{xy}(l_{3})"],
        #"tightId_3":[3,-1.5,1.5,"","tightId_3"],
        #"tightId_4":[3,-1.5,1.5,"","tightId_4"],
        #"d0_4":[10,0,0.2,"[cm]","d_{xy}(l_{4})"]
        "njets":[10,-0.5,9.5,"","nJets"],
        "jpt_1":[10,0,200,"[GeV]","Jet^{1} P_{T}"], 
        "nbtag":[5,-0.5,4.5,"","nBTag"]

}


varSystematics= ['nom', 'JER', 'JESUp', 'JESDown', 'JERUp', 'JERDown', 'UnclUp', 'UnclDown']
varSystematics= ['JESUp', 'JESDown', 'JERUp', 'JERDown', 'UnclUp', 'UnclDown']
'''
for iv in varSystematics : 
            hName = 'm_sv_new_{2:s}'.format(str(syst))
            plotSettings[hName] = [10,0,200,"[Gev]","m(#tau#tau_new)(SV)_"+iv]
            hName = 'm_sv_new_FM_{2:s}'.format(str(syst))
            plotSettings[hName] = [10,0,200,"[Gev]","m(#tau#tau_new)(SV)_FM_"+iv]
            hName = 'mt_sv_new_{2:s}'.format(str(syst))
            plotSettings[hName] = [10,0,200,"[Gev]","mt(#tau#tau_new)(SV)_"+iv]
            hName = 'mt_sv_new_FM_{2:s}'.format(str(syst))
            plotSettings[hName] = [10,0,200,"[Gev]","mt(#tau#tau_new)(SV)_FM"+iv]
'''

plotSettingss= { # [nBins,xMin,xMax,units]
        "m_sv":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "mt_sv":[10,0,200,"[Gev]","m_{T}(#tau#tau)(SV)"],
        "met":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        "njets":[10,-0.5,9.5,"","nJets"],
        "mll":[40,50,130,"[Gev]","m(l^{+}l^{-})"],
        "mll2":[40,50,130,"[Gev]","m(l^{+}l^{-})"],
        #"mllall":[40,50,130,"[Gev]","m(l^{+}l^{-})"],
        "m_vis":[30,50,200,"[Gev]","m(#tau#tau)"],
        "pt_tt":[40,0,200,"[GeV]","P_{T}(#tau#tau)"],
        "H_LT":[30,50,200,"[Gev]","H_{LT}(#tau#tau)"],

        "pt_1":[40,0,200,"[Gev]","P_{T}(#tau_{1})"],
        "eta_1":[60,-3,3,"","#eta(l_{1})"],
        "phi_1":[60,-3,3,"","#phi(l_{1})"],
        "iso_1":[20,0,1,"","relIso(l_{1})"],
        "dZ_1":[10,0,0.2,"[cm]","d_{z}(l_{1})"],
        "d0_1":[10,0,0.2,"[cm]","d_{xy}(l_{1})"],
        "q_1":[10,-5,5,"","charge(l_{1})"],

        "pt_2":[40,0,200,"[Gev]","P_{T}(l_{2})"],
        "eta_2":[60,-3,3,"","#eta(l_{2})"],
        "phi_2":[60,-3,3,"","#phi(l_{2})"],
        "iso_2":[20,0,1,"","relIso(l_{2})"],
        "dZ_2":[10,0,0.2,"[cm]","d_{z}(l_{2})"],
        "d0_2":[10,0,0.2,"[cm]","d_{xy}(l_{2})"],
        "q_2":[10,-5,5,"","charge(l_{2})"],

	"iso_3":[20,0,1,"","relIso(l_{3})"],
        "pt_3":[40,0,200,"[Gev]","P_{T}(l_{3})"],
        "eta_3":[60,-3,3,"","#eta(l_{3})"],
        "phi_3":[60,-3,3,"","#phi(l_{3})"],
        "dZ_3":[10,0,0.2,"[cm]","d_{z}(l_{3})"],
        "d0_3":[10,0,0.2,"[cm]","d_{xy}(l_{3})"],

        "iso_4":[20,0,1,"","relIso(l_{4})"],
        "pt_4":[40,0,200,"[Gev]","P_{T}(l_{4})"],
        "eta_4":[60,-3,3,"","#eta(l_{4})"],
        "phi_4":[60,-3,3,"","#phi(l_{4})"],
        "dZ_4":[10,0,0.2,"[cm]","d_{z}(l_{4})"],
        "d0_4":[10,0,0.2,"[cm]","d_{xy}(l_{4})"],

        "H_LT_FM":[30,50,200,"[Gev]","H_{LT}(#tau#tau)"],

        
        "m_sv_FM":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "mt_sv_FM":[10,0,200,"[Gev]","m_{T}(#tau#tau)(SV)"],
        "met_FM":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        "njets_FM":[10,-0.5,9.5,"","nJets"],
        "mll_FM":[40,50,130,"[Gev]","m(l^{+}l^{-})"],
        "m_vis_FM":[30,50,200,"[Gev]","m(#tau#tau)"],
        "pt_tt_FM":[40,0,200,"[GeV]","P_{T}(#tau#tau)"],

        "weight":[20,-10,10,"","PUWeight"],
        "weightPUtrue":[20,-10,10,"","PUtrue"],
        "weightPU":[20,-10,10,"","PU"],
        "nPV":[40,-0.5,39.5,"","nPV"],
        "nPU":[130,-0.5,129.5,"","nPU"],
        "nPUtrue":[130,-0.5,129.5,"","nPUtrue"],
        "Generator_weight":[2000,1000,1000,"","genWeight"],
        "gen_match_1":[30,-0.5,29.5,"","gen_match_1"],
        "gen_match_2":[30,-0.5,29.5,"","gen_match_2"],
        "gen_match_3":[30,-0.5,29.5,"","gen_match_3"],
        "gen_match_4":[30,-0.5,29.5,"","gen_match_4"],

        "dPhi_l1H":[20,-4,4,"#Delta#Phi(l1,H)",""],
        "dPhi_l2H":[20,-4,4,"#Delta#Phi(l2,H)",""],
        "dPhi_lH":[20,-4,4,"#Delta#Phi(l,H)",""],

        "dEta_l1H":[20,-4,4,"#Delta#eta(l1,H)",""],
        "dEta_l2H":[20,-4,4,"#Delta#eta(l2,H)",""],
        "dEta_lH":[20,-4,4,"#Delta#eta(l,H)",""],

        "dR_l1H":[20,-4,4,"#Delta#R(l1,H)",""],
        "dR_l2H":[20,-4,4,"#Delta#R(l2,H)",""],
        "dR_lH":[20,-4,4,"#Delta#R(l,H)",""],

        "inTimeMuon_1":[10,-5,5,"","inTimeMuon_1"],
        "isGlobal_1":[10,-5,5,"","isGlobal_1"],
        "isTracker_1":[10,-5,5,"","isTracker_1"],
        "looseId_1":[10,-5,5,"","looseId_1"],
        "mediumId_1":[10,-5,5,"","mediumId_1"],
        "Electron_mvaFall17V2noIso_WP90_1":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_1"],


        "inTimeMuon_2":[10,-5,5,"","inTimeMuon_2"],
        "isGlobal_2":[10,-5,5,"","isGlobal_2"],
        "isTracker_2":[10,-5,5,"","isTracker_2"],
        "looseId_2":[10,-5,5,"","looseId_2"],
        "mediumId_2":[10,-5,5,"","mediumId_2"],
        "Electron_mvaFall17V2noIso_WP90_2":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_2"],



        "inTimeMuon_3":[10,-5,5,"","inTimeMuon_3"],
        "isGlobal_3":[10,-5,5,"","isGlobal_3"],
        "isTracker_3":[10,-5,5,"","isTracker_3"],
        "looseId_3":[10,-5,5,"","looseId_3"],
        "mediumId_3":[10,-5,5,"","mediumId_3"],
        "Electron_mvaFall17V2noIso_WP90_3":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_3"],



        "inTimeMuon_4":[10,-5,5,"","inTimeMuon_4"],
        "isGlobal_4":[10,-5,5,"","isGlobal_4"],
        "isTracker_4":[10,-5,5,"","isTracker_4"],
        "looseId_4":[10,-5,5,"","looseId_4"],
        "mediumId_4":[10,-5,5,"","mediumId_4"],
        "Electron_mvaFall17V2noIso_WP90_4":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_4"],

        "Z_Pt":[10,0,200,"[Gev]","P_T(l_{1}l_{2})"],
        "Z_DR":[60,0,6,"","#Delta R(l_{1}l_{2})"],

}


plotSettingss = { # [nBins,xMin,xMax,units]
        "m_sv":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "met":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        "njets":[10,-0.5,9.5,"","nJets"],

        "weight":[20,-10,10,"","PUWeight"],
        "weightPUtrue":[20,-10,10,"","PUtrue"],
        "weightPU":[20,-10,10,"","PU"],
        "nPV":[40,-0.5,39.5,"","nPV"],
        "nPU":[130,-0.5,129.5,"","nPU"],
        "nPUtrue":[130,-0.5,129.5,"","nPUtrue"],
        "Generator_weight":[2000,1000,1000,"","genWeight"],
        "pt_1":[40,0,200,"[Gev]","P_{T}(#tau_{1})"],
        "eta_1":[60,-3,3,"","#eta(l_{1})"],
        "phi_1":[60,-3,3,"","#phi(l_{1})"],
        "iso_1":[20,0,1,"","relIso(l_{1})"],
        "dZ_1":[10,0,0.2,"[cm]","d_{z}(l_{1})"],
        "d0_1":[10,0,0.2,"[cm]","d_{xy}(l_{1})"],
        "q_1":[10,-5,5,"","charge(l_{1})"],

        "pt_2":[40,0,200,"[Gev]","P_{T}(l_{2})"],
        "eta_2":[60,-3,3,"","#eta(l_{2})"],
        "phi_2":[60,-3,3,"","#phi(l_{2})"],
        "iso_2":[20,0,1,"","relIso(l_{2})"],
        "dZ_2":[10,0,0.2,"[cm]","d_{z}(l_{2})"],
        "d0_2":[10,0,0.2,"[cm]","d_{xy}(l_{2})"],
        "q_2":[10,-5,5,"","charge(l_{2})"],

	"iso_3":[20,0,1,"","relIso(l_{3})"],
        "pt_3":[40,0,200,"[Gev]","P_{T}(l_{3})"],
        "eta_3":[60,-3,3,"","#eta(l_{3})"],
        "phi_3":[60,-3,3,"","#phi(l_{3})"],
        "dZ_3":[10,0,0.2,"[cm]","d_{z}(l_{3})"],
        "d0_3":[10,0,0.2,"[cm]","d_{xy}(l_{3})"],

        "iso_4":[20,0,1,"","relIso(l_{4})"],
        "pt_4":[40,0,200,"[Gev]","P_{T}(l_{4})"],
        "eta_4":[60,-3,3,"","#eta(l_{4})"],
        "phi_4":[60,-3,3,"","#phi(l_{4})"],
        "dZ_4":[10,0,0.2,"[cm]","d_{z}(l_{4})"],
        "d0_4":[10,0,0.2,"[cm]","d_{xy}(l_{4})"],


        #"Jet_pt":[100,0,500,"[GeV]","Jet P_{T}"], 
        #"Jet_eta":[60,-3,3,"","Jet #eta"],
        #"Jet_phi":[60,-3,3,"","Jet #phi"],
        #"Jet_ht":[100,0,800,"[GeV]","H_{T}"],

        "jpt_1":[10,0,200,"[GeV]","Jet^{1} P_{T}"], 
        "jeta_1":[60,-3,3,"","Jet^{1} #eta"],
        "jpt_2":[10,0,200,"[GeV]","Jet^{2} P_{T}"], 
        "jeta_2":[6,-3,3,"","Jet^{2} #eta"],

        "bpt_1":[40,0,200,"[GeV]","BJet^{1} P_{T}"], 
        "bpt_2":[40,0,200,"[GeV]","BJet^{2} P_{T}"], 

        "nbtag":[5,-0.5,4.5,"","nBTag"],
        #"nbtagLoose":[10,0,10,"","nBTag Loose"],
        #"nbtagTight":[5,0,5,"","nBTag Tight"],
        "beta_1":[60,-3,3,"","BJet^{1} #eta"],
        "beta_2":[60,-3,3,"","BJet^{2} #eta"],

        "met_phi":[60,-3,3,"","#it{p}_{T}^{miss} #phi"], 
        "puppi_phi":[60,-3,3,"","PUPPI#it{p}_{T}^{miss} #phi"], 
        "puppimet":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        #"mt_tot":[100,0,1000,"[GeV]"], # sqrt(mt1^2 + mt2^2)
        #"mt_sum":[100,0,1000,"[GeV]"], # mt1 + mt2

        "mll":[40,50,130,"[Gev]","m(l^{+}l^{-})"],

        "m_vis":[30,50,200,"[Gev]","m(#tau#tau)"],
        "pt_tt":[40,0,200,"[GeV]","P_{T}(#tau#tau)"],
        "H_DR":[60,0,6,"","#Delta R(#tau#tau)"],
        "H_tot":[30,0,200,"[GeV]","m_{T}tot(#tau#tau)"],


        "m_sv_new":[10,0,200,"[Gev]","m(#tau#tau)(newSV)"],
        "mt_sv":[10,0,200,"[Gev]","m_{T}(#tau#tau)(SV)"],
        "AMass":[100,50,550,"[Gev]","m_{Z+H}(SV)"],

        "Z_Pt":[10,0,200,"[Gev]","P_T(l_{1}l_{2})"],
        "Z_DR":[60,0,6,"","#Delta R(l_{1}l_{2})"],

        "DeepTauiD_VSjet_3":[256,-0.5,255.5,"","DeepVSjet_3"],
        "DeepTauiD_VSjet_4":[256,-0.5,255.5,"","DeepVSjet_4"],
        "DeepTauiD_VSe_3":[256,-0.5,255.5,"","DeepVSe_3"],
        "DeepTauiD_VSe_4":[256,-0.5,255.5,"","DeepVSe_4"],
        "DeepTauiD_VSmu_3":[256,-0.5,255.5,"","DeepVSmu_3"],
        "DeepTauiD_VSmu_4":[256,-0.5,255.5,"","DeepVSmu_4"],
        "TriggerW":[10,0,200,"","TriggerW"],
        "LeptonW":[10,0,200,"","TriggerW"],

        "inTimeMuon_1":[10,-5,5,"","inTimeMuon_1"],
        "isGlobal_1":[10,-5,5,"","isGlobal_1"],
        "isTracker_1":[10,-5,5,"","isTracker_1"],
        "looseId_1":[10,-5,5,"","looseId_1"],
        "mediumId_1":[10,-5,5,"","mediumId_1"],
        "Electron_mvaFall17V2noIso_WP90_1":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_1"],
        "gen_match_1":[30,-0.5,29.5,"","gen_match_1"],


        "inTimeMuon_2":[10,-5,5,"","inTimeMuon_2"],
        "isGlobal_2":[10,-5,5,"","isGlobal_2"],
        "isTracker_2":[10,-5,5,"","isTracker_2"],
        "looseId_2":[10,-5,5,"","looseId_2"],
        "mediumId_2":[10,-5,5,"","mediumId_2"],
        "Electron_mvaFall17V2noIso_WP90_2":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_2"],
        "gen_match_2":[30,-0.5,29.5,"","gen_match_2"],



        "inTimeMuon_3":[10,-5,5,"","inTimeMuon_3"],
        "isGlobal_3":[10,-5,5,"","isGlobal_3"],
        "isTracker_3":[10,-5,5,"","isTracker_3"],
        "looseId_3":[10,-5,5,"","looseId_3"],
        "mediumId_3":[10,-5,5,"","mediumId_3"],
        "Electron_mvaFall17V2noIso_WP90_3":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_3"],
        "gen_match_3":[30,-0.5,29.5,"","gen_match_3"],



        "inTimeMuon_4":[10,-5,5,"","inTimeMuon_4"],
        "isGlobal_4":[10,-5,5,"","isGlobal_4"],
        "isTracker_4":[10,-5,5,"","isTracker_4"],
        "looseId_4":[10,-5,5,"","looseId_4"],
        "mediumId_4":[10,-5,5,"","mediumId_4"],
        "Electron_mvaFall17V2noIso_WP90_4":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_4"],
        "gen_match_4":[30,-0.5,29.5,"","gen_match_4"],

        "pt_1_FM":[40,0,200,"[Gev]","P_{T}(#tau_{1})"],
        "eta_1_FM":[60,-3,3,"","#eta(l_{1})"],
        "phi_1_FM":[60,-3,3,"","#phi(l_{1})"],
        "iso_1_FM":[20,0,1,"","relIso(l_{1})"],
        "dZ_1_FM":[10,0,0.2,"[cm]","d_{z}(l_{1})"],
        "d0_1_FM":[10,0,0.2,"[cm]","d_{xy}(l_{1})"],
        "q_1_FM":[10,-5,5,"","charge(l_{1})"],

        "pt_2_FM":[40,0,200,"[Gev]","P_{T}(l_{2})"],
        "eta_2_FM":[60,-3,3,"","#eta(l_{2})"],
        "phi_2_FM":[60,-3,3,"","#phi(l_{2})"],
        "iso_2_FM":[20,0,1,"","relIso(l_{2})"],
        "dZ_2_FM":[10,0,0.2,"[cm]","d_{z}(l_{2})"],
        "d0_2_FM":[10,0,0.2,"[cm]","d_{xy}(l_{2})"],
        "q_2_FM":[10,-5,5,"","charge(l_{2})"],

	"iso_3_FM":[20,0,1,"","relIso(l_{3})"],
        "pt_3_FM":[40,0,200,"[Gev]","P_{T}(l_{3})"],
        "eta_3_FM":[60,-3,3,"","#eta(l_{3})"],
        "phi_3_FM":[60,-3,3,"","#phi(l_{3})"],
        "dZ_3_FM":[10,0,0.2,"[cm]","d_{z}(l_{3})"],
        "d0_3_FM":[10,0,0.2,"[cm]","d_{xy}(l_{3})"],

        "iso_4_FM":[20,0,1,"","relIso(l_{4})"],
        "pt_4_FM":[40,0,200,"[Gev]","P_{T}(l_{4})"],
        "eta_4_FM":[60,-3,3,"","#eta(l_{4})"],
        "phi_4_FM":[60,-3,3,"","#phi(l_{4})"],
        "dZ_4_FM":[10,0,0.2,"[cm]","d_{z}(l_{4})"],
        "d0_4_FM":[10,0,0.2,"[cm]","d_{xy}(l_{4})"],


        "njets_FM":[10,-0.5,9.5,"","nJets"],

        "jpt_1_FM":[10,0,200,"[GeV]","Jet^{1} P_{T}"], 
        "jeta_1_FM":[60,-3,3,"","Jet^{1} #eta"],
        "jpt_2_FM":[10,0,200,"[GeV]","Jet^{2} P_{T}"], 
        "jeta_2_FM":[6,-3,3,"","Jet^{2} #eta"],

        "bpt_1_FM":[40,0,200,"[GeV]","BJet^{1} P_{T}"], 
        "bpt_2_FM":[40,0,200,"[GeV]","BJet^{2} P_{T}"], 

        "nbtag_FM":[5,-0.5,4.5,"","nBTag"],
        "beta_1_FM":[60,-3,3,"","BJet^{1} #eta"],
        "beta_2_FM":[60,-3,3,"","BJet^{2} #eta"],

        "met_FM":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
        "met_phi_FM":[60,-3,3,"","#it{p}_{T}^{miss} #phi"], 
        "puppi_phi_FM":[60,-3,3,"","PUPPI#it{p}_{T}^{miss} #phi"], 
        "puppimet_FM":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 

        "mll_FM":[40,50,130,"[Gev]","m(l^{+}l^{-})"],

        "m_vis_FM":[30,50,200,"[Gev]","m(#tau#tau)"],
        "pt_tt_FM":[40,0,200,"[GeV]","P_{T}(#tau#tau)"],
        "H_DR_FM":[60,0,6,"","#Delta R(#tau#tau)"],
        #"H_tot_FM":[30,0,200,"[GeV]","m_{T}tot(#tau#tau)"],

        "m_sv_FM":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "mt_sv_FM":[10,0,200,"[Gev]","m_{T}(#tau#tau)(SV)"],
        "AMass_FM":[100,50,550,"[Gev]","m_{Z+H}(SV)"],

        "Z_Pt_FM":[10,0,200,"[Gev]","P_T(l_{1}l_{2})"],
        "Z_DR_FM":[60,0,6,"","#Delta R(l_{1}l_{2})"],


        "inTimeMuon_1_FM":[10,-5,5,"","inTimeMuon_1"],
        "isGlobal_1_FM":[10,-5,5,"","isGlobal_1"],
        "isTracker_1_FM":[10,-5,5,"","isTracker_1"],
        "looseId_1_FM":[10,-5,5,"","looseId_1"],
        "mediumId_1_FM":[10,-5,5,"","mediumId_1"],
        "Electron_mvaFall17V2noIso_WP90_1_FM":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_1"],
        "gen_match_1_FM":[30,-0.5,29.5,"","gen_match_1"],


        "inTimeMuon_2_FM":[10,-5,5,"","inTimeMuon_2"],
        "isGlobal_2_FM":[10,-5,5,"","isGlobal_2"],
        "isTracker_2_FM":[10,-5,5,"","isTracker_2"],
        "looseId_2_FM":[10,-5,5,"","looseId_2"],
        "mediumId_2_FM":[10,-5,5,"","mediumId_2"],
        "Electron_mvaFall17V2noIso_WP90_2_FM":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_2"],
        "gen_match_2_FM":[30,-0.5,29.5,"","gen_match_2"],

        "inTimeMuon_3_FM":[10,-5,5,"","inTimeMuon_3"],
        "isGlobal_3_FM":[10,-5,5,"","isGlobal_3"],
        "isTracker_3_FM":[10,-5,5,"","isTracker_3"],
        "looseId_3_FM":[10,-5,5,"","looseId_3"],
        "mediumId_3_FM":[10,-5,5,"","mediumId_3"],
        "Electron_mvaFall17V2noIso_WP90_3_FM":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_3"],
        "gen_match_3_FM":[30,-0.5,29.5,"","gen_match_3"],



        "inTimeMuon_4_FM":[10,-5,5,"","inTimeMuon_4"],
        "isGlobal_4_FM":[10,-5,5,"","isGlobal_4"],
        "isTracker_4_FM":[10,-5,5,"","isTracker_4"],
        "looseId_4_FM":[10,-5,5,"","looseId_4"],
        "mediumId_4_FM":[10,-5,5,"","mediumId_4"],
        "Electron_mvaFall17V2noIso_WP90_4_FM":[10,-5,5,"","Electron_mvaFall17V2noIso_WP90_4"],
        "gen_match_4_FM":[30,-0.5,29.5,"","gen_match_4"],
}

#for plotVar in plotSettings :
#    name = plotVar+"_FM"
#    plotSettings.update(name :[plotVar[0],plotVar[1],plotVar[2],plotVar[3],plotVar[4]])



def makeMultiPlots (year=2018,sign='OS', LTcut=0, tag=''):
    col  = '4'
    if 'ZPeak' in tag  : col = '5'
    for plotVar in plotSettings :

     #command="cd plots;montage -auto-orient -title {2:s} -tile 2x4 -geometry +5+5 -page A4 *{0:s}*_{1:s}_{2:s}_{3:s}_log_{4:s}brute.png Multi_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}brute_log.pdf;cd ..".format(str(year),sign,plotVar, str(args.workingPoint),str(args.bruteworkingPoint))
     #os.system(command)
     #Stack_2018_eeee_OS_m_sv_FM_64_log_64brute_0_ZPeak.png
     plotVar=plotVar.replace('[','_')
     plotVar=plotVar.replace(']','')
     #print '--->', '*{0:s}*_{1:s}_{2:s}_{3:s}_log_{4:s}brute*.png'.format(str(year),sign,plotVar, str(args.workingPoint),str(args.bruteworkingPoint), str(tag), str(args.inSystematics), col)
     if 'ZPeak' in tag : command="cd plots_ZPeak;montage -auto-orient -title {2:s} -tile 2x{7:s} -geometry +5+5 -page A4 *{0:s}*_{1:s}_{2:s}_{3:s}_*{4:s}brute*.png Multi_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}brute{5:s}_{6:s}.pdf;cd ..".format(str(year),sign,plotVar, str(args.workingPoint),str(args.bruteworkingPoint), str(tag), str(args.inSystematics), col)

     if tag=='ll' :      command="cd plots;montage -title {2:s} -auto-orient -tile 2x3 -geometry +5+5  -page B5 *{0:s}_ll*_{1:s}_{2:s}_{3:s}_{4:s}brute_{6:s}.png Multi_{0:s}_{1:s}_ll_{2:s}_{3:s}_{4:s}brute_{6:s}.pdf;cd ..".format(str(year),sign,plotVar, str(args.workingPoint),str(args.bruteworkingPoint), str(tag), str(args.inSystematics), col)

     if tag=='' :      command="cd plots{5:s};montage -auto-orient -title {2:s} -tile 2x{7:s} -geometry +5+5 -page A4 *{0:s}*_{1:s}_{2:s}_{3:s}_{4:s}brute{5:s}_{6:s}.png Multi_{0:s}_{1:s}_{2:s}_{3:s}_{4:s}brute{5:s}_{6:s}.pdf;cd ..".format(str(year),sign,plotVar, str(args.workingPoint),str(args.bruteworkingPoint), str(tag), str(args.inSystematics), col)

     os.system(command)
     print command

def ErrorBand (histo, hdata):

    ratioH = hdata.Clone("ratioH")
    ratioErrH = histo.Clone("ratioErrH")
    ratioErrSyst = histo.Clone("ratioErrSyst")
    ratioH.SetMarkerColor(1)
    ratioH.SetMarkerStyle(20)
    ratioH.SetMarkerSize(1.2)
    ratioH.SetLineColor(1)
    '''
    ratioH.GetYaxis().SetRangeUser(0.22,1.98)
    ratioH.GetYaxis().SetNdivisions(505)
    ratioH.GetXaxis().SetLabelFont(42)
    ratioH.GetXaxis().SetLabelOffset(0.04)
    ratioH.GetXaxis().SetLabelSize(0.14)
    ratioH.GetXaxis().SetTitleSize(0.13)
    ratioH.GetXaxis().SetTitleOffset(1.2)
    ratioH.GetYaxis().SetTitle("Obs/Exp");
    ratioH.GetYaxis().SetLabelFont(42)
    ratioH.GetYaxis().SetLabelOffset(0.015)
    ratioH.GetYaxis().SetLabelSize(0.13)
    ratioH.GetYaxis().SetTitleSize(0.14)
    ratioH.GetYaxis().SetTitleOffset(0.5)
    ratioH.GetXaxis().SetTickLength(0.07)
    ratioH.GetYaxis().SetTickLength(0.04)
    ratioH.GetYaxis().SetLabelOffset(0.01)
    '''
    hdiv = hdata.Clone('hdiv')
    hdiv.Divide(histo)
    syst_ = 0.02

    muer=0.01;
    tauer=0.05;
    lumierr = 0.025;


    trigerr_ = 0.02
    lumierr_ = 0.025 
    iderr_ = 0.02

    for iB in range(1,hdata.GetNbinsX()+1,1) :
       x1 = hdata.GetBinContent(iB)
       x2 = histo.GetBinContent(iB)
       bkgErr = histo.GetBinError(iB)
       xBkg = histo.GetBinContent(iB)
       #toterr_ = bkgErr*bkgErr 
       toterr_ = bkgErr*bkgErr+ x2*x2*(trigerr_*trigerr_ + lumierr_*lumierr_ + iderr_*iderr_)
       #histo.SetBinError(iB, sqrt(toterr_))

       ratioErrH.SetBinContent(iB,1.0)
       ratioErrH.SetBinError(iB,0.0)
       ratioErrSyst.SetBinContent(iB,1.0)
       ratioErrSyst.SetBinError(iB,0)
       if xBkg > 0. : ratioErrSyst.SetBinError(iB,sqrt(toterr_)/xBkg)
       errBkg = histo.GetBinError(iB)
       errBkgSyst = histo.GetBinError(iB)
       if xBkg>0. :
	   relErr = errBkg/xBkg
	   ratioErrH.SetBinError(iB,relErr)


       if x1>0. and x2>0. :
       #if x1>0  :
	   e1 = hdata.GetBinError(iB)
	   ratio = x1/x2
	   eratio = e1/x2
	   #eratio = hdiv.GetBinError(iB)
	   ratioH.SetBinContent(iB,ratio)
	   ratioH.SetBinError(iB,eratio)
       #else :
       #	   ratioH.SetBinContent(iB,1000)
	    
       

    ratioErrH.SetFillColorAlpha(kGreen,0.5)
    ratioErrH.SetFillStyle(3002)
    ratioErrSyst.SetFillColorAlpha(kRed,0.75)
    ratioErrSyst.SetFillStyle(4004)
    return ratioH, ratioErrH,ratioErrSyst




def makeDiTauStack(outDir,inFile,rootDi,dndm = False, doRatio = False, year=2020, sign='OS', LTcut=0., cat='mmtt', outFileName="plots.root") :
    dndm  = False
    if args.unBlind.lower() == 'true' or args.unBlind.lower() == 'yes' : doRatio = True
    doRatio = True
    
    outFileName = "plots_{0:d}_{1:s}".format(year,sign)
    if args.setlog.lower() == 'yes' or args.setlog.lower() == 'true' : outFileName +="_Log"
    outFileName += ".root"

    #if cat =='eeet' :    fOut = TFile( outFileName, 'recreate' )
    #else :    fOut = TFile( outFileName, 'recreate' )

    lumi_13TeV = cat+"   41.8 fb^{-1}, 2017"
    iPeriod = 4    # 2=2016+2017, 3=All 13TeV, 4 = 2016 5=2017 
    if year==2017: iPeriod = 5
    elif year==2018: iPeriod = 6

    #elif year > 2018 : iPeriod = 2
    else : iPeriod = 3

    xR=0.65   #legend parameters
    xR=0.2    #legend parameters
    lg = TLegend(xR+0.35,0.6,xR+0.8,0.9)
    lg.SetNColumns(3)
    lgf = TLegend(xR+0.35,0.6,xR+0.8,0.9)
    lgf.SetNColumns(2)
    H = 600
    W = 600
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

    c = TCanvas('c_{0:s}'.format(cat),'c_{0:s}'.format(cat),90,90,W,H)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)



    if not doRatio :
       c.SetLeftMargin(L/W)
       c.SetRightMargin(R/W)
       c.SetTopMargin(T/H)
       c.SetBottomMargin(B/H)

    c.cd()
    setLog = False
    if args.setlog.lower() == 'yes' or args.setlog.lower() == 'true' : setLog = True 
    ratioPad = TPad("pad2","",0.0,0.0,1.0,0.29)
    plotPad = TPad("pad1","",0.0016,0.291,1.0,1.0)

    if doRatio :
	plotPad.SetTicks(0,0)
	plotPad.SetLeftMargin(L/W)
	plotPad.SetRightMargin(R/W)
	plotPad.SetTopMargin(T/H)
	plotPad.SetBottomMargin(B_ratio/H) 
	plotPad.SetFillColor(0)
	plotPad.SetBottomMargin(0.05)

	ratioPad.SetLeftMargin  (L/W)
	ratioPad.SetRightMargin (R/W)
	ratioPad.SetTopMargin   (T_ratio/H)
	ratioPad.SetTopMargin   (0.007)
	ratioPad.SetBottomMargin(B_ratio_label/H)
	ratioPad.SetGridy(1)
	ratioPad.SetFillColor(4000)

    else :
	plotPad = TPad("pad1","",0.0,0.03,1.0,1.0)
	plotPad.SetLeftMargin(L/W)
	plotPad.SetRightMargin(R/W)
	plotPad.SetTopMargin(T/H)
	plotPad.SetBottomMargin(B/H)
	
    if setLog : plotPad.SetLogy()
    c.cd()
    plotPad.Draw()
    if doRatio : ratioPad.Draw()
    plotPad.cd()
    print("In makeStack inFile={0:s}".format(inFile))
    #f = TFile(inFile,'update')

    histo = {}
    histoSyst = {}
    
    hsW[cat] = {}
    hW[cat]={}
    hsumall ={}

	    
    lg.SetBorderSize(0)
    lg.SetFillColor(0)
    lg.SetFillStyle (0)
    lg.SetTextSize(0.035)
    lgf.SetBorderSize(0)
    lgf.SetFillColor(0)
    lgf.SetFillStyle (0)
    lgf.SetTextSize(0.035)
    #lg.Draw("same")

    '''
    hall=TH1D("hCutFlowAllGroup_"+cat,"AllGroupCutFlow",20,-0.5,19.5)
    f.cd()
    CutFlows=['hCutFlowPerGroup', 'hCutFlowPerGroupFM']
    #CutFlows=['hCutFlowPerGroupFM']
    c2 = TCanvas('c2','c2',90,90,W,H)
    c2.SetFillColor(0)
    c2.SetBorderMode(0)
    c2.SetFrameFillStyle(0)
    c2.SetFrameBorderMode(0)

    c2.SetLeftMargin(L/W)
    c2.SetRightMargin(R/W)
    c2.SetTopMargin(T/H)
    c2.SetBottomMargin(B/H)
    plotPadd = TPad("pad1","",0.0,0.03,1.0,1.0)
    plotPadd.SetLeftMargin(L/W)
    plotPadd.SetRightMargin(R/W)
    plotPadd.SetTopMargin(T/H)
    plotPadd.SetBottomMargin(B/H)
    plotPadd.SetLogy()
    sizes=[]
    for ih,ihCut in enumerate(CutFlows) : 
        hsW[cat][ih] = THStack("hsW","")
        hall.Reset()
	for group in groups :
	    #if group !='data' : hW[cat][group] = f.Get("hCutFlowWeighted_"+group+"_"+cat)
	    hW[cat][group] = f.Get(ihCut+"_"+group+"_"+cat)
	    #for i in range (11,17) : print hW[cat][group].GetBinContent(i), i, 'group', group, cat,  hW[cat][group].GetName()
	    print hW[cat][group].GetBinContent(16), 'group', group, cat,  hW[cat][group].GetName()

	    
	    hW[cat][group].GetXaxis().SetBinLabel(11, "OS iso/Id pair")
	    hW[cat][group].GetXaxis().SetRange(11,16)
	    #if group != 'Signal' and group != 'data'  : hall.Add(hW[cat][group],1)

	    if group == 'data' :
		try : applyDATAStyle(hW[cat][group])
		except KeyError : pass
		if ih==0 : lg.AddEntry(hW[cat]['data'],group,"ple")
	    elif group == 'Signal' :
		applySignalStyle(hW[cat][group])
		if ih==0 : lg.AddEntry(hW[cat]['Signal'],"ZH#rightarrow#tau#tau X 10","pl")
	    else :
		applyStyle(hW[cat][group],colors[group],1,1001)
		#print 'will be adding bkg process now', group, hW[cat][group].GetSumOfWeights(), hW[cat][group].GetBinContent(16)
		hsW[cat][ih].Add(hW[cat][group])
		if ih==0 : lg.AddEntry(hW[cat][group],group,"f")



	hsWLast = hsW[cat][ih].GetStack().Last()
	#for i in range(16,17) : print  hall.GetXaxis().GetBinLabel(i), 'allbkg', hall.GetBinContent(i), 'ZZ', hW[cat]['ZZ'].GetBinContent(i), 'DY', hW[cat]['DY'].GetBinContent(i), 'top', hW[cat]['Top'].GetBinContent(i), 'WZ', hW[cat]['WZ'].GetBinContent(i), 'Other', hW[cat]['Other'].GetBinContent(i), ' data', hW[cat]['data'].GetBinContent(i), 'hsW', hsWLast.GetBinContent(i), 'cat', cat
	#print 'some total statistics allbkg', hall.Write("hCutFlowAllBkg_"+cat)
	#hall.Write()
	#f.Close()

	c2.cd()
        c2.Clear()
	if args.setlog.lower() == 'yes' or args.setlog.lower() == 'true' : setLog = True

	gPad.SetLogy()
	c2.cd()
	if ih==0 : plotPadd.Draw()
	#hsWLast.SetMinimum(0.5)
	hW[cat]['data'].SetMinimum(0.5)
	hsWLast.SetMaximum(hW[cat]['data'].GetMaximum()*10e+03)
	hW[cat]['data'].SetMaximum(5000)
	hW[cat]['data'].Draw("ep hist")
	hsWLast.Draw("hist same")
	hsW[cat][ih].Draw("hist same")
	hW[cat]['data'].Draw("ep same hist")
	hW[cat]['Signal'].Scale(10)
	#hW['Signal'].SetLineColor(0)
	#hW['Signal'].SetMarkerSize(2)
	#hW['Signal'].SetLineColor(0)
	hW[cat]['Signal'].Draw("same  hist")
	lg.Draw("same")

	signText = 'Same Sign_{0:s}'.format(cat)
	if sign == 'OS' : signText = 'OS {0:s}'.format(cat)
	hMax = hW[cat]['data'].GetMaximum()
	lTex2a = TLatex(hW[cat]['data'].GetBinLowEdge(11), hMax*0.5,'{0:s}'.format(signText))
	lTex2a = TLatex(hW[cat]['data'].GetBinLowEdge(11)+0.5,hW[cat]['data'].GetMinimum() + 500,'{0:s}'.format(signText))
	lTex2a.SetTextSize(0.035) 
	lTex2a.Draw()
	CMS_lumi.CMS_lumi(c2, iPeriod, 10)


	gPad.RedrawAxis()
	gPad.Modified()
	gPad.Update()
	c2.SaveAs("./plots/{2:s}_{0:s}_{1:s}.png".format( str(cat), str(year), str(ihCut)))


        #hCutFlowPerGroup_eeem_2018.png
        #sizes=[hW[cat]['Other'].GetBinContent(16)+hW[cat]['Top'].GetBinContent(16), hW[cat]['DY'].GetBinContent(16), hW[cat]['WZ'].GetBinContent(16), hW[cat]['ZZ'].GetBinContent(16) ]
        #makePie(sizes, ngroup, cat, str(ihCut))

    #for ih,ihCut in enumerate(CutFlows) : 
    #command="cd plots;montage -auto-orient -title {4:s} -tile 2x4 -geometry +5+5 -page A4 {4:s}_*_{0:s}.png Multi_{4:s}_{0:s}_{1:s}_{2:s}_{3:s}brute.pdf;cd ..".format(str(year),sign, str(args.workingPoint),str(args.bruteworkingPoint), str(ihCut), cat)
    #os.system(command)


    command="cd plots;montage -auto-orient -title {4:s} -tile 2x4 -geometry +5+5 -page A4 {4:s}_pie_*.png Multi_{4:s}_pie_{0:s}_{1:s}_{2:s}_{3:s}brute.pdf;cd ..".format(str(year),sign, str(args.workingPoint),str(args.bruteworkingPoint), str(ihCut), cat)
    os.system(command)
    '''

    f = TFile(inFile,'read')
    '''
    fjesUp = TFile('allGroups_2018_OS_LT00_64SV_64brute_jesTotalUp.root', 'read')
    fjesDown = TFile('allGroups_2018_OS_LT00_64SV_64brute_jesTotalUp.root', 'read')
    fjerUp = TFile('allGroups_2018_OS_LT00_64SV_64brute_jerUp.root', 'read')
    fjerDown = TFile('allGroups_2018_OS_LT00_64SV_64brute_jerDown.root', 'read')
    fUnclUp = TFile('allGroups_2018_OS_LT00_64SV_64brute_UnclUp.root', 'read')
    fUnclDown = TFile('allGroups_2018_OS_LT00_64SV_64brute_UnclDown.root', 'read')
    '''

    extratag=''
    if 'ZPeak' in inFile : extratag = '_ZPeak'
    #f.cd()
    for plotVar in plotSettings :
        histo[plotVar] ={}
        histoSyst[plotVar] ={}
        hsumall[plotVar] ={}
        hsum ={}
        hsumjesTotalDown ={}
        hsumjesTotalUp ={}
        hsumjerUp ={}
        hsumjerDown ={}
        hsumUnclUp ={}
        hsumUnclDown ={}
        hs=[]
        hs = THStack("hs","")
        '''
        hsSystjesTotalUp = THStack("hsjesTotalUp","")
        hsSystjesTotalDown = THStack("hsjesTotalDown","")
        hsSystjerUp = THStack("hsjerUp","")
        hsSystjerDown = THStack("hsjerDown","")
        hsSystUnclUp = THStack("hsjerUnclUp","")
        hsSystUnclDown = THStack("hsjerUnclDown","")
        '''

        #hsall = THStack("hsall","")
        for group in groups :
            units = plotSettings[plotVar][3]
            labelX = plotSettings[plotVar][4]
            try  : 
	        histo[plotVar][group] ={}
	        histoSyst[plotVar][group] ={}
	    except KeyError : continue
	    h_ = "h{0:s}_{1:s}_{2:s}".format(group,cat,plotVar)
            #print 'will try ', "h{0:s}_{1:s}_{2:s}".format(group,cat,plotVar)
            if 'CutFlow' in plotVar : 
	        h_ = "hCutFlowPerGroup_{0:s}_{1:s}".format(group,cat)
            if 'CutFlowFM' in plotVar : 
	        h_ = "hCutFlowPerGroupFM_{0:s}_{1:s}".format(group,cat)


            try :
	        #print 'will try to read', h_
	        histo[plotVar][group] = f.Get(h_)
                '''
	        histoSyst[plotVar][group]['jesTotalUp'] = fjesUp.Get(h_)
	        histoSyst[plotVar][group]['jesTotalDown'] = fjesDown.Get(h_)
	        histoSyst[plotVar][group]['jerUp'] = fjerUp.Get(h_)
	        histoSyst[plotVar][group]['jerDown'] = fjerDown.Get(h_)
	        histoSyst[plotVar][group]['UnclUp'] = fUnclUp.Get(h_)
	        histoSyst[plotVar][group]['UnclDown'] = fUnclDown.Get(h_)
                '''

            except KeyError : continue
	    if not histo[plotVar][group] : continue


            #print histo[plotVar][group].GetName(), histo[plotVar][group].GetNbinsX()
	    if 'gen_match' in plotVar and group =='data': histo[plotVar][group].Scale(0)

	    if 'gen_match' in plotVar :


		if 'gen_match_' in plotVar :
                    if (cat[:2]=='ee' or cat[:2]=='mm' or cat[2:]=='em') and 'tt' not in cat : 
                    

			histo[plotVar][group].GetXaxis().SetBinLabel(1,"unmatched")
			histo[plotVar][group].GetXaxis().SetBinLabel(2,"prompt ")
			histo[plotVar][group].GetXaxis().SetBinLabel(16,"prompt #tau")
			histo[plotVar][group].GetXaxis().SetBinLabel(23,"prompt g")
			histo[plotVar][group].GetXaxis().SetBinLabel(6,"b#rightarrow l")
			histo[plotVar][group].GetXaxis().SetBinLabel(5,"c#rightarrow l")
			histo[plotVar][group].GetXaxis().SetBinLabel(4,"lq#rightarrow l")


		if 'gen_match_3' in plotVar or 'gen_match_4' in plotVar :
		    if 'tt' in cat :  #tau

			histo[plotVar][group].GetXaxis().SetBinLabel(1,"unmachted")
			histo[plotVar][group].GetXaxis().SetBinLabel(2,"prompt e")
			histo[plotVar][group].GetXaxis().SetBinLabel(3,"prompt #mu")
			histo[plotVar][group].GetXaxis().SetBinLabel(4,"#tau #rightarrow e")
			histo[plotVar][group].GetXaxis().SetBinLabel(5,"#tau #rightarrow #mu")
			histo[plotVar][group].GetXaxis().SetBinLabel(6,"#tau_{h}")

		if 'gen_match_4' in plotVar :
		    if cat[2:]=='mt' or cat[2:]=='et' in cat:  #tau

			histo[plotVar][group].GetXaxis().SetBinLabel(1,"unmachted")
			histo[plotVar][group].GetXaxis().SetBinLabel(2,"prompt e")
			histo[plotVar][group].GetXaxis().SetBinLabel(3,"prompt #mu")
			histo[plotVar][group].GetXaxis().SetBinLabel(4,"#tau #rightarrow e")
			histo[plotVar][group].GetXaxis().SetBinLabel(5,"#tau #rightarrow #mu")
			histo[plotVar][group].GetXaxis().SetBinLabel(6,"#tau_{h}")
            
	    #if 'gen_match' not in plotVar : histo[plotVar][group].Rebin(2)
	    if 'CutFlow' in histo[plotVar][group].GetName() : histo[plotVar][group].GetXaxis().SetRange(11,16)
            if dndm : convertToDNDM(histo[plotVar][group])
            if group == 'data' :
                try : applyDATAStyle(histo[plotVar][group])
                except KeyError : pass
            if group == 'Signal' :
                applySignalStyle(histo[plotVar][group])
            if group != 'data' and group != 'Signal' :
                if group not in fakegroup : applyStyle(histo[plotVar][group],colors[group],1,1001)
                #if group== 'f1' or group== 'f2' : histo[plotVar][group].SetLineColor(kMagenta-10)
                #if group== 'fakes'  : histo[plotVar][group].SetLineColor(kBlack)
                if group in fakegroup : 
                    applyStyle(histo[plotVar][group],colors[group],1,3001)

                #if 'f1' not in group and 'f2' not in group and 'fakes' not in group and '_FM' not in plotVar : hs.Add(histo[plotVar][group]) 
                #if group not in fakegroup and '_FM' in plotVar : hs.Add(histo[plotVar][group]) 
                hs.Add(histo[plotVar][group]) 
                #hsSystjesTotalDown.Add(histoSyst[plotVar][group]['jesTotalDown']) 
                #hsSystjesTotalUp.Add(histoSyst[plotVar][group]['jesTotalUp']) 
                #hsSystjerDown.Add(histoSyst[plotVar][group]['jerDown']) 
                #hsSystjerUp.Add(histoSyst[plotVar][group]['jerUp']) 

            #if '_met' in plotVar : print '============', group, histo[plotVar][group].GetSumOfWeights()
	try : hs.GetStack().Last()
	except ReferenceError  : continue

	hsum = hs.GetStack().Last()
        '''
	hsumjesTotalUp = hsSystjesTotalUp.GetStack().Last()
	hsumjesTotalUp.SetLineStyle(2)
	hsumjesTotalDown = hsSystjesTotalDown.GetStack().Last()
	hsumjesTotalDown.SetLineStyle(3)
	hsumjerUp = hsSystjerUp.GetStack().Last()
	hsumjerUp.SetLineStyle(4)
	hsumjerDown = hsSystjerDown.GetStack().Last()
	hsumjerDown.SetLineStyle(5)
        '''

        hh = hsum.GetMaximum()
        hMax = hh*2
        if histo[plotVar]['data'].GetMaximum() > hh : hMax = histo[plotVar]['data'].GetMaximum()
        if setLog : hMax = 75e+03+hh
        else  : 
            hMax = 2*max(hsum.GetMaximum(),histo[plotVar]['data'].GetMaximum())

	if setLog : hs.SetMinimum(0.001)
	else : hs.SetMinimum(0.01)
	if not hs : continue
         
	hsum.SetMinimum(0.001)
	if setLog : 
	    hsum.SetMinimum(0.015)
            if 'w_fm' in plotVar :
               print 'will set this to small number==============================================' 
               hs.SetMinimum(0.00001)
               hsum.SetMinimum(0.00001)
        hsum.SetMaximum(hMax)

        if cat[:2] == 'ee': labelX = labelX.replace('l_','e_')
        if cat[:2] == 'mm' : labelX = labelX.replace('l_','#mu_')
        hsum.GetXaxis().SetTitleSize(0.045)
	if doRatio :
	    hsum.GetXaxis().SetLabelSize(0)
	    hsum.GetXaxis().SetTitle('')
	else :
	    if units!="" :
		hsum.GetXaxis().SetTitle(labelX+" "+units)
	    else :
		hsum.GetXaxis().SetTitle(labelX)

	try : hsum.GetYaxis().SetTitle("Events")
        except KeyError : pass

	if units !='' : 
	    binw = hsum.GetBinLowEdge(2) - hsum.GetBinLowEdge(1)
            un = units.replace('[','')
            un = un.replace(']','')
	    hsum.GetYaxis().SetTitle("Events / {0:.1f} {1:s}".format(binw,un))

	hsum.GetYaxis().SetTitleOffset(1.5)

	if dndm : hsum.GetYaxis().SetTitle("dN/d"+labelX)

        for i in range(1,hsum.GetNbinsX()+1) : 
	    try :
	        if hsum.GetBinContent(i) > 0 and float(histo[plotVar]['Signal'].GetBinContent(i)/sqrt(histo[plotVar]['Signal'].GetBinContent(i) + hsum.GetBinContent(i))) > 0.2 : 
	            #print 'will have to blind %i for var %s', i, plotVar
	            histo[plotVar]['data'].SetBinContent(i,0)
	    except ValueError : continue
        
        #print 'for ',plotVar, histo[plotVar]['data'].GetEntries()
        bkgdErr = hsum.Clone("bkgdErr")
        bkgdErr.SetFillStyle(3013)
        bkgdErr.SetFillColor(1)
        bkgdErr.SetMarkerStyle(21)
        bkgdErr.SetMarkerSize(0)
	hsum.Draw("hist")
	hs.Draw("hist same ")
        bkgdErr.Draw("e2same")
	#hsumjesTotalDown.Draw("hist same e2")
	#hsumjesTotalUp.Draw("hist same e2")
	#hsumjerDown.Draw("hist same e2")
	#hsumjerUp.Draw("hist same e2")
	if doRatio : 
	    histo[plotVar]['data'].Draw("same ep hist")
	histo[plotVar]['Signal'].Draw("same e1 hist")
	#hsum2 = hsum.Clone("hsum2")
        #hsum2.SetLineColor(histo[plotVar]['Signal'].GetLineColor())
        #hsum2.SetFillColor(0)
        #hsum2.Add(histo[plotVar]['Signal'])
	#hsum2.Draw("same hist")

	if doRatio :
	    data2 = histo[plotVar]['data'].Clone("data")
	    mc = hsum.Clone('mc')
            if 'gen_match' in plotVar : 
	        data2 = hsum.Clone()

	    xmin = mc.GetXaxis().GetXmin()
	    xmax = mc.GetXaxis().GetXmax()
            
	    if 'CutFlow' in plotVar :
                xmin=9.5
                xmax=15.5
	    line = TLine(xmin,1.0,xmax,1.0)
	    line.SetLineWidth(1)
	    line.SetLineColor(kBlack)

	    #ratioPad.Draw()
	    ratioPad.cd()

	    #mc.Sumw2()
	    #data2.Sumw2()

	    data2.SetMarkerStyle(20)
	    data2.SetTitleSize(0.12,"Y")
	    data2.SetTitleOffset(0.40,"Y")
	    data2.SetTitleSize(0.12,"X")
	    data2.SetLabelSize(0.10,"X")
            if 'gen_match' in plotVar : 
                data2.SetLabelSize(0.13,"X")
                data2.GetXaxis().SetLabelOffset(0.05)
                #data2.GetXaxis().LabelsOption("v")
	    data2.SetLabelSize(0.08,"Y")
	    data2.GetYaxis().SetRangeUser(0.04,2.48)
	    data2.GetYaxis().SetNdivisions(305)
	    data2.GetYaxis().SetTitle("Obs/Exp")

	    if units!="" :
		data2.GetXaxis().SetTitle(labelX+" "+units)
	    else :
		data2.GetXaxis().SetTitle(labelX)

            ratioPad.cd()
            leg = TLegend(0.55,0.8,0.85,0.92,"","brNDC")
            leg.SetBorderSize(0);
            leg.SetTextFont(42);
            leg.SetLineColor(0);
            leg.SetLineStyle(1);
            leg.SetLineWidth(0);
            leg.SetFillColor(0);
            leg.SetFillStyle(1001);
            leg.SetFillStyle(0);
            hRatio, herror, herrorsyst = ErrorBand(hsum,data2)
	    line.Draw()
            entry=leg.AddEntry(herror,"Syst. unc.","f");
	    #data2.Divide(mc)
            #data2.Draw("P")
            hRatio.Draw("P")
            herrorsyst.Draw("e2 same ")
            herror.Draw("e2 same ")
            hRatio.Draw("e same")
            #herrorSyst = hRatio.Clone('herrorSyst')


            #data2.Draw("e same")

            leg.Draw("same")
	    line.Draw("same")
            #gPad.RedrawAxis()

	#c.cd()
	plotPad.cd()
	lg.Clear()
	lgf.Clear()
        totsum=0
        sizes=[]
        piegroup=[]
        colorgroup=[]
	for group in groups :
	    try :
                #if plotVar == 'met' : 
                    #if group != 'data' and group != 'Signal' and 'fakes' not in group and  'f1' not in group and  'f2' not in group: 
                        #if histo[plotVar][group].GetSumOfWeights() > 0 : 
			    #sizes.append(histo[plotVar][group].GetSumOfWeights())
			    #print group, cat, "\t", histo[plotVar][group].GetSumOfWeights() , "\t", '{0:10.3f}'.format(histo[plotVar][group].GetSumOfWeights()/hsum.GetSumOfWeights())
			    #piegroup.append(group)
			    #colorgroup.append(colors[group])
		if group == 'data' : lg.AddEntry(histo[plotVar][group],group,"ple")
		elif group == 'Signal' : 
                    lg.AddEntry(histo[plotVar][group],"ZH#rightarrow#tau#tau","pl")
                    lgf.AddEntry(histo[plotVar][group],"ZH#rightarrow#tau#tau","pl")

		else : 
                    if 'f1' not in group and 'f2' not in group and 'fakes' not in group and '_FM' not in plotVar and group in groupss: lg.AddEntry(histo[plotVar][group],group,"f")
                    #if group not in fakegroup and  group!='Top' and group!='DY' and '_FM' in plotVar :  lgf.AddEntry(histo[plotVar][group],group,"f")
                    if group not in fakegroup and  group!='Top' and group!='DY' and group!='f1' and group!='f2' and 'fakes' !=group and '_FM' in plotVar :  lgf.AddEntry(histo[plotVar][group],group,"f")
                    if group not in fakegroup and group=='f1' : lgf.AddEntry(histo[plotVar][group],'f1',"f")
                    if group not in fakegroup and group=='f2' : lgf.AddEntry(histo[plotVar][group],'f2',"f")
                    if group not in fakegroup and group=='fakes' : lgf.AddEntry(histo[plotVar][group],'f1,f2',"f")
                       
	    except KeyError :
		continue
        #sizes=[hW[cat]['Other'].GetBinContent(16)+hW[cat]['Top'].GetBinContent(16), hW[cat]['DY'].GetBinContent(16), hW[cat]['WZ'].GetBinContent(16), hW[cat]['ZZ'].GetBinContent(16) ]
        

	if '_FM' not in plotVar : lg.Draw("same")
	if '_FM' in plotVar : lgf.Draw("same")

	lTex1 = TLatex(120.,0.97*hMax,'Preliminary {0:d}'.format(year))
	lTex1.SetTextSize(0.04) 
	#lTex1.Draw("same")
	signText = 'Same Sign_{0:s}'.format(cat)
	#if sign == 'OS' : signText = 'Opposite Sign'
	if sign == 'OS' : signText = 'OS {0:s}'.format(cat)
        
	if setLog : lTex2 = TLatex(histo[plotVar][group].GetBinLowEdge(histo[plotVar][group].GetNbinsX()-3), hMax*0.55,'{0:s}'.format(signText))
	else: lTex2 = TLatex(histo[plotVar][group].GetBinLowEdge(2), hMax*0.55,'{0:s}'.format(signText))
	#lTex2 = TLatex(30.,0.8*hMax,'{0:s}'.format(signText))
        if setLog : lTex2 = TLatex(histo[plotVar][group].GetBinLowEdge(2),histo[plotVar][group].GetMinimum() + 1000,'{0:s}'.format(signText))
	if 'CutFlow' in histo[plotVar][group].GetName() : 
            lTex2 = TLatex(histo[plotVar][group].GetBinLowEdge(11)+0.5 ,histo[plotVar][group].GetMinimum() + 1000,'{0:s}'.format(signText))
	lTex2.SetTextSize(0.045) 
	lTex2.Draw('same')
        CMS_lumi.CMS_lumi(c, iPeriod, 11)
	#plotting.FixBoxPadding(plotPad,plotPad, 0.01);

        plotPad.cd()
        plotPad.Update()
        plotPad.RedrawAxis()

	outFileBase = "Stack_{0:d}_{1:s}_{2:s}_{3:s}_{4:s}".format(year,cat,sign,plotVar, str(args.workingPoint)) 
	if setLog : outFileBase = "Stack_{0:d}_{1:s}_{2:s}_{3:s}_{4:s}_log".format(year,cat,sign,plotVar, str(args.workingPoint)) 
	outFileBase = outFileBase +"_"+str(args.bruteworkingPoint)+"brute_"+str(args.inSystematics)
        outFileBase=outFileBase.replace('[','_')
        outFileBase=outFileBase.replace(']','')
	c.SetName(outFileBase)
	c.SetTitle(outFileBase)
	c.SaveAs("./plots{1:s}/{0:s}{1:s}.png".format(outFileBase,extratag))
        #if plotVar == 'met' :   makePie(sizes, piegroup, cat, colorgroup,'MC_2018')

        #del histo[plotVar][group]
        #del hs
        #del hsum
	#fOut.cd()
        #c.Write("{0:d}_{1:s}_{2:s}_{3:s}".format(year,cat,sign,plotVar))
        #c.Write()	#c.SaveAs("{0:s}.root".format(outFileBase))
    f.Close()
    del f
    del c
    del lg
    del lgf
    del plotPad
    del ratioPad
    

    
    
if __name__ == '__main__':

#def makeDiTauStack(outDir,inFile,rootDir,s,labelX, units = "GeV",left=false,channel = "",
#                   json = "Golden",log = false,dndm=false, doRatio = false) :
    args = getArgs()
    inFileName = args.inFile
    year  = int(inFileName.split('_')[1])
    sign  = inFileName.split('_')[2]
    LTcut = float(inFileName.split('_')[3][2:4])
    tdrstyle.setTDRStyle()
    writeExtraText = True       # if extra text
    extraText  = "Preliminary"  # default extra text is "Preliminary"
    lumi_sqrtS = "13 TeV"

    cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}
    #cats = { 1:'llet', 2:'llmt', 3:'lltt', 4:'llem'}
    extratag=''
    if 'ZPeak' in inFileName : 
        extratag = '_ZPeak'
        cats= { 1:'eeee', 2:'eemm' , 3:'mmee', 4:'mmmm', 5:'eee', 6:'eem', 7:'mme', 8:'mmm', 9:'ee', 10:'mm'}


    if len(cats)==4 : extratag ='ll'

    print cats
#   see comments on cat argument at top of file

    #cats = { 1:'eeet', 2:'eemt'}

    if args.cat.lower() == 'all' :
        for cat in cats.values() :
	   print cat
           #makeDiTauStack('.','{0:s}'.format(inFileName),'', False, False, year=year,sign=sign,LTcut=LTcut,cat=cat)
	       
    makeMultiPlots(year=year,sign=sign,LTcut=LTcut, tag=extratag)
    #command="cd plots;montage -auto-orient -title {4:s} -tile 2x4 -geometry +5+5 -page A4 MC_{0:s}_pie_*.png Multi_pie_{0:s}_{1:s}_{2:s}_{3:s}brute.pdf;cd ..".format(str(year),sign, str(args.workingPoint),str(args.bruteworkingPoint), cat)
    #os.system(command)
#def makeDiTauStack(outDir,inFile,rootDir,channel = "",  dndm = False, doRatio = False, year=2017, sign='OS', LTcut=0., cat='mmtt') :
        
   

