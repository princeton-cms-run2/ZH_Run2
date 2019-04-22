import tdrstyle
import CMS_lumi
from ROOT import TCanvas, TH1D, TH1F, THStack, TFile, TPad, TLegend 
from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure

def applyStyle( h, fill, line, fillStyle) :
    h.SetFillColor(fill)
    h.SetLineColor(line)
    h.SetFillStyle(fillStyle)
    h.SetLineWidth(2)

def applySignalStyle(h) :
    h.SetFillStyle(0)
    h.SetLineWidth(3)
    h.SetLineColor(kBlue+2)
    h.SetLineStyle(2)

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


        
def makeDiTauStack(outDir,inFile,rootDir,s,labelX, units = "GeV",left=False, channel = "",
                   json = "Golden", log = False, dndm = False, doRatio = False) :

    cat = 'mmtt'
    tdrstyle.setTDRStyle()

    writeExtraText = True       # if extra text
    extraText  = "Preliminary"  # default extra text is "Preliminary"
    lumi_sqrtS = "13 TeV"
    if json=="Golden" : lumi_13TeV = channel+"    41.8 fb^{-1}, 2017"
    iPeriod = 4    # 1=7TeV, 2=8TeV, 3=7+8TeV, 7=7+8+13TeV 

    xR=0.65   #legend parameters
    xR=0.2    #legend parameters
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

    c = TCanvas('c1','c1',50,50,W,H)
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
    
    ratioPad = TPad("pad2","",0.0,0.0,1.0,0.29)
    plotPad = TPad("pad1","",0.0016,0.291,1.0,1.0)
    if doRatio :
	plotPad.SetTicks(0,0)
	plotPad.SetLeftMargin(L/W)
	plotPad.SetRightMargin(R/W)
	plotPad.SetTopMargin(T/H)
	plotPad.SetBottomMargin(B_ratio/H) 
	plotPad.SetFillColor(0)
	plotPad.SetBottomMargin(0)

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
	
    plotPad.Draw()
    plotPad.cd()

    print("In makeStack inFile={0:s}".format(inFile))
    f = TFile(inFile)

    groups = ['data','Reducible','Rare','ZZ4L','Signal']
    histo = {}
    colors = {'data':0,'Reducible':kMagenta-10,'Rare':kBlue-8,'ZZ4L':kAzure-9,'Signal':kOrange-4}
    hs = THStack("hs","")
    for group in groups :
        histo[group] = f.Get("h{0:s}_{1:s}_Mtt".format(group,cat))
        #print("In makeStack(): histo={0:s} type(histo)={1:s}".format(str(histo[group]),type(histo[group])))
        if dndm : convertToDNDM(histo[group])
        if group == 'data' :
            applyDATAStyle(histo[group])
        elif group == 'Signal' :
	    applySignalStyle(histo[group])
        else :
            applyStyle(histo[group],colors[group],1,1001)
        if group != 'data' : hs.Add(histo[group]) 


    hMax= 1.2*max(histo['data'].GetMaximum(),hs.GetMaximum())
    print("hMax={0:f}".format(hMax))
    hs.SetMaximum(hMax)
    hs.Draw("HIST")
    histo['data'].Draw("e,SAME")

    
    if doRatio :
        hs.GetXaxis().SetLabelSize(0)
    else :
        if units!="" :
            hs.GetXaxis().SetTitle(labelX+" ["+units+"]")
	else :
	    hs.GetXaxis().SetTitle(labelX)

    hs.GetYaxis().SetTitle("Events")
    hs.GetYaxis().SetTitleOffset(1)

    if dndm : hs.GetYaxis().SetTitle("dN/d"+labelX)

    c.cd()

    if doRatio :
        data2 = histo['data'].Clone("data")
        mc = histo['Rare']
        mc.Add(histo['Reducible'])
        mc.Add(histo['ZZ4L'])
        xmin = mc.GetXaxis().GetXmin()
        xmax = mc.GetXaxis().GetXmax()
        line = TLine(xmin,1.0,xmax,1.0)
        line.SetLineWidth(1)
        line.SetLineColor(kBlack)

        ratioPad.Draw()
        ratioPad.cd()

        data2.Divide(data2,mc)

        data2.SetMarkerStyle(20)
        data2.SetTitleSize(0.12,"Y")
        data2.SetTitleOffset(0.40,"Y")
        data2.SetTitleSize(0.12,"X")
        data2.SetLabelSize(0.10,"X")
        data2.SetLabelSize(0.08,"Y")
        data2.GetYaxis().SetRangeUser(0.62,1.38)
        data2.GetYaxis().SetNdivisions(305)
        data2.GetYaxis().SetTitle("Obs/Exp   ")

        if units!="" :
	    data2.GetXaxis().SetTitle(labelX+" ["+units+"]")
        else :
	    data2.GetXaxis().SetTitle(labelX)

        data2.Draw("P")
        line.Draw()

    c.cd()
    plotPad.cd()
        
    l = TLegend(xR,0.55,xR+0.28,0.9)
    for group in groups : l.AddEntry(histo[group],group,"F") 
    l.SetBorderSize(0)
    l.SetFillColor(0)
    l.SetFillStyle (0)
    l.Draw()

    factor = 1.05
    if left : factor = 1./2.2
           
    xL = hs.GetXaxis().GetXmin()+(hs.GetXaxis().GetXmax()-hs.GetXaxis().GetXmin())*xR*factor
    yL = hs.GetMaximum()*0.35

    offsetF=yL-0.1*hs.GetMaximum()
    offsetFF=yL-0.2*hs.GetMaximum()

    plotPad.Draw()
    #CMS_lumi(plotPad,4,11)

    c.SaveAs("stack.png")
    c.SaveAs("stack.root")
    raw_input()
    
    
if __name__ == '__main__':

#def makeDiTauStack(outDir,inFile,rootDir,s,labelX, units = "GeV",left=false,channel = "",
#                   json = "Golden",log = false,dndm=false, doRatio = false) :   
   makeDiTauStack('.','./allGroups.root','',3,'m(#tau#tau)') 

   

