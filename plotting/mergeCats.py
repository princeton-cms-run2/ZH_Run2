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
        #"m_sv_new":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"Z_Pt":[10,0,200,"[Gev]","P_T(l_{1}l_{2})"],
        #"m_sv_new_FM":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMext":[20,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMjallv2":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "m_sv_new_FMjall":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "lep_FWDH_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_0_75_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_75_150_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_0J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_GE1J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_GT250_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
}


cutflows=['hCutFlowPerGroup', 'hCutFlowPerGroupFM']



scaleSyst = ["Central"]

scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']


for i, sys in enumerate(scale) :
    scaleSyst.append(sys+'Up')
    scaleSyst.append(sys+'Down')

jes=['jesAbsolute', 'jesAbsolute_{0:s}'.format(str(era)), 'jesBBEC1', 'jesBBEC1_{0:s}'.format(str(era)), 'jesEC2', 'jesEC2_{0:s}'.format(str(era)), 'jesFlavorQCD', 'jesHF', 'jesHF_{0:s}'.format(str(era)), 'jesRelativeBal', 'jesRelativeSample_{0:s}'.format(str(era)), 'jesHEMIssue', 'jesTotal', 'jer']

jesSyst=[]
for i, sys in enumerate(jes) :
    jesSyst.append(sys+'Up')
    jesSyst.append(sys+'Down')

otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')

sysall = scaleSyst + jesSyst + OtherSyst

print '--------------->', len(sysall)

#sysall=['Central']
if str(args.overideSyst) != '' : sysall=[str(args.overideSyst)]



groups=['Signal']
groups = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1', 'f2', 'Signal','Other','Top','DY','WZ','ZZ','data', 'Reducible']
#groupss = ['Signal','Other','Top','DY','WZ','ZZ','data', 'Reducible']



groupss = ['Other','ZZ','data', 'Reducible', 'ggZH', 'ZH', 'WH']

groups=groupss

h={}

cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}

dirs=['llet','llmt','lltt','llem','all']
dirs=['llet','llmt','lltt','llem', 'eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
dirs=['eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']

tag='pow_noL'

#allGroups_2016_OS_LT00_16noSV_pow_noL_sysscale_m_etalt1p2Up.root


for sys in sysall : 

    print 'working on', sys
    #step 1 : merge all the .root files for a given systematic
    haddFile='allGroups_{0:s}_OS_LT00_{1:s}_sys{2:s}.root'.format(era, tag, sys)
    haddFile='allGroups_{0:s}_OS_LT00_16noSV_{1:s}_sys{2:s}.root'.format(era, tag, sys)

    command='mkdir -p   /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/data ; mv  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/data*root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}data/. '.format(haddFile,era, tag, sys)
    #os.system(command)
    #if sys =='Central' : 
    #    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/*_sys{3:s}*root'.format(haddFile,era, tag, sys)
    #else : 
    #    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/*_sys{3:s}*root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/data_{1:s}_sysCentral.root'.format(haddFile,era, tag, sys)
    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/*_sys{3:s}*root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/data/data_{1:s}_sys{3:s}.root'.format(haddFile,era, tag, sys)

    hfile= os.path.isfile('allGroups_{0:s}_OS_LT00_16noSV_{1:s}_sys{2:s}.root'.format(era, tag, sys))
    if not hfile :     os.system(command)

    inFileName=haddFile

    #step 2 : merge ll categories  the .root files for a given systematic
    outFileName='cards_{0:s}_sys{2:s}.root'.format(era, tag, sys)
    
    fIn = TFile( inFileName, 'read' )
    fOut = TFile( outFileName, 'recreate' )
    

    fOut.cd()
    for i, idir in enumerate(dirs) :
	fOut.mkdir('{0:s}'.format(str(dirs[i])))

    fIn.cd()

    for group in groups : 



	gg=group
	#group='h'+group
	
	for plotVar in histos :
	    for icat, cat in cats.items()[0:8] :
		h[icat-1]={}
		hname='h'+group+"_"+cat+"_"+plotVar
		h[icat-1] = fIn.Get(hname)

	    try : 
                '''	
		h[0].Add(h[4])
		h[1].Add(h[5])
		h[2].Add(h[6])
		h[3].Add(h[7])
                '''

                #acommand='python makeStack.py -f {0:s} -L no -u yes -w 16 -b 16 -j {3:s} -e pow_noLv2pow'.format(haddFile,era,tag,sys)
                #os.system(command)

		if sys == 'Central' : plotVar =''
                else : plotVar = '_CMS_'+sys

                if sys in scale or 'tauid' in sys or 'scale_e' in sys or 'scale_m' in sys: 
                    plotVar = plotVar.replace('Up','_{0:s}Up'.format(era))
                    plotVar = plotVar.replace('Down','_{0:s}Down'.format(era))

                if 'PreFire' in sys : plotVar = plotVar.replace('PreFire', 'prefiring')
                if 'jes' in sys : plotVar = plotVar.replace('jes', 'Jet')
                if 'jer' in sys : plotVar = plotVar.replace('jer', 'JER_{0:s}'.format(era))

                if group=='data' : ogroup = 'data_obs'
                if group =='ZH' : ogroup='ZH_lep_htt125'
                if group =='ggZH' : ogroup='ggZH_lep_htt125'
                if group =='WH' : ogroup='ZH_hww125'
                if group =='Other' : ogroup='Triboson'
                if group =='ZZ' : ogroup='ZZ'
                if group =='Reducible' : ogroup='Reducible'

                for i, idir in enumerate(dirs) :
                    #print 'trying this now', fOut.GetFileName()
                    fOut.cd()

		    fOut.cd('{0:s}'.format(str(dirs[i])))
                    
                    ht = h[i].GetTitle()
                    hplus=''
                    if 'FWDH' in ht : hplus = '_FWDH_htt125'
                    if 'PTV_150_250_GE1J' in ht : hplus = '_PTV_150_250_GE1J_htt125'
                    if 'PTV_150_250_0J' in ht : hplus = '_PTV_150_250_0J_htt125'
                    if 'PTV_GT250' in ht : hplus = '_PTV_GT250_htt125'
                    if 'PTV_0_75' in ht : hplus = '_PTV_0_75_htt125'
                    if 'PTV_75_150' in ht : hplus = '_PTV_75_150_htt125'
                 
		    #hname=ogroup+plotVar

                    # ggZH_lep_PTV_0_75_htt125_CMS_JER_2016Down Cecile 
                    # ggZH_lep_CMS_JER_2016Up_PTV_0_75_htt125   mine
                    # ggZH_lep_htt125_PTV_0_75_htt125_CMS_JER_2016Up
                    # ggZH_lep_PTV_0_75_htt125_CMS_JER_2016Up

                    #iaf len(hplus) > 0 and 'ZH' in group : hname = hname.replace('_htt125','')
                    if len(hplus) > 0 and 'ZH' in group : ogroup = ogroup.replace('lep_htt125','lep')
		    h[i].SetName(ogroup+hplus+plotVar)
		    h[i].SetTitle('h1')

                    if h[i].GetSumOfWeights() == 0.0 and h[i].GetNbinsX () <21: print 'this has 0.0 SoW or problem with bins', h[i].GetName(), cat, sys, h[i].GetNbinsX() 

		    #h[i].SetTitle(hname)
                    #if ( ('PTV' in hplus or 'FWDH' in hplus ) and 'ZH' in group ) or ('PTV' not in hplus and 'FWDH' not in hplus and 'ZH' not in group ): 
                    if ( 'PTV' in hplus or 'FWDH' in hplus )and 'ZH' not in group  and 'WH' not in group: continue
		    else:     h[i].Write()
                    #print 'name should be', hname, i
                    #fOut.ls()

                '''
                fOut.cd('llmt')
		hname=ogroup+plotVar
		h[1].SetName(hname)

		hname=group+"_lltt_"+plotVar
		hname=ogroup+plotVar
		h[2].SetName(hname)

                fOut.cd('llem')
		hname=ogroup+plotVar
		h[3].SetName(hname)
                '''

		#hsum=h[0].Clone()
	       
		
		#for i in range(1,4) : 
		#    hsum.Add(h[i])

                '''
		for i in range(0,4) : 
		    fOut.cd()
		    h[i].Write()

                '''
                #fOut.cd()
                #fOut.cd('all')
		#hsum.SetName(ogroup+plotVar)
		#hsum.Write()

		#fOut.Write()
	    except AttributeError : 
		#print 'problem with', group, icat, cat, plotVar
		continue


