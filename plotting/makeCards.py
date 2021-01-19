from ROOT import gSystem, gStyle, gROOT, kTRUE, kFALSE, gDirectory, gPad
from ROOT import TCanvas, TH1D, TH1F,  TH1, TFile
#from ROOT import kBlack, kBlue, kMagenta, kOrange, kAzure, kRed, kGreen, kFALSE
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
    parser.add_argument("-r","--region",default='OS',type=str,help="overide systematics list")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)
tag= str(args.extraTag)





histos = { # [nBins,xMin,xMax,units]
        #"m_sv_new_FM":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMext":[20,0,200,"[Gev]","m(#tau#tau)(SV)"],
        #"m_sv_new_FMjallv2":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "m_sv_new_FMjall":[10,0,200,"[Gev]","m(#tau#tau)(SV)"],
        "lep_FWDH_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_0_75_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_75_150_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_0J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_150_250_GE1J_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"],
        "lep_PTV_GT250_htt125":[21,0,21,"[Gev]","m(#tau#tau)(SV)"]
}


cutflows=['hCutFlowPerGroup', 'hCutFlowPerGroupFM']



scaleSyst = ["Central"]

#scaleSyst=[]

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

otherS=['PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')


signalS=['NLOEWK', 'scale_lowpt', 'scale_highpt', 'lep_scale'] 
SignalSyst=[]
for i, sys in enumerate(signalS) :
    SignalSyst.append(sys+'Up')
    SignalSyst.append(sys+'Down')


sysall =['Central']
sysall = scaleSyst + jesSyst + OtherSyst + SignalSyst
#sysall = scaleSyst + jesSyst + OtherSyst 

#sysall =['Central']
print '--------------->', len(sysall), sysall

#sysall=['Central']
if str(args.overideSyst) != '' : sysall=[str(args.overideSyst)]



groups=['Signal']
#groups = ['bfl1', 'ljfl1', 'cfl1','jfl1','bfl2', 'ljfl2', 'cfl2','jfl2','jft1', 'jft2','fakes','f1', 'f2', 'Signal','Other','Top','DY','WZ','ZZ','data', 'Reducible']
#groupss = ['Signal','Other','Top','DY','WZ','ZZ','data', 'Reducible']

groups = ['Other','ZZ','data', 'Reducible', 'ggZH', 'ZH', 'WH']
#groups = ['Other','ZZ','data', 'Reducible', 'ggZH', 'ZH', 'HWW', 'ggHWW']
groups = ['Other','ZZ','data', 'SSR', 'ggZH', 'ZH', 'HWW', 'ggHWW']
Sgroups = [ 'ggZH', 'ZH', 'HWW', 'ggHWW']
#Sgroups = [ 'ggZH']


h={}

#ascaleXsec={'

#cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'eeem', 5:'mmet', 6:'mmmt', 7:'mmtt', 8:'mmem'}
#cats = { 1:'eeet', 2:'eemt', 3:'eett', 4:'mmet', 5:'mmmt', 6:'mmtt' }

cats = [ 'eeet', 'eemt', 'eett', 'mmet', 'mmmt', 'mmtt' ]

dirs=['llet','llmt','lltt','llem','all']
dirs=['llet','llmt','lltt','llem', 'eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
dirs=['eeet', 'eemt', 'eett', 'eeem', 'mmet', 'mmmt', 'mmtt', 'mmem']
dirs=['eeet', 'eemt', 'eett',  'mmet', 'mmmt', 'mmtt']

dirs=cats

tag='pow_noL'
gSSR=['SSR', 'Reducible']

#allGroups_2016_OS_LT00_16noSV_pow_noL_sysscale_m_etalt1p2Up.root
sign=str(args.region)
for sys in sysall : 

    print 'working on', sys
    #step 1 : merge all the .root files for a given systematic
    haddFile='allGroups_{0:s}_{3:s}_LT00_{1:s}_sys{2:s}.root'.format(era, tag, sys,sign)
    haddFile='allGroups_{0:s}_{3:s}_LT00_16noSVll_{1:s}_sys{2:s}.root'.format(era, tag, sys,sign)

    command='mkdir -p   /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{3:s}/data ; mv  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{3:s}/data*root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/data/. '.format(haddFile,era, tag, sys)
    #os.system(command)
    #if sys =='Central' : 
    #    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/*_sys{3:s}*root'.format(haddFile,era, tag, sys)
    #else : 
    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/*_sys{3:s}*root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/data_{1:s}_sysCentral.root'.format(haddFile,era, tag, sys)
    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{4:s}/*_sys{3:s}*.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{4:s}/data/data_{1:s}_sys{3:s}.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_SS/*_sys{3:s}.root   '.format(haddFile,era, tag, sys,sign)
    command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{4:s}/*_sys{3:s}*.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{4:s}/data/data_{1:s}_sys{3:s}.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_SS/*_sysCentral.root   /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/{1:s}_OSS/*.root'.format(haddFile,era, tag, sys,sign)

    if sys in SignalSyst : 
        command='hadd -f {0:s} /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}_{4:s}/*_sys{3:s}*.root'.format(haddFile,era, tag, sys,sign)

    hfile= os.path.isfile('allGroups_{0:s}_{3:s}_LT00_16noSVll_{1:s}_sys{2:s}.root'.format(era, tag, sys,sign))
    if not hfile :   
        print command
        os.system(command)


    inFileName=haddFile

    #step 2 : merge ll categories  the .root files for a given systematic
    outFileName='cards_{0:s}_sys{2:s}.root'.format(era, tag, sys)
    
    fIn = TFile( inFileName, 'read' )
    fOut = TFile( outFileName, 'recreate' )
    

    fOut.cd()
    for i, idir in enumerate(dirs) :
	fOut.mkdir('{0:s}'.format(str(dirs[i])))

    fIn.cd()


    SSRSumOfW={}
    RedSumOfW={}
    for ig in gSSR : 
	for icat, cat in enumerate(dirs) :
            SSRSumOfW[icat]={}
            RedSumOfW[icat]={}
	    for plotVar in histos :
                if 'FMjall' not in plotVar : continue
		SSRSumOfW[icat][plotVar] = {}
		RedSumOfW[icat][plotVar] = {}

    for ig in gSSR :
	for icat, cat in enumerate(dirs) :
	    for plotVar in histos :
		if 'FMjall' not in plotVar : continue
		hname='h'+ig+"_"+cat+"_"+plotVar
		if sys in SignalSyst : 
		    SSRSumOfW[icat][plotVar] = 0
		    RedSumOfW[icat][plotVar] = 0
		else  :
		    try : 
			h1 = fIn.Get(hname)
			if 'SSR' in ig :
			    SSRSumOfW[icat][plotVar] = h1.GetSumOfWeights()
			    #SSRSumOfW[icat][plotVar] = 100.
			if 'Reducible' in ig :
			    RedSumOfW[icat][plotVar] = h1.GetSumOfWeights()
		    except KeyError : continue

    print 'Reducible SumOfWegights from AR*FF', RedSumOfW
    print 'SS SumOfWegights from data- prompt MC', SSRSumOfW
    for igroup, group in enumerate(groups) : 


	if group =='Reducible' : continue

	h[igroup]={}
        if sys in SignalSyst and group not in Sgroups : continue

	for icat, cat in enumerate(dirs) :
	    h[igroup][icat]={}
	    for plotVar in histos :
		hname='h'+group+"_"+cat+"_"+plotVar
		h[igroup][icat] = fIn.Get(hname)

                 
		#if group in Sgroups : h[igroup][icat].Scale(1.1)

		if group=='data' : 
                    for i in range(1,22) : 
                        xi = h[igroup][icat].GetBinContent(i)
                        if xi <1  : 
                            h[igroup][icat].SetBinContent(i,0)
                            h[igroup][icat].SetBinError(i,0)

                if 'SSR' in group and 'FMjall' in plotVar: 
                    try : 
                        #print 'see ? ', plotVar, hname, h[igroup][icat].GetName(), h[igroup][icat].GetSum()
                        h[igroup][icat].Scale( RedSumOfW[icat][plotVar]/SSRSumOfW[icat][plotVar])
                        #if  cat[2:]=='mt'  or cat[2:]=='et' :  h[igroup][icat].Scale(0.9)
                    except KeyError : continue


                try : h[igroup][icat].GetName()
		except ReferenceError : continue
                #print icat, cat, cats, h[igroup][icat].GetName()



		#if 'Reducible' in group : 
                #    for ij in range(1,22) :
                #        ir = h[igroup][icat].GetBinError(ij)
		#	h[igroup][icat].SetBinError(ij,0.5*ir)

		#print group, sys, cat, hname
		for ij in range(1,22) : 

		    #if h[icat].GetBinContent(i) < 0 : print 'Reducible neg', i, h[icat].GetBinContent(i), plotVar, sys, cat
		    if h[igroup][icat].GetBinContent(ij) < 0 : 
			print 'warning, process', group, 'has a negative bin', ij, h[igroup][icat].GetBinContent(ij), icat, cat, sys, h[igroup][icat].GetName()
			h[igroup][icat].SetBinContent(ij,0.01)
			h[igroup][icat].SetBinError(ij,0.001)


		if sys == 'Central' : plotVar =''
		else : plotVar = '_CMS_'+sys

		if sys in scale or 'tauid' in sys or 'scale_e' in sys or 'scale_m' in sys or 'scale_t' in sys: 
		    plotVar = plotVar.replace('Up','_{0:s}Up'.format(era))
		    plotVar = plotVar.replace('Down','_{0:s}Down'.format(era))

		if 'lep_scale' in sys:
		    plotVar = plotVar.replace('lep_scale', 'ZHlep_scale')
		    plotVar = plotVar.replace('_CMS', '')
		    if 'ZH' in group : 
			plotVar = plotVar.replace('ZH_htt125', 'ZH_lep_htt125')
		    if 'HWW' in group : 
			plotVar = plotVar.replace('ZH_hww125', 'ZH_lep_hww125"')

		if 'lowpt' in sys or 'highpt' in sys:
		    plotVar = plotVar.replace('scale_', 'ZH_scale_')
		    plotVar = plotVar.replace('_CMS', '')

		if 'NLOEWK' in sys : 
		    plotVar = plotVar.replace('NLOEWK', 'qqVH_NLOEWK')
		    plotVar = plotVar.replace('_CMS', '')
				    
		if 'PreFire' in sys : plotVar = plotVar.replace('PreFire', 'prefiring')
		if 'jes'in sys  : #or 'BBEC1' in sys or 'EC2' in sys or 'FlavorQCD' in sys or 'HF' in sys or 'Relative' in sys :
		    plotVar = plotVar.replace('jes', 'scale_j_')
		if 'jer' in sys :
		    plotVar = plotVar.replace('jer', 'res_j_{0:s}'.format(era))


		if group=='data' : ogroup = 'data_obs'
		if group =='ZH' : ogroup='ZH_lep_htt125'
		if group =='ggZH' : ogroup='ggZH_lep_htt125'
		if group =='HWW' : ogroup='ZH_lep_hww125'
		if group =='ggHWW' : ogroup='ggZH_lep_hww125'
		#if group =='WH' : ogroup='ZH_hww125'
		if group =='Other' : ogroup='Triboson'
		if group =='ZZ' : ogroup='ZZ'
		#if group =='Reducible' : ogroup='Reducible'
		if group =='SSR' : ogroup='Reducible'

		if group=='data' : 
                    h[igroup][icat].Sumw2(kFALSE)
                    h[igroup][icat].SetBinErrorOption(TH1.kPoisson)

		#for i, idir in enumerate(dirs) :
		#print 'trying this now', fOut.GetFileName()
		fOut.cd()

		fOut.cd('{0:s}'.format(str(dirs[icat])))
		#print '--->', i, cat, idir, h[i].GetTitle()
		ht = h[igroup][icat].GetTitle()
		hplus=''
		etag='htt125'
		if 'HWW' in group : etag='hww125'
		if 'FWDH' in ht : hplus = '_FWDH_'+etag
		if 'PTV_150_250_GE1J' in ht : hplus = '_PTV_150_250_GE1J_'+etag
		if 'PTV_150_250_0J' in ht : hplus = '_PTV_150_250_0J_'+etag
		if 'PTV_GT250' in ht : hplus = '_PTV_GT250_'+etag
		if 'PTV_0_75' in ht : hplus = '_PTV_0_75_'+etag
		if 'PTV_75_150' in ht : hplus = '_PTV_75_150_'+etag
	     
		#hname=ogroup+plotVar


		#iaf len(hplus) > 0 and 'ZH' in group : hname = hname.replace('_htt125','')
		if len(hplus) ==0 and 'ZH' in group and 'lep_scale' not in sys : ogroup = ogroup.replace('lep_','')
		if len(hplus) ==0 and 'HWW' in group and 'lep_scale' not in sys: ogroup = ogroup.replace('lep_','')
		if len(hplus) >0 and 'ZH' in group : ogroup = ogroup.replace('lep_htt125','lep')
		if len(hplus) >0 and 'HWW' in group : ogroup = ogroup.replace('lep_hww125','lep')
		#f len(hplus) > 0 and 'ggZH' in group : ogroup = ogroup.replace('htt125','hww125')

		h[igroup][icat].SetName(ogroup+hplus+plotVar)
		h[igroup][icat].SetTitle('h1')

		#if h[i].GetSumOfWeights() == 0.0 and h[i].GetNbinsX () <21: print 'this has 0.0 SoW or problem with bins', h[i].GetName(), cat, sys, h[i].GetNbinsX() 

		#h[i].SetTitle(hname)
		#if ( ('PTV' in hplus or 'FWDH' in hplus ) and 'ZH' in group ) or ('PTV' not in hplus and 'FWDH' not in hplus and 'ZH' not in group ): 
		if ( 'PTV' in hplus or 'FWDH' in hplus ) and 'ZH' not in group  and 'WH' not in group and 'HWW' not in group: continue
		else:     

		    '''
		    htemp=h[i]
		    px    = TH1F( 'px', 'px', 18,0,18 )
		    for j in range(1,6) : 
			px.SetBinContent(j,htemp.GetBinContent(j))
			px.SetBinError(j,htemp.GetBinError(j))

		    for j in range(8,13) : 
			px.SetBinContent(j-1,htemp.GetBinContent(j))
			px.SetBinError(j-1,htemp.GetBinError(j))

		    for j in range(15,20) : 
			px.SetBinContent(j-2,htemp.GetBinContent(j))
			px.SetBinError(j-2,htemp.GetBinError(j))

		    px.SetBinContent(6,htemp.GetBinContent(6)+htemp.GetBinContent(7))
		    px.SetBinError(6,sqrt(  htemp.GetBinError(6)*htemp.GetBinError(6)+htemp.GetBinError(7)*htemp.GetBinError(7)))

		    px.SetBinContent(12,htemp.GetBinContent(13)+htemp.GetBinContent(14))
		    px.SetBinError(12,sqrt(  htemp.GetBinError(13)*htemp.GetBinError(13)+htemp.GetBinError(14)*htemp.GetBinError(14)))

		    px.SetBinContent(18,htemp.GetBinContent(20)+htemp.GetBinContent(21))
		    px.SetBinError(18,sqrt(  htemp.GetBinError(20)*htemp.GetBinError(20)+htemp.GetBinError(21)*htemp.GetBinError(21)))
		    
		    px.SetName(htemp.GetName())
		    px.SetTitle(htemp.GetTitle())


		    px.Write()
		    htemp.Write()
		    '''
		    #print h[igroup][icat].GetName(), h[igroup][icat].GetSum(), hname, igroup, group, icat, cat
		    h[igroup][icat].Write()

