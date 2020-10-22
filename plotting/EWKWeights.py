from ROOT import TFile

class EWKWeights() :

    def __init__(self):

        fileEWKin = './Zll_nloEWK_weight_unnormalized.root'
        self.finEWK = TFile.Open(fileEWKin,"READ")
        
    def getEWKWeight(self, pt, var="central") :
        hCentral  = self.finEWK.Get("SignalWeight_nloEWK_rebin")
        hUp  = self.finEWK.Get("SignalWeight_nloEWK_up_rebin")
        hDown  = self.finEWK.Get("SignalWeight_nloEWK_down_rebin")
        xB = 1.
        if var.lower() == "central" : xB = hCentral.GetBinContent(hCentral.FindBin(pt))
        if var.lower() == "up" : xB = hUp.GetBinContent(hUp.FindBin(pt))
        if var.lower() == "down" : xB = hDown.GetBinContent(hDown.FindBin(pt))
        return xB

