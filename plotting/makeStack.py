import tdrstyle
import CMS_lumi
from ROOT import gSystem, gStyle, gROOT, kTRUE
from ROOT import TCanvas, TH1D, TH1F, THStack, TFile, TPad, TLegend, TLatex, TLine, TAttMarker, TMarker, TColor
from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure, kRed, kGreen
from math import sqrt
import array
import plotting
import os

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
    parser.add_argument("-w","--wait",default='wait',help="Wait for enter")
    parser.add_argument("-L","--setlog",default='yes',help="Set log scale")
    parser.add_argument("-u","--unBlind",default='yes',help="Unblind data")
    
    return parser.parse_args()



def applyStyle( h, fill, line, fillStyle) :
    h.SetFillColor(fill)
    h.SetLineColor(line)
    h.SetFillStyle(fillStyle)
    h.SetLineWidth(2)

def applySignalStyle(h) :
    h.SetLineWidth(3)
    h.SetFillColor(0)
    h.SetLineColor(kRed)
    h.SetLineStyle(2)
    h.SetMarkerSize(1.5);
    h.SetMarkerColor(kRed);



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



groups = ['data','WJets','Rare','Top','DY','ZZ','Signal']

plotSettings = { # [nBins,xMin,xMax,units]

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


        "njets":[10,-0.5,9.5,"","nJets"],
        #"Jet_pt":[100,0,500,"[GeV]","Jet P_{T}"], 
        #"Jet_eta":[60,-3,3,"","Jet #eta"],
        #"Jet_phi":[60,-3,3,"","Jet #phi"],
        #"Jet_ht":[100,0,800,"[GeV]","H_{T}"],

        "jpt_1":[60,0,300,"[GeV]","Jet^{1} P_{T}"], 
        "jeta_1":[60,-3,3,"","Jet^{1} #eta"],
        "jpt_2":[60,0,300,"[GeV]","Jet^{2} P_{T}"], 
        "jeta_2":[6,-3,3,"","Jet^{2} #eta"],

        "bpt_1":[40,0,200,"[GeV]","BJet^{1} P_{T}"], 
        "bpt_2":[40,0,200,"[GeV]","BJet^{2} P_{T}"], 

        "nbtag":[5,-0.5,4.5,"","nBTag"],
        #"nbtagLoose":[10,0,10,"","nBTag Loose"],
        #"nbtagTight":[5,0,5,"","nBTag Tight"],
        "beta_1":[60,-3,3,"","BJet^{1} #eta"],
        "beta_2":[60,-3,3,"","BJet^{2} #eta"],

        "met":[50,0,250,"[GeV]","#it{p}_{T}^{miss}"], 
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

        "mt_sv":[60,0,300,"[Gev]","m_{T}(#tau#tau)"],
        "m_sv":[60,0,300,"[Gev]","m(#tau#tau)(SV)"],
        "m_sv_new":[60,0,300,"[Gev]","m(#tau#tau)(newSV)"],
        "mt_sv":[60,0,300,"[Gev]","m_{T}(#tau#tau)(SV)"],
        #"mt_sv_new":[60,0,300,"[Gev]","m_{T}(#tau#tau)(newSV)"],
        "AMass":[100,50,550,"[Gev]","m_{Z+H}(SV)"],
        #"CutFlowWeighted":[15,0.5,15.5,"","cutflow"],
        #"CutFlow":[15,0.5,15.5,"","cutflow"]

        "Z_Pt":[60,0,300,"[Gev]","P_T(l_{1}l_{2})"],
        "Z_DR":[60,0,6,"","#Delta R(l_{1}l_{2})"],

        "GenMatchTau_3":[10,-0.5,9.5,"","genMatch #tau_{3}"],
        "GenMatchTau_4":[10,-0.5,9.5,"","genMatch #tau_{4}"],
        "DeepTauiD_VSjet_3":[256,-0.5,255.5,"","DeepVSjet_3"],
        "DeepTauiD_VSjet_4":[256,-0.5,255.5,"","DeepVSjet_4"],
        "DeepTauiD_VSe_3":[256,-0.5,255.5,"","DeepVSe_3"],
        "DeepTauiD_VSe_4":[256,-0.5,255.5,"","DeepVSe_4"],
        "DeepTauiD_VSmu_3":[256,-0.5,255.5,"","DeepVSmu_3"],
        "DeepTauiD_VSmu_4":[256,-0.5,255.5,"","DeepVSmu_4"],

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


}




def makeMultiPlots (year=2017,sign='OS', LTcut=0):
    for plotVar in plotSettings :

     print "montage -title {2:s} -tile 2x4 -geometry +10+5 -border 5 -page A4 *{0:s}*_{1:s}_{2:s}_log.png Multi_{0:s}_{1:s}_{2:s}.pdf -auto-orient;cd ..".format(str(year),sign,plotVar)
     command="cd plots;montage -auto-orient -title {2:s} -tile 2x4 -geometry +5+5 -page A4 *{0:s}*_{1:s}_{2:s}_log.png Multi_{0:s}_{1:s}_{2:s}.pdf;cd ..".format(str(year),sign,plotVar)
     os.system(command)


def ErrorBand (histo, hdata):

    bkgRatioErrH  = hdata.Clone("bkgRatioErrH")
    bkgRatioErrH.Reset()
    
    bkgRatioErrH.SetLineColor(kBlack);
    bkgRatioErrH.SetMarkerStyle(20)
    bkgRatioErrH.SetMarkerSize(0)
    bkgRatioErrH.Reset()

    for iB in range(1,hdata.GetNbinsX()+1,1) :
        datX = hdata.GetBinContent(iB);
        datE = hdata.GetBinError(iB);
        bkgX = histo.GetBinContent(iB);
        bkgE = histo.GetBinError(iB);
        datRatioX = 0.
        datRatioE = 0.
        bkgErr = 0.
        if bkgX != 0 : 
            datRatioX = datX/bkgX;
            datatioE = datE/bkgX;
            bkgErr = float(bkgE / bkgX);
        syst_ = 0.02;

        muer=0.02;
        tauer=0.05;
        lumierr = 0.025;

        '''
        allnofake = (allbkg.GetBinContent(iB)-hqcd.GetBinContent(iB))/allbkg.GetBinContent(iB);
        fake = hqcd.GetBinContent(iB)/allbkg.GetBinContent(iB);
        dy =(hdyj.GetBinContent(iB)+hztt.GetBinContent(iB))/allbkg.GetBinContent(iB);
        dyall =(hdyj.GetBinContent(iB))/allbkg.GetBinContent(iB);
        ztt =(hztt.GetBinContent(iB))/allbkg.GetBinContent(iB);
        rest = (hdib.GetBinContent(iB)+httx.GetBinContent(iB)) /allbkg.GetBinContent(iB);
        ww = (hww.GetBinCon tent(iB)) /allbkg.GetBinContent(iB);
        top = htt.GetBinContent(iB)/allbkg.GetBinContent(iB);
        stop = hstop.GetBinContent(iB)/allbkg.GetBinContent(iB);
        '''

        trigerr_ = 0.02
	lumierr_ = 0.025
	iderr_ = 0.02
        #toterr_ =  top*0.05*0.05 + +ww*0.25*0.25 + stop*0.25*0.25+ 0.15*0.15*fake + 0.1*0.1*rest   +0.025*0.25*allnofake + 0.05*0.05*dyall + (muer*muer + tauer*tauer + bkgErr*bkgErr)*allnofake + 0.05*0.05*top +0.04*0.04*stop + 0.09*0.09*dy + 0.04*0.04*ztt + 0.1*0.1;
        toterr_ = bkgErr*bkgErr + trigerr_*trigerr_ + lumierr_*lumierr_ + iderr_*iderr_

        
        bkgRatioErrH.SetBinContent(iB,1);
        bkgRatioErrH.SetBinError(iB,sqrt(toterr_));
        #print toterr_
        #DataHErrP.SetBinContent(iB,datX);
        #DataHErrP.SetBinError(iB,datE);
        #DataHErrM.SetBinContent(iB,bkgX);
        #DataHErrM.SetBinError(iB,bkgE);
    bkgRatioErrH.SetFillColor(kGreen)
    bkgRatioErrH.SetFillStyle(3002)
    return bkgRatioErrH




def makeDiTauStack(outDir,inFile,rootDi,dndm = False, doRatio = False, year=2020, sign='OS', LTcut=0., cat='mmtt', outFileName="plots.root") :
    
    if args.unBlind.lower() == 'true' or args.unBlind.lower() == 'yes' : doRatio = True
    #doRatio = False
    
    outFileName = "plots_{0:d}_{1:s}".format(year,sign)
    if args.setlog.lower() == 'yes' or args.setlog.lower() == 'true' : outFileName +="_Log"
    outFileName += ".root"

    fOut = TFile( outFileName, 'update' )
    tdrstyle.setTDRStyle()
    writeExtraText = True       # if extra text
    extraText  = "Preliminary"  # default extra text is "Preliminary"
    lumi_sqrtS = "13 TeV"
    lumi_13TeV = cat+"   41.8 fb^{-1}, 2017"
    iPeriod = 4    # 2=2016+2017, 3=All 13TeV, 4 = 2016 5=2017 
    if year==2017: iPeriod = 5
    elif year==2018: iPeriod = 6

    #elif year > 2018 : iPeriod = 2
    else : iPeriod = 3

    print '========================================================>', year, iPeriod

    xR=0.65   #legend parameters
    xR=0.2    #legend parameters
    lg = TLegend(xR+0.4,0.6,xR+0.8,0.9)
    lg.SetNColumns(2)
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

    c = TCanvas('c1','c1',90,90,W,H)
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
    f = TFile(inFile)


    histo = {}
    hsumall ={}
    kTop = TColor.GetColor("#ffcc66")
    kDY = TColor.GetColor("#58d885")
    colors = {'data':0,'WJets':kMagenta-10,'Rare':kBlue-8,'ZZ':kAzure-9,'Top':kTop,'DY':kDY,'Signal':kRed}
    for plotVar in plotSettings :
        histo[plotVar] ={}
        hsumall[plotVar] ={}
        hsum ={}
        hs = THStack("hs","")
        hsall = THStack("hsall","")
        f.cd()
        for group in groups :
            units = plotSettings[plotVar][3]
            labelX = plotSettings[plotVar][4]
            try  : histo[plotVar][group] ={}
	    except KeyError : continue
	    h_ = "h{0:s}_{1:s}_{2:s}".format(group,cat,plotVar)
            #print 'will try ', "h{0:s}_{1:s}_{2:s}".format(group,cat,plotVar)
            if 'CutFlow' in plotVar : 
	        if 'data' in group : h_ = "hCutFlow_{0:s}_data".format(cat)
	        else : h_ = "hCutFlow_{0:s}_{1:s}".format(cat,group)


            try : histo[plotVar][group] = f.Get(h_)
            except KeyError : continue
            #print histo[plotVar][group].GetName(), histo[plotVar][group].GetNbinsX()

            '''if 'GenMatchTau' in plotVar : 
	        c.cd()
		#c.Clear()
		plotPad = TPad("pad1","",0.0,0.03,1.0,1.0)
		plotPad.SetLeftMargin(L/W)
		plotPad.SetRightMargin(R/W)
		plotPad.SetTopMargin(T/H)
		plotPad.SetBottomMargin(B/H)
		ratioPad = TPad("pad2","",0.0,0.0,0.0,0.)
		plotPad.Draw()
		ratioPad.Draw()
	    '''
            if 'GenMatchTau' in plotVar : 
	         histo[plotVar][group].GetXaxis().SetBinLabel(2,"prompt e")
	         histo[plotVar][group].GetXaxis().SetBinLabel(3,"prompt #mu")
	         histo[plotVar][group].GetXaxis().SetBinLabel(4,"#tau#rightarrow e")
	         histo[plotVar][group].GetXaxis().SetBinLabel(5,"#tau#rightarrow #mu")
	         histo[plotVar][group].GetXaxis().SetBinLabel(6,"#tau_{h}")
	         histo[plotVar][group].GetXaxis().SetBinLabel(1,"unknown")
            
            if dndm : convertToDNDM(histo[plotVar][group])
            if group == 'data' :
                try : applyDATAStyle(histo[plotVar][group])
                except KeyError : pass
            if group == 'Signal' :
                applySignalStyle(histo[plotVar][group])
            if group != 'data' and group != 'Signal' :
                applyStyle(histo[plotVar][group],colors[group],1,1001)
        
            if group != 'data' and group != 'Signal' : hs.Add(histo[plotVar][group]) 
            #if '_met' in plotVar : print '============', group, histo[plotVar][group].GetSumOfWeights()
        hMax = 75e+03+hs.GetMaximum()
	if not setLog : hMax = 300+hs.GetMaximum()
	hs.SetMinimum(0.)
        #if setLog : 
	#    hs.SetMaximum(10e+05*hs.GetMaximum())
        #else :     hs.SetMinimum(0.)
        hsum=hs.GetStack().Last()
	hsum.SetMinimum(0.)
	if setLog : hsum.SetMinimum(0.015)
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
	    if histo[plotVar]['Signal'].GetBinContent(i) + hsum.GetBinContent(i) > 0 and float(histo[plotVar]['Signal'].GetBinContent(i)/sqrt(histo[plotVar]['Signal'].GetBinContent(i) + hsum.GetBinContent(i))) > 0.2 : 
	        print 'will have to blind %i for var %s', i, plotVar
	        histo[plotVar]['data'].SetBinContent(i,0)

	hsum.Draw("hist")
	hs.Draw("hist same")
	if doRatio : 
	    histo[plotVar]['data'].Draw("same ep hist")
	histo[plotVar]['Signal'].Draw("same e1 hist")

	if doRatio :
	    data2 = histo[plotVar]['data'].Clone("data")
	    mc = histo[plotVar]['Rare'].Clone("Rare")
	    mc.Add(histo[plotVar]['WJets'])
	    mc.Add(histo[plotVar]['Top'])
	    mc.Add(histo[plotVar]['DY'])
	    mc.Add(histo[plotVar]['ZZ'])
	    xmin = mc.GetXaxis().GetXmin()
	    xmax = mc.GetXaxis().GetXmax()
	    line = TLine(xmin,1.0,xmax,1.0)
	    line.SetLineWidth(1)
	    line.SetLineColor(kBlack)

	    #ratioPad.Draw()
	    ratioPad.cd()

	    data2.Divide(data2,mc)

	    data2.SetMarkerStyle(20)
	    data2.SetTitleSize(0.12,"Y")
	    data2.SetTitleOffset(0.40,"Y")
	    data2.SetTitleSize(0.12,"X")
	    data2.SetLabelSize(0.10,"X")
	    data2.SetLabelSize(0.08,"Y")
	    data2.GetYaxis().SetRangeUser(0.42,1.58)
	    data2.GetYaxis().SetNdivisions(305)
	    data2.GetYaxis().SetTitle("Obs/Exp   ")

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
            herror = ErrorBand(mc,data2)
            for iB in range(1,data2.GetNbinsX()+1,1) :
                datX = data2.GetBinContent(iB)
                datE = data2.GetBinError(iB)
                bkgX = mc.GetBinContent(iB)
		if bkgX > 0.000 : data2.SetBinError(iB,datE/bkgX)
		else : data2.SetBinError(iB,0)

	    data2.Draw("P")
	    line.Draw()
            entry=leg.AddEntry(herror,"Syst. unc.","f");
            leg.Draw("same")
            herror.Draw("same e2")

	#c.cd()
	plotPad.cd()
	lg.Clear()
	for group in groups :
	    try :
		#print group, histo[plotVar][group].GetSumOfWeights()

		if group == 'data' : lg.AddEntry(histo[plotVar][group],group,"ple")
		elif group == 'Signal' : lg.AddEntry(histo[plotVar][group],"ZH#rightarrow#tau#tau","pl")
		else : lg.AddEntry(histo[plotVar][group],group,"f")
	    except KeyError :
		continue
	    
	lg.SetBorderSize(0)
	lg.SetFillColor(0)
	lg.SetFillStyle (0)
	lg.SetTextSize(0.035)
	lg.Draw("same")
        '''
	y_min, y_max = (plotting.GetPadYMin(plotPad), plotting.GetPadYMax(plotPad))
	if y_max == 0 : y_max = 100
	try :
	    plotting.FixBothRanges(plotPad, y_min if setLog else 0, 0.05 if setLog else 0, y_max, 0.25)
	    #plotting.FixTopRange(plotPad,plotting.GetPadYMax(plotPad), 0.15);
	    plotting.FixOverlay();
	except KeyError : pass
	'''

	lTex1 = TLatex(120.,0.97*hMax,'Preliminary {0:d}'.format(year))
	lTex1.SetTextSize(0.04) 
	#lTex1.Draw("same")
	signText = 'Same Sign_{0:s}'.format(cat)
	#if sign == 'OS' : signText = 'Opposite Sign'
	if sign == 'OS' : signText = 'OS {0:s}'.format(cat)
        
	lTex2 = TLatex(histo[plotVar][group].GetBinLowEdge(2), hMax*0.5,'{0:s}'.format(signText))
	#lTex2 = TLatex(30.,0.8*hMax,'{0:s}'.format(signText))
        if setLog : lTex2 = TLatex(histo[plotVar][group].GetBinLowEdge(2),histo[plotVar][group].GetMinimum() + 1000,'{0:s}'.format(signText))
	lTex2.SetTextSize(0.045) 
	lTex2.Draw()
        CMS_lumi.CMS_lumi(c, iPeriod, 11)

	#plotting.FixBoxPadding(plotPad,plotPad, 0.01);


        plotPad.cd()
        plotPad.Update()
        plotPad.RedrawAxis()
        #frame = c.GetFrame()
        #frame.Draw()

	outFileBase = "Stack_{0:d}_{1:s}_{2:s}_{3:s}".format(year,cat,sign,plotVar) 
	if setLog : outFileBase = "Stack_{0:d}_{1:s}_{2:s}_{3:s}_log".format(year,cat,sign,plotVar) 
	c.SaveAs("./plots/{0:s}.png".format(outFileBase))
	fOut.cd()
        c.Write("{0:d}_{1:s}_{2:s}_{3:s}".format(year,cat,sign,plotVar))
        #f.Close()
	#c.SaveAs("{0:s}.root".format(outFileBase))
    
    
if __name__ == '__main__':

#def makeDiTauStack(outDir,inFile,rootDir,s,labelX, units = "GeV",left=false,channel = "",
#                   json = "Golden",log = false,dndm=false, doRatio = false) :
    args = getArgs()
    inFileName = args.inFile
    year  = int(inFileName.split('_')[1])
    sign  = inFileName.split('_')[2]
    LTcut = float(inFileName.split('_')[3][2:4])

#   see comments on cat argument at top of file
    cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}
    #cats = { 1:'eeet', 2:'mmmt'}
    #cats = { 1:'eeet'}
    #cats = { 6:'mmmt'}

    if args.cat.lower() == 'all' :
        for cat in cats.values() :
	   print cat
           makeDiTauStack('.','{0:s}'.format(inFileName),'', False, False, year=year,sign=sign,LTcut=LTcut,cat=cat)
	     
    makeMultiPlots(year=year,sign=sign,LTcut=LTcut)
#def makeDiTauStack(outDir,inFile,rootDir,channel = "",  dndm = False, doRatio = False, year=2017, sign='OS', LTcut=0., cat='mmtt') :
        
   

