#
# estimate fake rate for irreducilble backgrounds 
#
import CMS_lumi
from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, TLatex, kRed, kBlue, kBlack, TLegend, TF1, gStyle, gROOT, THStack, TColor, TPad, gPad
from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure, kRed, kGreen
gROOT.SetBatch(True) # don't pop up any plots
import tdrstyle 

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./FakeRates.root',help="File to be analyzed.")
    parser.add_argument("-y","--year",default=2018,type=int,help="Year for data.")
    parser.add_argument("-r","--region",default='SS',type=str,help="Year for data.")
    parser.add_argument("-w","--workingPoint",default='16',type=int,help="16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight")
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


args = getArgs()
era = str(args.year)
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
hList = ['e_et','t_et','m_mt','t_mt','t1_tt','t2_tt', 'e_em', 'm_em']
hListMode = ['t_et','t_mt','t1_tt','t2_tt']
hModes = ['0','1','10','11']

tdrstyle.setTDRStyle()
writeExtraText = True       # if extra text
extraText  = "Preliminary"  # default extra text is "Preliminary"
lumi_sqrtS = "13 TeV"
#lumi_13TeV = cat+"   41.8 fb^{-1}, 2017"
iPeriod = 4    # 2=2016+2017, 3=All 13TeV, 4 = 2016 5=2017
if args.year==2017: iPeriod = 5
if args.year==2018: iPeriod = 6

if args.year > 2018 : iPeriod = 2



kTop = TColor.GetColor("#ffcc66")
kDY = TColor.GetColor("#58d885")
colors = {'WJets':kMagenta-10,'Rare':kBlue-8,'ZZ':kAzure-9,'Top':kTop,'DY':kDY}


# size info
H, W, H_ref, W_ref = 600, 1000, 600, 600
# references for T, B, L, R
T, B, L, R = 0.08*H_ref, 0.12*H_ref, 0.16*W_ref, 0.04*W_ref

#margins for inbetween the pads in a ratio plot
B_ratio = 0.1*H_ref
T_ratio = 0.03*H_ref

#margin required for lebal on bottom of raito plot
B_ratio_label = 0.3*H_ref

# Read in fake-rate histograms and use them to calculate the fake rate factors

fin='FakeRates_{0:s}_{1:s}_{2:s}.root'.format(str(args.year),args.region,str(args.workingPoint))
f = TFile(fin)
hBase, hTight, hBasePrompt, hTightPrompt, hBasePromptMode, hTightPromptMode,= {}, {}, {}, {}, {}, {} 
#groups = ['ZZ','WJets','Rare','Top','DY']
groups = ['WJets','Rare','Top','DY','ZZ']

for h in hList :
    hName = "{0:s}Base".format(h)
    hBase[h] = f.Get(hName) 
    hTight[h] = f.Get("{0:s}Tight".format(h))
    hBase[h].Sumw2()
    hTight[h].Sumw2()

for group in groups :
    hBasePrompt[group], hTightPrompt[group] = {}, {}
    hBasePromptMode[group], hTightPromptMode[group] = {}, {}
    for h in hList :
	hName = "{0:s}_{1:s}BasePrompt".format(group,h)
	#hBasePrompt[group][h] = TH1D(hName,hName,10,0.,100.)
	hBasePrompt[group][h] = f.Get(hName)
	hBasePrompt[group][h].Sumw2()

	hName = "{0:s}_{1:s}TightPrompt".format(group,h)
	#hTightPrompt[group][h] = TH1D(hName,hName,10,0.,100.)
	hTightPrompt[group][h] = f.Get(hName)
	hTightPrompt[group][h].Sumw2()
        print hBasePrompt[group][h].GetName(), hBasePrompt[group][h].GetSumOfWeights(), hTightPrompt[group][h].GetName(), hTightPrompt[group][h].GetSumOfWeights()

        hBasePromptMode[group][h], hTightPromptMode[group][h] = {}, {}

        for m in hModes :
	    hName = "{0:s}_{1:s}_{2:s}Mode_BasePrompt".format(group,h,m)
	    hBasePromptMode[group][h][m] = f.Get(hName)
	    hName = "{0:s}_{1:s}_{2:s}Mode_TightPrompt".format(group,h,m)
	    hTightPromptMode[group][h][m] = f.Get(hName)



# plot raw histograms 

if True :
    c11 = TCanvas('c11','Tight/Base (Data)',50,50,1300,800)
    c11.SetFillColor(0)
    c11.SetBorderMode(0)
    c11.SetFrameFillStyle(0)
    c11.SetFrameBorderMode(0)

    c11.SetLeftMargin(L/W)
    c11.SetRightMargin(R/W)
    c11.SetTopMargin(T/H)
    c11.SetBottomMargin(B/H)
    c11.Divide(4,2)
    ratioPad, plotPad= {}, {}
    htest= {}

    for i, h in enumerate(hList) :
        c11.cd(i+1)
	ratioPad[h] = TPad("pad2","",0.0,0.0,1.0,0.29)
	plotPad[h] = TPad("pad1","",0.0016,0.291,1.0,1.0)
	plotPad[h].SetTicks(0,0)
	plotPad[h].SetLeftMargin(L/W)
	plotPad[h].SetRightMargin(R/W)
	plotPad[h].SetTopMargin(T/H)
	plotPad[h].SetBottomMargin(B_ratio/H)
	plotPad[h].SetFillColor(0)
	plotPad[h].SetBottomMargin(0.05)

	ratioPad[h].SetLeftMargin  (L/W)
	ratioPad[h].SetRightMargin (R/W)
	ratioPad[h].SetTopMargin   (T_ratio/H)
	ratioPad[h].SetTopMargin   (0.007)
	ratioPad[h].SetBottomMargin(B_ratio_label/H)
	ratioPad[h].SetGridy(1)
	ratioPad[h].SetFillColor(4000)

    leg = {}
    for i, h in enumerate(hList) :
        c11.cd(i+1)
	#gPad.SetLogy()
        plotPad[h].Draw()
        ratioPad[h].Draw()
	plotPad[h].SetLogy()
        plotPad[h].cd()
	hBase[h].SetMinimum(0.01)
	hTight[h].SetMinimum(0.01)
        hBase[h].SetLineWidth(2)
        hBase[h].SetLineColor(kBlue)
        #hBase[h].GetXaxis().SetTitle('p_{T} (GeV/c)')
        hBase[h].GetXaxis().SetTitle('')
        hBase[h].GetXaxis().SetLabelSize(0.00)
        hBase[h].GetXaxis().SetTitleSize(0.05)
        yMax = hBase[h].GetMaximum()
        leg[h] = TLegend(0.63,0.73,0.96,0.96,h)
        leg[h].AddEntry(hBase[h],"Base (data)","L")
	leg[h].SetTextSize(0.045)
        hBase[h].GetYaxis().SetTitle('Counts')
        hBase[h].GetYaxis().SetLabelSize(0.05)
        hBase[h].GetYaxis().SetTitleSize(0.05)
        hBase[h].GetYaxis().SetTitleOffset(1.05)
        hBase[h].SetMaximum(hBase[h].GetMaximum()*500)
        hBase[h].Draw()
        hTight[h].SetLineWidth(2)
        hTight[h].SetLineColor(kRed)
        #hTight[h].Scale(5.)
        hTight[h].Draw('SAME')
        leg[h].AddEntry(hTight[h],"Tight (data)","L")
        leg[h].Draw()
        
        ratioPad[h].cd()
        htest[h] = hTight[h].Clone()
        htest[h].SetLineColor(kBlack)
        htest[h].Divide(hBase[h])
        htest[h].GetYaxis().SetLabelSize(0.12)
        htest[h].GetYaxis().SetTitleSize(0.1)
        htest[h].GetYaxis().SetTitleOffset(0.55)
        htest[h].GetXaxis().SetLabelSize(0.12)
        htest[h].GetXaxis().SetTitleSize(0.1)
        htest[h].GetXaxis().SetTitle('p_{T} (GeV/c)')
        htest[h].GetYaxis().SetRangeUser(0.005,htest[h].GetMaximum()*1.1)
        htest[h].GetYaxis().SetNdivisions(305)
        htest[h].GetYaxis().SetTitle("Tight/Base   ")
        htest[h].Draw()
        #leg[h].Draw()
        c11.Update()

    c11.SaveAs("Tight_Base_Data_Hist_"+era+"_"+args.region+"_"+str(args.workingPoint)+".pdf")
    c11.SaveAs("Tight_Base_Data_Hist_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")


######################## Per decay Mode

if True :
    #c12 = TCanvas('c12','Tight/Base (MC)',50,50,1200,600)
    c12 = TCanvas('c12','Tight/Base (Data)',50,50,1600,900)
    c12.SetFillColor(0)
    c12.SetBorderMode(0)
    c12.SetFrameFillStyle(0)
    c12.SetFrameBorderMode(0)

    c12.SetLeftMargin(L/W)
    c12.SetRightMargin(R/W)
    c12.SetTopMargin(T/H)
    c12.SetBottomMargin(B/H)

    c12.Divide(4,4)
    leg = {}
    hsBasePrompt, hsTightPrompt = {}, {}
    hsBasePromptMode, hsTightPromptMode = {}, {}
    ratioPad, plotPad= {}, {}
    hsum, hsumm= {}, {}
    htest= {}
    print hListMode

    for i, h in enumerate(hListMode) : #this is a reduced hList to account only for taus
        ratioPad[h], plotPad[h]= {}, {}


    for i, h in enumerate(hListMode) :
        hsBasePromptMode[h], hsTightPromptMode[h] = {}, {}
        hsum[h], hsumm[h] = {}, {}
	leg[h]= {}
        htest[h]= {}

        for j, m in enumerate(hModes) :
	    c12.cd(i+ 1 + j*4)
	    ratioPad[h][m] = TPad("pad2","",0.0,0.0,1.0,0.29)
	    plotPad[h][m] = TPad("pad1","",0.0016,0.291,1.0,1.0)
	    plotPad[h][m].SetTicks(0,0)
	    plotPad[h][m].SetLeftMargin(L/W)
	    plotPad[h][m].SetRightMargin(R/W)
	    plotPad[h][m].SetTopMargin(T/H)
	    plotPad[h][m].SetBottomMargin(B_ratio/H)
	    plotPad[h][m].SetFillColor(0)
	    plotPad[h][m].SetBottomMargin(0.05)

	    ratioPad[h][m].SetLeftMargin  (L/W)
	    ratioPad[h][m].SetRightMargin (R/W)
	    ratioPad[h][m].SetTopMargin   (T_ratio/H)
	    ratioPad[h][m].SetTopMargin   (0.007)
	    ratioPad[h][m].SetBottomMargin(B_ratio_label/H)
	    ratioPad[h][m].SetGridy(1)
	    ratioPad[h][m].SetFillColor(4000)
	    plotPad[h][m].Draw()
	    ratioPad[h][m].Draw()
	    plotPad[h][m].SetLogy()
	    plotPad[h][m].cd()
	    print 'inside canvas-----------------------', i+1 +4*j, 'for mode', m, 'and channel', h
            hsBasePromptMode[h][m] = THStack("hsBasePromptMode","")
            hsTightPromptMode[h][m] = THStack("hsTightPromptMode","")
	    leg[h][m] = TLegend(0.43,0.63,0.96,0.96,h)
	    leg[h][m].SetTextSize(0.085)
	    title="Prompt Base DM{0:s}(MC)".format(m)
	    leg[h][m].AddEntry(hBasePromptMode['ZZ'][h][m],title,"l")
	    title="Tight Base DM{0:s}(MC)".format(m)
	    leg[h][m].AddEntry(hTightPromptMode['ZZ'][h][m],title,"L")
            
	    for group in groups :
            
		hBasePromptMode[group][h][m].SetLineWidth(2)
		hBasePromptMode[group][h][m].SetLineColor(kBlue)
		hBasePromptMode[group][h][m].GetXaxis().SetTitle('')
		hBasePromptMode[group][h][m].GetXaxis().SetLabelSize(0.05)
		hBasePromptMode[group][h][m].GetXaxis().SetTitleSize(0.05)
		hBasePromptMode[group][h][m].SetMinimum(0.01)
		hBasePromptMode[group][h][m].SetMaximum(hBasePromptMode[group][h][m].GetMaximum()*700)


		hBasePromptMode[group][h][m].GetYaxis().SetTitle('Counts') 
		hBasePromptMode[group][h][m].GetYaxis().SetLabelSize(0.05)
		hBasePromptMode[group][h][m].GetYaxis().SetTitleSize(0.05)

		hsBasePromptMode[h][m].Add(hBasePromptMode[group][h][m])

		hTightPromptMode[group][h][m].SetLineWidth(2)
		hTightPromptMode[group][h][m].SetLineColor(kRed)
		hTightPromptMode[group][h][m].SetMinimum(0.01)

		hsTightPromptMode[h][m].Add(hTightPromptMode[group][h][m])


	    hsum[h][m]=hsBasePromptMode[h][m].GetStack().Last()
	    hsum[h][m].SetMinimum(0.01)
	    hsum[h][m].SetMaximum(hsum[h][m].GetMaximum()*50)
	    hsum[h][m].Draw()
	    hsumm[h][m]=hsTightPromptMode[h][m].GetStack().Last()
	    hsumm[h][m].Draw('SAME')
	    leg[h][m].Draw('same')
	    ratioPad[h][m].cd()
	    htest[h][m] = hsumm[h][m].Clone()
	    htest[h][m].SetLineColor(kBlack)
	    htest[h][m].Divide(hsum[h][m])
	    htest[h][m].GetYaxis().SetLabelSize(0.12)
	    htest[h][m].GetYaxis().SetTitleSize(0.1)
	    htest[h][m].GetYaxis().SetTitleOffset(0.55)
	    htest[h][m].GetXaxis().SetLabelSize(0.12)
	    htest[h][m].GetXaxis().SetTitleSize(0.1)
	    htest[h][m].GetXaxis().SetTitle('p_{T} (GeV/c)')
	    htest[h][m].GetYaxis().SetRangeUser(0.005,htest[h][m].GetMaximum()*1.1)
	    htest[h][m].GetYaxis().SetNdivisions(305)
	    htest[h][m].GetYaxis().SetTitle("Tight/Base   ")
	    htest[h][m].Draw()


	c12.Update()
    c12.SaveAs("Tight_Base_MC_Hist_DM_"+era+"_"+args.region+"_"+str(args.workingPoint)+".pdf")
    c12.SaveAs("Tight_Base_MC_Hist_DM_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")

###############################################3
if True :
    #c12 = TCanvas('c12','Tight/Base (MC)',50,50,1200,600)
    c12 = TCanvas('c12','Tight/Base (Data)',50,50,1300,800)
    c12.SetFillColor(0)
    c12.SetBorderMode(0)
    c12.SetFrameFillStyle(0)
    c12.SetFrameBorderMode(0)

    c12.SetLeftMargin(L/W)
    c12.SetRightMargin(R/W)
    c12.SetTopMargin(T/H)
    c12.SetBottomMargin(B/H)

    c12.Divide(4,2)
    leg = {}
    hsBasePrompt, hsTightPrompt = {}, {}
    ratioPad, plotPad= {}, {}
    hsum, hsumm= {}, {}
    htest= {}

    for i, h in enumerate(hList) :
        c12.cd(i+1)
	ratioPad[h] = TPad("pad2","",0.0,0.0,1.0,0.29)
	plotPad[h] = TPad("pad1","",0.0016,0.291,1.0,1.0)
	plotPad[h].SetTicks(0,0)
	plotPad[h].SetLeftMargin(L/W)
	plotPad[h].SetRightMargin(R/W)
	plotPad[h].SetTopMargin(T/H)
	plotPad[h].SetBottomMargin(B_ratio/H)
	plotPad[h].SetFillColor(0)
	plotPad[h].SetBottomMargin(0.05)

	ratioPad[h].SetLeftMargin  (L/W)
	ratioPad[h].SetRightMargin (R/W)
	ratioPad[h].SetTopMargin   (T_ratio/H)
	ratioPad[h].SetTopMargin   (0.007)
	ratioPad[h].SetBottomMargin(B_ratio_label/H)
	ratioPad[h].SetGridy(1)
	ratioPad[h].SetFillColor(4000)


    for i, h in enumerate(hList) :
	c12.cd(i+1)
	#gPad.SetLogy()
        plotPad[h].Draw()
        ratioPad[h].Draw()
	plotPad[h].SetLogy()
        plotPad[h].cd()
        hsBasePrompt[h] = THStack("hsBasePrompt","")
        hsTightPrompt[h] = THStack("hsTightPrompt","")
        leg[h] = TLegend(0.43,0.73,0.96,0.96,h)
	leg[h].SetTextSize(0.045)
	title="Prompt Base (MC)"
	leg[h].AddEntry(hBasePrompt[group][h],title,"l")
	leg[h].AddEntry(hTightPrompt[group][h],"Prompt Tight (MC)","L")
        for group in groups :
	    hBasePrompt[group][h].SetLineWidth(2)
	    hBasePrompt[group][h].SetLineColor(kBlue)
	    hBasePrompt[group][h].GetXaxis().SetTitle('')
	    hBasePrompt[group][h].GetXaxis().SetLabelSize(0.05)
	    hBasePrompt[group][h].GetXaxis().SetTitleSize(0.05)
	    hBasePrompt[group][h].SetMinimum(0.01)
	    hBasePrompt[group][h].SetMaximum(hBasePrompt[group][h].GetMaximum()*500)


	    hBasePrompt[group][h].GetYaxis().SetTitle('Counts') 
	    hBasePrompt[group][h].GetYaxis().SetLabelSize(0.05)
	    hBasePrompt[group][h].GetYaxis().SetTitleSize(0.05)

	    hsBasePrompt[h].Add(hBasePrompt[group][h])

	    hTightPrompt[group][h].SetLineWidth(2)
	    hTightPrompt[group][h].SetLineColor(kRed)
	    hTightPrompt[group][h].SetMinimum(0.01)

	    hsTightPrompt[h].Add(hTightPrompt[group][h])


	hsum[h]=hsBasePrompt[h].GetStack().Last()
	hsum[h].SetMinimum(0.01)
	hsum[h].SetMaximum(hsum[h].GetMaximum()*50)
	hsum[h].Draw()
	hsumm[h]=hsTightPrompt[h].GetStack().Last()
	hsumm[h].Draw('SAME')
	leg[h].Draw()

        ratioPad[h].cd()
        htest[h] = hsumm[h].Clone()
        htest[h].SetLineColor(kBlack)
        htest[h].Divide(hsum[h])
        htest[h].GetYaxis().SetLabelSize(0.12)
        htest[h].GetYaxis().SetTitleSize(0.1)
        htest[h].GetYaxis().SetTitleOffset(0.55)
        htest[h].GetXaxis().SetLabelSize(0.12)
        htest[h].GetXaxis().SetTitleSize(0.1)
        htest[h].GetXaxis().SetTitle('p_{T} (GeV/c)')
        htest[h].GetYaxis().SetRangeUser(0.005,htest[h].GetMaximum()*1.1)
        htest[h].GetYaxis().SetNdivisions(305)
        htest[h].GetYaxis().SetTitle("Tight/Base   ")
        htest[h].Draw()



	c12.Update()
    c12.SaveAs("Tight_Base_MC_Hist_"+era+"_"+args.region+"_"+str(args.workingPoint)+".pdf")
    c12.SaveAs("Tight_Base_MC_Hist_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")

'''

        for group in groups :
	    hTight[h].Draw()
	    hTightPrompt[group][h].SetLineWidth(2)
	    hTightPrompt[group][h].SetLineColor(kRed)
	    hTightPrompt[group][h].Draw('SAME')
	    hsBaseTight.Add(hTightPrompt[group][h])
	    title="Prompt Tight (MC) {0:s}".format(group)
	    leg[h].AddEntry(hTightPrompt[group][h],title,"L")
	    leg[h].Draw()

	hsumm=hsBaseTight.GetStack().Last()
	hsumm.Draw('SAME')
	c13.Update()
    c13.SaveAs("Tight_Base_MC_Hist_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")
'''

# Cases
#  1) tight/base
#  2) tightPrompt/basePrompt
#  3) tightPrompt/tight
#  4) (tight-tightPrompt)/(base-basePrompt)

# plot data and MC prompt rates

if True :
    c1 = TCanvas('c1','Tight/Base (Data)',50,50,W,H)
    c1.SetFillColor(0)
    c1.SetBorderMode(0)
    c1.SetFrameFillStyle(0)
    c1.SetFrameBorderMode(0)

    c1.SetLeftMargin(L/W)
    c1.SetRightMargin(R/W)
    c1.SetTopMargin(T/H)
    c1.SetBottomMargin(B/H)

    c1.Divide(4,2)
    lTeX = {}
    hTight_2 = {}
    xMin, xMax, yMin, yMax = 0., 100., 0., 0.25
    for i, h in enumerate(hList) :
        c1.cd(i+1)
        hTight_2[h] = hTight[h].Clone()
        hTight_2[h].SetLineColor(kBlack) 
        #hTight_2[h].Sumw2()
        hTight_2[h].Divide(hBase[h])
        hTight_2[h].GetXaxis().SetRangeUser(xMin,xMax)
        hTight_2[h].SetMinimum(yMin)
        hTight_2[h].SetMaximum(yMax)
        hTight_2[h].SetLineWidth(2)
        hTight_2[h].SetMarkerStyle(20)
        hTight_2[h].SetMarkerSize(1.0)
        hTight_2[h].SetMarkerColor(kRed)
        hTight_2[h].GetXaxis().SetTitle('p_{T} (GeV/c)')
        hTight_2[h].GetXaxis().SetLabelSize(0.05)
        hTight_2[h].GetXaxis().SetTitleSize(0.05)
        hTight_2[h].GetYaxis().SetTitle('Tight (data)/Base (data)')
        hTight_2[h].GetYaxis().SetLabelSize(0.05)
        hTight_2[h].GetYaxis().SetTitleSize(0.05)
        hTight_2[h].Draw()
        lTeX[h] = TLatex(0.8*xMax,0.9*yMax,h)
        lTeX[h].SetTextSize(0.06) 
        lTeX[h].Draw()
        c1.Update()
    c1.SaveAs("Tight_Base_Data_ratio_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")

if True :
    c2 = TCanvas('c2','Prompt Tight/Prompt Base (MC)',50,50,W,H)
    c2.SetFillColor(0)
    c2.SetBorderMode(0)
    c2.SetFrameFillStyle(0)
    c2.SetFrameBorderMode(0)

    c2.SetLeftMargin(L/W)
    c2.SetRightMargin(R/W)
    c2.SetTopMargin(T/H)
    c2.SetBottomMargin(B/H)

    c2.Divide(4,2)
    lTeX = {}
    xMin, xMax, yMin, yMax = 0., 100., 0., 1.0
    hTightPrompt_2 = {}
    hBasePrompt_2 = {}

    hTightPrompt_2 = {}

    for i, h in enumerate(hList) :
        hsBasePrompt_2 = THStack("hsBasePrompt_2","")
        hsBaseTight_2 = THStack("hsTightPrompt_2","")
        hTightPrompt_2[h] = {}
        hBasePrompt_2[h] = {}
        c2.cd(i+1)

        for group in groups :
	    hTightPrompt_2[h][group] = hTightPrompt[group][h].Clone()
	    hTightPrompt_2[h][group].SetLineColor(kBlack) 
	    #hTightPrompt_2[h][group].Sumw2()

            hBasePrompt_2[h][group] = hBasePrompt[group][h].Clone()
	    #print 'try', hBasePrompt[group][h].GetSumOfWeights(), hTightPrompt[group][h].GetSumOfWeights(), group, h, hBasePrompt[group][h].GetName()
	    #hBasePrompt_2[h][group].Sumw2()
	    hsBasePrompt_2.Add(hBasePrompt[group][h])


	    hTightPrompt_2[h][group].GetXaxis().SetRangeUser(xMin,xMax)
	    hTightPrompt_2[h][group].SetMinimum(yMin)
	    hTightPrompt_2[h][group].SetMaximum(yMax)
	    hTightPrompt_2[h][group].SetLineWidth(2)
	    hTightPrompt_2[h][group].SetMarkerStyle(20)
	    hTightPrompt_2[h][group].SetMarkerSize(1.0)
	    hTightPrompt_2[h][group].SetMarkerColor(kRed)
	    hTightPrompt_2[h][group].GetXaxis().SetTitle('p_{T} (GeV/c)')
	    hTightPrompt_2[h][group].GetXaxis().SetLabelSize(0.05)
	    hTightPrompt_2[h][group].GetXaxis().SetTitleSize(0.05)
	    hTightPrompt_2[h][group].GetYaxis().SetTitle('Tight Prompt (MC)/Base Prompt (MC)')
	    hTightPrompt_2[h][group].GetYaxis().SetLabelSize(0.05)
	    hTightPrompt_2[h][group].GetYaxis().SetTitleSize(0.05)

	    hsBaseTight_2.Add(hTightPrompt_2[h][group])
	    hsBasePrompt_2.Add(hBasePrompt_2[h][group])


        hsum=hsBaseTight_2.GetStack().Last()
        hsumm=hsBasePrompt_2.GetStack().Last()
	hsum.Divide(hsumm)
	print hsum.GetSumOfWeights()
	hsum.GetXaxis().SetRangeUser(xMin,xMax)
	hsum.SetMinimum(yMin)
	hsum.SetMaximum(yMax)
	hsum.SetLineWidth(2)
	hsum.SetMarkerStyle(20)
	hsum.SetMarkerSize(1.0)
	hsum.SetMarkerColor(kBlue)
	hsum.GetXaxis().SetLabelSize(0.05)
	hsum.GetXaxis().SetTitleSize(0.05)

if True :
    c3 = TCanvas('c3','Prompt Tight/Prompt Base (MC)',50,50,W,H)
    c3.SetFillColor(0)
    c3.SetBorderMode(0)
    c3.SetFrameFillStyle(0)
    c3.SetFrameBorderMode(0)
    
    c3.SetLeftMargin(L/W)
    c3.SetRightMargin(R/W)
    c3.SetTopMargin(T/H)
    c3.SetBottomMargin(B/H)

    c3.Divide(4,2)
    lTeX = {}
    xMin, xMax, yMin, yMax = 0., 100., 0., 0.5
    hTightPrompt_3 = {} 
    for i, h in enumerate(hList) :
        hTightPrompt_3[h] = {} 
        hsBaseTight_3 = THStack("hsTightPrompt_3","")
	c3.cd(i+1)

	for group in groups :
	    hTightPrompt_3[h][group]= hTightPrompt[group][h].Clone()
	    hTightPrompt_3[h][group].SetLineColor(kBlack)
	    #hTightPrompt_3[h][group].Sumw2()
	    hsBaseTight_3.Add(hTightPrompt_3[h][group])

	hsum = hsBaseTight_3.GetStack().Last()
	hsum.Divide(hTight[h])
	hsum.GetXaxis().SetRangeUser(xMin,xMax)
	hsum.SetMinimum(yMin)
	hsum.SetMaximum(yMax)
	hsum.SetLineWidth(2)
	hsum.SetMarkerStyle(20)
	hsum.SetMarkerSize(1.0)
	hsum.SetMarkerColor(kRed)
	hsum.GetXaxis().SetTitle('p_{T} (GeV/c)')
	hsum.GetXaxis().SetLabelSize(0.05)
	hsum.GetXaxis().SetTitleSize(0.05)
	hsum.GetYaxis().SetTitle('Prompt Tight (MC)/ Tight (data)')
	hsum.GetYaxis().SetLabelSize(0.05)
	hsum.GetYaxis().SetTitleSize(0.05)


	lTeX[h] = TLatex(0.8*xMax,0.9*yMax,h)
	lTeX[h].SetTextSize(0.06) 
	hsum.Draw()
	lTeX[h].Draw()
	c3.Update()
	
    c3.SaveAs("Tight_MC_Tight_Data_ratio_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")


c4 = TCanvas('c4','(Tight - Prompt Tight)/(Base - Prompt Base)',50,50,W,H)
c4.SetFillColor(0)
c4.SetBorderMode(0)
c4.SetFrameFillStyle(0)
c4.SetFrameBorderMode(0)

c4.SetLeftMargin(L/W)
c4.SetRightMargin(R/W)
c4.SetTopMargin(T/H)
c4.SetBottomMargin(B/H)

#gStyle.SetStatY(0.95)
#gStyle.SetStatX(1.1)
#gStyle.SetStatW(0.15)
#gStyle.SetStatH(0.7) 

c4.Divide(4,2)
lTeX, lTex1, lTex2, fit0 = {}, {}, {}, {}
hNum, hDen = {}, {}
xMin, xMax, yMin, yMax = 0., 100., 0., 0.5
if True : 
    for i, h in enumerate(hList) :
	gStyle.SetOptFit(0)
	c4.cd(i+1)

        
	hNum[h] = hTight[h].Clone()
	hNum[h].SetLineColor(kBlack)
	hDen[h] = hBase[h].Clone()
        
	for group in groups:
	    print ''
	    print 'subtracting from Tight prompt',  hNum[h].GetSumOfWeights(), hNum[h].GetSumOfWeights()-hTightPrompt[group][h].GetSumOfWeights(), group, h,  hTightPrompt[group][h].GetSumOfWeights(), hNum[h].GetName(), hTightPrompt[group][h].GetName()
	    print 'subtracting from Base prompt',  hDen[h].GetSumOfWeights(), hDen[h].GetSumOfWeights()-hBasePrompt[group][h].GetSumOfWeights(), group, h, hBasePrompt[group][h].GetSumOfWeights(), hDen[h].GetName(), hBasePrompt[group][h].GetName()
	    hNum[h].Add(hTightPrompt[group][h],-1.)
	    hDen[h].Add(hBasePrompt[group][h],-1.)
            #print 'channel', h, group, 'base', hNum[h].GetSumOfWeights(), 'Tight', hDen[h].GetSumOfWeights(), hNum[h].GetSumOfWeights()/hDen[h].GetSumOfWeights()
        
	hNum[h].Divide(hDen[h])
	#hNum[h].SetMaximum(hNum[h].GetMaximum()+0.2)
	hNum[h].GetXaxis().SetRangeUser(xMin,xMax)
	hNum[h].SetMinimum(yMin)
	hNum[h].SetMaximum(yMax)
	hNum[h].SetLineWidth(2)
	hNum[h].SetMarkerStyle(20)
	hNum[h].SetMarkerSize(1.0)
	hNum[h].SetMarkerColor(kRed)
	hNum[h].GetXaxis().SetTitle('p_{T} (GeV/c)')
	hNum[h].GetXaxis().SetLabelSize(0.05)
	hNum[h].GetXaxis().SetTitleSize(0.05)
	hNum[h].GetYaxis().SetTitle('(Tight - Prompt Tight)/(Base - Prompt Base)')
	hNum[h].GetYaxis().SetLabelSize(0.05)
	hNum[h].GetYaxis().SetTitleSize(0.05)
	hNum[h].Draw()
	lTeX[h] = TLatex(0.8*xMax,0.8*yMax,h)
	lTeX[h].SetTextSize(0.06) 
	lTeX[h].Draw()
	fitName = "f{0:s}".format(h)
	fit0[h] = TF1(fitName,"pol0",15.,100.)
	hNum[h].Fit(fitName,"R")
	lTex1[h]= TLatex(0.1*xMax,0.9*yMax,"Avg={0:.4f} +/- {1:.4f}".format(fit0[h].GetParameter(0),fit0[h].GetParError(0)))
	lTex1[h].Draw()
	lTex2[h]= TLatex(0.1*xMax,0.8*yMax,"chi2/DOF = {0:.2f} / {1:d}".format(fit0[h].GetChisquare(),fit0[h].GetNDF()))
	lTex2[h].Draw()
	c4.Update()
	
    c4.Draw()
    c4.SaveAs("Corrected_Fake_"+era+"_"+args.region+"_"+str(args.workingPoint)+".pdf")
    c4.SaveAs("Corrected_Fake_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")




if True :
    c12 = TCanvas('c12','Tight composition (MC)',90,90,1200,600)
    c12.SetFillColor(0)
    c12.SetBorderMode(0)
    c12.SetFrameFillStyle(0)
    c12.SetFrameBorderMode(0)

    c12.SetLeftMargin(L/W)
    c12.SetRightMargin(R/W)
    c12.SetTopMargin(T/H)
    c12.SetBottomMargin(B/H)

    c12.Divide(4,2)

    c12a = TCanvas('c12a','Base composition (MC)',90,90,1200,600)
    c12a.SetFillColor(0)
    c12a.SetBorderMode(0)
    c12a.SetFrameFillStyle(0)
    c12a.SetFrameBorderMode(0)

    c12a.SetLeftMargin(L/W)
    c12a.SetRightMargin(R/W)
    c12a.SetTopMargin(T/H)
    c12a.SetBottomMargin(B/H)
    c12a.Divide(4,2)

    leg = {}
    xR=0.65   #legend parameters
    xR=0.2    #legend parameters
    #hsBasePrompt, hsBaseTight = {}, {}
    hsBasePrompt, hsTightPrompt= {}, {}
    for i, h in enumerate(hList) :
        hsBasePrompt[h] = THStack("hsBasePrompt","")
        hsTightPrompt[h] = THStack("hsTightPrompt","")
	#leg[h] = TLegend(0.43,0.63,0.96,0.96,h)
        leg[h] = TLegend(xR+0.2,0.6,xR+0.75,0.9,h)
        leg[h].SetNColumns(2)
        for group in groups :
	    applyStyle(hBasePrompt[group][h],colors[group],1,1001)
	    hBasePrompt[group][h].GetXaxis().SetTitle('p_{T} (GeV/c)')
	    hBasePrompt[group][h].GetXaxis().SetLabelSize(0.05)
	    hBasePrompt[group][h].GetXaxis().SetTitleSize(0.05)
	    title="Prompt Base (MC) {0:s}".format(group)
	    c12a.SetTitle(title)

	    hBasePrompt[group][h].GetYaxis().SetTitle('Counts') 
	    hBasePrompt[group][h].GetYaxis().SetLabelSize(0.05)
	    hBasePrompt[group][h].GetYaxis().SetTitleSize(0.05)

	    hsBasePrompt[h].Add(hBasePrompt[group][h])

	    applyStyle(hTightPrompt[group][h],colors[group],1,1001)


	    hTightPrompt[group][h].GetXaxis().SetTitle('p_{T} (GeV/c)')
	    hTightPrompt[group][h].GetXaxis().SetLabelSize(0.05)
	    hTightPrompt[group][h].GetXaxis().SetTitleSize(0.05)
	    title="Prompt Tight (MC) {0:s}".format(group)
	    c12.SetTitle(title)

	    hTightPrompt[group][h].GetYaxis().SetTitle('Counts') 
	    hTightPrompt[group][h].GetYaxis().SetLabelSize(0.05)
	    hTightPrompt[group][h].GetYaxis().SetTitleSize(0.05)

	    hsTightPrompt[h].Add(hTightPrompt[group][h])
            hl = '{0:s}'.format(group)
	    leg[h].AddEntry(hTightPrompt[group][h], hl,"f")

	c12a.cd(i+1)
	hsum=hsBasePrompt[h].GetStack().Last()
        hsum.SetMaximum(hsum.GetMaximum()*2.5)
	hsum.Draw()
	hsBasePrompt[h].Draw('hist same')
	leg[h].Draw('same')
	c12a.Update()

	c12.cd(i+1)
	hsumm=hsTightPrompt[h].GetStack().Last()
        hsumm.SetMaximum(hsumm.GetMaximum()*2.5)
	hsumm.Draw()
	hsTightPrompt[h].Draw('hist same')
	leg[h].Draw('same')
	c12.Update()

    #CMS_lumi.CMS_lumi(c12, iPeriod, 11)
    lTex1 = TLatex(120.,0.97,'Preliminary {0:d}'.format(args.year))
    lTex1.SetTextSize(0.04)
    c12.cd()
    lTex1.Draw("same")
    c12a.cd()
    lTex1.Draw("same")

    #CMS_lumi.CMS_lumi(c12a, iPeriod, 11)
    c12.SaveAs("Tight_MC_composition_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")
    c12a.SaveAs("Base_MC_composition_"+era+"_"+args.region+"_"+str(args.workingPoint)+".png")



