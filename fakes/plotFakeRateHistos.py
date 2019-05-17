#
# estimate fake rate for irreducilble backgrounds 
#

from ROOT import TFile, TTree, TH1D, TCanvas, TLorentzVector, TLatex, kRed, kBlue, kBlack, TLegend, TF1, gStyle
import tdrstyle 

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    parser.add_argument("-f","--inFileName",default='./FakeRates.root',help="File to be analyzed.")
    parser.add_argument("-y","--year",default=2017,type=int,help="Year for data.")
    return parser.parse_args()

args = getArgs()
cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt', 7:'et', 8:'mt', 9:'tt' }
hList = ['e_et','m_mt','t_et','t_mt','t1_tt','t2_tt']

tdrstyle.setTDRStyle()

# size info
H, W, H_ref, W_ref = 600, 1000, 600, 100
# references for T, B, L, R
T, B, L, R = 0.08*H_ref, 0.12*H_ref, 0.16*W_ref, 0.04*W_ref

# Read in fake-rate histograms and use them to calculate the fake rate factors

f = TFile(args.inFileName)
hBase, hTight, hBasePrompt, hTightPrompt = {}, {}, {}, {}
for h in hList :
    hName = "{0:s}Base".format(h)
    hBase[h] = f.Get(hName) 
    #print("hName={0:s} hBase[{1:s}]={2:s}".format(hName,h,str(hBase[h])))
    hTight[h] = f.Get("{0:s}Tight".format(h))
    hBasePrompt[h] = f.Get("{0:s}BasePrompt".format(h)) 
    hTightPrompt[h] = f.Get("{0:s}TightPrompt".format(h)) 

# plot raw histograms 

if True :
    c11 = TCanvas('c11','Tight/Base (Data)',50,50,W,H)
    c11.SetFillColor(0)
    c11.SetBorderMode(0)
    c11.SetFrameFillStyle(0)
    c11.SetFrameBorderMode(0)

    c11.SetLeftMargin(L/W)
    c11.SetRightMargin(R/W)
    c11.SetTopMargin(T/H)
    c11.SetBottomMargin(B/H)

    c11.Divide(3,2)
    leg = {}
    for i, h in enumerate(hList) :
        c11.cd(i+1)
        hBase[h].SetLineWidth(2)
        hBase[h].SetLineColor(kBlue)
        hBase[h].GetXaxis().SetTitle('p_t (GeV/c)')
        hBase[h].GetXaxis().SetLabelSize(0.05)
        hBase[h].GetXaxis().SetTitleSize(0.05)
        yMax = hBase[h].GetMaximum()
        leg[h] = TLegend(0.63,0.73,0.96,0.96,h)
        leg[h].AddEntry(hBase[h],"Base (data)","L")
        hBase[h].GetYaxis().SetTitle('Counts')
        hBase[h].GetYaxis().SetLabelSize(0.05)
        hBase[h].GetYaxis().SetTitleSize(0.05)
        hBase[h].Draw()
        hTight[h].SetLineWidth(2)
        hTight[h].SetLineColor(kRed)
        #hTight[h].Scale(5.)
        hTight[h].Draw('SAME')
        leg[h].AddEntry(hTight[h],"Tight x5 (data)","L")
        leg[h].Draw()
        c11.Update()
    
    c11.Draw()
    c11.SaveAs("Tight_Base_Data_Hist.png")
    raw_input()

if True :
    c12 = TCanvas('c12','Tight/Base (MC)',50,50,W,H)
    c12.SetFillColor(0)
    c12.SetBorderMode(0)
    c12.SetFrameFillStyle(0)
    c12.SetFrameBorderMode(0)

    c12.SetLeftMargin(L/W)
    c12.SetRightMargin(R/W)
    c12.SetTopMargin(T/H)
    c12.SetBottomMargin(B/H)

    c12.Divide(3,2)
    leg = {}
    for i, h in enumerate(hList) :
        c12.cd(i+1)
        hBasePrompt[h].SetLineWidth(2)
        hBasePrompt[h].SetLineColor(kBlue)
        hBasePrompt[h].GetXaxis().SetTitle('p_t (GeV/c)')
        hBasePrompt[h].GetXaxis().SetLabelSize(0.05)
        hBasePrompt[h].GetXaxis().SetTitleSize(0.05)
        yMax = hBasePrompt[h].GetMaximum()
        leg[h] = TLegend(0.43,0.63,0.96,0.96,h)
        leg[h].AddEntry(hBasePrompt[h],"Prompt Base (MC)","L")
        hBasePrompt[h].GetYaxis().SetTitle('Counts') 
        hBasePrompt[h].GetYaxis().SetLabelSize(0.05)
        hBasePrompt[h].GetYaxis().SetTitleSize(0.05)
        hBasePrompt[h].Draw()
        hTightPrompt[h].SetLineWidth(2)
        hTightPrompt[h].SetLineColor(kRed)
        hTightPrompt[h].Draw('SAME')
        leg[h].AddEntry(hTightPrompt[h],"Tight (data)","L")
        leg[h].Draw()
        c12.Update()
    
    c12.Draw()
    c12.SaveAs("Tight_Base_MC_Hist.png")
    raw_input()

if True :
    c13 = TCanvas('c13','Prompt Tight (MC) / Tight (Data)',50,50,W,H)
    c13.SetFillColor(0)
    c13.SetBorderMode(0)
    c13.SetFrameFillStyle(0)
    c13.SetFrameBorderMode(0)

    c13.SetLeftMargin(L/W)
    c13.SetRightMargin(R/W)
    c13.SetTopMargin(T/H)
    c13.SetBottomMargin(B/H)

    c13.Divide(3,2)
    leg = {}
    for i, h in enumerate(hList) :
        c13.cd(i+1)
        hTight[h].SetLineWidth(2)
        hTight[h].SetLineColor(kBlue)
        hTight[h].GetXaxis().SetTitle('p_t (GeV/c)')
        hTight[h].GetXaxis().SetLabelSize(0.05)
        hTight[h].GetXaxis().SetTitleSize(0.05)
        yMax = hTight[h].GetMaximum()
        leg[h] = TLegend(0.43,0.63,0.96,0.96,h)
        leg[h].AddEntry(hTight[h],"Tight (data)","L")
        hTight[h].GetYaxis().SetTitle('Counts') 
        hTight[h].GetYaxis().SetLabelSize(0.05)
        hTight[h].GetYaxis().SetTitleSize(0.05)
        hTight[h].Draw()
        hTightPrompt[h].SetLineWidth(2)
        hTightPrompt[h].SetLineColor(kRed)
        hTightPrompt[h].Draw('SAME')
        leg[h].AddEntry(hTightPrompt[h],"Prompt Tight (MC)","L")
        leg[h].Draw()
        c13.Update()
    
    c13.Draw()
    c13.SaveAs("Tight_Base_MC_Hist.png")
    raw_input()


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

    c1.Divide(3,2)
    lTeX = {}
    hTight_2 = {}
    xMin, xMax, yMin, yMax = 0., 100., 0., 0.25
    for i, h in enumerate(hList) :
        c1.cd(i+1)
        hTight_2[h] = hTight[h].Clone()
        hTight_2[h].SetLineColor(kBlack) 
        hTight_2[h].Sumw2()
        hTight_2[h].Divide(hBase[h])
        hTight_2[h].GetXaxis().SetRangeUser(xMin,xMax)
        hTight_2[h].SetMinimum(yMin)
        hTight_2[h].SetMaximum(yMax)
        hTight_2[h].SetLineWidth(2)
        hTight_2[h].SetMarkerStyle(20)
        hTight_2[h].SetMarkerSize(1.0)
        hTight_2[h].SetMarkerColor(kRed)
        hTight_2[h].GetXaxis().SetTitle('p_t (GeV/c)')
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
    
    c1.Draw()
    c1.SaveAs("Tight_Base_Data.png")
    raw_input()

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

    c2.Divide(3,2)
    lTeX = {}
    xMin, xMax, yMin, yMax = 0., 100., 0., 1.0
    hTightPrompt_2 = {}
    for i, h in enumerate(hList) :
        c2.cd(i+1)
        hTightPrompt_2[h] = hTightPrompt[h].Clone()
        hTightPrompt_2[h].SetLineColor(kBlack) 
        hTightPrompt_2[h].Sumw2()
        hTightPrompt_2[h].Divide(hBasePrompt[h])
        hTightPrompt_2[h].GetXaxis().SetRangeUser(xMin,xMax)
        hTightPrompt_2[h].SetMinimum(yMin)
        hTightPrompt_2[h].SetMaximum(yMax)
        hTightPrompt_2[h].SetLineWidth(2)
        hTightPrompt_2[h].SetMarkerStyle(20)
        hTightPrompt_2[h].SetMarkerSize(1.0)
        hTightPrompt_2[h].SetMarkerColor(kRed)
        hTightPrompt_2[h].GetXaxis().SetTitle('p_t (GeV/c)')
        hTightPrompt_2[h].GetXaxis().SetLabelSize(0.05)
        hTightPrompt_2[h].GetXaxis().SetTitleSize(0.05)
        hTightPrompt_2[h].GetYaxis().SetTitle('Tight Prompt (MC)/Base Prompt (MC)')
        hTightPrompt_2[h].GetYaxis().SetLabelSize(0.05)
        hTightPrompt_2[h].GetYaxis().SetTitleSize(0.05)
        hTightPrompt_2[h].Draw()
        lTeX[h] = TLatex(0.8*xMax,0.9*yMax,h)
        lTeX[h].SetTextSize(0.06) 
        lTeX[h].Draw()
        c2.Update()
    
    c2.Draw()
    c2.SaveAs("Tight_Base_MC.png")
    raw_input()

if True :
    c3 = TCanvas('c3','Prompt Tight (MC)/ Tight (data)',50,50,W,H)
    c3.SetFillColor(0)
    c3.SetBorderMode(0)
    c3.SetFrameFillStyle(0)
    c3.SetFrameBorderMode(0)
    
    c3.SetLeftMargin(L/W)
    c3.SetRightMargin(R/W)
    c3.SetTopMargin(T/H)
    c3.SetBottomMargin(B/H)

    c3.Divide(3,2)
    lTeX = {}
    xMin, xMax, yMin, yMax = 0., 100., 0., 0.5
    hTightPrompt_3 = {} 
    for i, h in enumerate(hList) :
        c3.cd(i+1)
        hTightPrompt_3[h] = hTightPrompt[h].Clone()
        hTightPrompt_3[h].SetLineColor(kBlack)
        hTightPrompt_3[h].Sumw2()
        hTightPrompt_3[h].Divide(hTight[h])
        hTightPrompt_3[h].GetXaxis().SetRangeUser(xMin,xMax)
        hTightPrompt_3[h].SetMinimum(yMin)
        hTightPrompt_3[h].SetMaximum(yMax)
        hTightPrompt_3[h].SetLineWidth(2)
        hTightPrompt_3[h].SetMarkerStyle(20)
        hTightPrompt_3[h].SetMarkerSize(1.0)
        hTightPrompt_3[h].SetMarkerColor(kRed)
        hTightPrompt_3[h].GetXaxis().SetTitle('p_t (GeV/c)')
        hTightPrompt_3[h].GetXaxis().SetLabelSize(0.05)
        hTightPrompt_3[h].GetXaxis().SetTitleSize(0.05)
        hTightPrompt_3[h].GetYaxis().SetTitle('Prompt Tight (MC)/ Tight (data)')
        hTightPrompt_3[h].GetYaxis().SetLabelSize(0.05)
        hTightPrompt_3[h].GetYaxis().SetTitleSize(0.05)
        hTightPrompt_3[h].Draw()
        lTeX[h] = TLatex(0.8*xMax,0.9*yMax,h)
        lTeX[h].SetTextSize(0.06) 
        lTeX[h].Draw()
        c3.Update()
    
    c3.Draw()
    c3.SaveAs("Tight_MC_Tight_Data.png")
    raw_input()


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

c4.Divide(3,2)
lTeX, lTex1, lTex2, fit0 = {}, {}, {}, {}
hNum, hDen = {}, {}
xMin, xMax, yMin, yMax = 0., 100., 0., 0.25
for i, h in enumerate(hList) :
    gStyle.SetOptFit(0)
    c4.cd(i+1)
    hNum[h] = hTight[h].Clone()
    hNum[h].SetLineColor(kBlack)
    hNum[h].Add(hTightPrompt[h],-1.) 
    hNum[h].Sumw2()
    hDen[h] = hBase[h].Clone()
    hDen[h].Add(hBasePrompt[h],-1.)
    hNum[h].Divide(hDen[h])
    hNum[h].GetXaxis().SetRangeUser(xMin,xMax)
    hNum[h].SetMinimum(yMin)
    hNum[h].SetMaximum(yMax)
    hNum[h].SetLineWidth(2)
    hNum[h].SetMarkerStyle(20)
    hNum[h].SetMarkerSize(1.0)
    hNum[h].SetMarkerColor(kRed)
    hNum[h].GetXaxis().SetTitle('p_t (GeV/c)')
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
    fit0[h] = TF1(fitName,"pol0",15.,70.)
    hNum[h].Fit(fitName,"R")
    lTex1[h]= TLatex(0.1*xMax,0.9*yMax,"Avg={0:.4f} +/- {1:.4f}".format(fit0[h].GetParameter(0),fit0[h].GetParError(0)))
    lTex1[h].Draw()
    lTex2[h]= TLatex(0.1*xMax,0.8*yMax,"chi2/DOF = {0:.2f} / {1:d}".format(fit0[h].GetChisquare(),fit0[h].GetNDF()))
    lTex2[h].Draw()
    c4.Update()
    
c4.Draw()
c4.SaveAs("Corrected_Fake.png")
raw_input()





    



