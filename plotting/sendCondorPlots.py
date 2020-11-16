import ROOT
from ROOT import TFile, TTree
import os
import os.path
import sys
import fileinput
import subprocess
import colors as BC



def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-f","--inFileName",default='file.csv',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-e","--extraTag",default='pow_noL',type=str,help="pow_noL or pow_wL")
    parser.add_argument("-o","--overideSyst",default='',type=str,help="overide systematics list")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)
tag= str(args.extraTag)

eospath='/eos/uscms/store/user/alkaloge/{0:s}/nAODv7/'.format(sel)

args.inFileName='MCsamples_{0:s}_paper.csv'.format(era)

command = "mkdir -p /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/{0:s}/data_{0:s}".format(era)
os.system(command)

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

otherS=['PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered'] 

signalS=['NLOEWK', 'scale_lowpt', 'scale_highpt', 'lep_scale'] 

OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')

SignalSyst=[]
for i, sys in enumerate(signalS) :
    SignalSyst.append(sys+'Up')
    SignalSyst.append(sys+'Down')

sysall = scaleSyst + jesSyst + OtherSyst + SignalSyst
sysall = SignalSyst

signalGroup=['ZH', 'ggZH', 'HWW', 'ggHWW']

#sysall=['Central']
if str(args.overideSyst) != '' : sysall=[str(args.overideSyst)]



for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    ds = vals[0]
    nickName=vals[1]
    #if 'Run' in ds or 'data' in ds : sysall = ["Central"]
    if '#' in ds : continue
    #if 'data' in ds : continue


    #if 'scale_lowpt' in sys or 'scale_highpt' in sys :
    #    if 'ZH' not in nickName and 'WH' not in nickName : continue
    parts=1
    if 'ggZH_HToTauTau_ZToLL' not in ds :  continue

    if 'ggZH_HToTauTau_ZToLL' in ds : 
	fin='../MC/condor/ZH/ggZH_HToTauTau_ZToLL_{0:s}/ggZH_HToTauTau_ZToLL_{0:s}.root'.format(era)
	ff = TFile(fin,'read')
	ttree = ff.Get("Events")
	ev = ttree.GetEntries()
	parts = ev/10000 +1
	print 'for ds', ds,' will make ', parts, ev

    for ic, sys in enumerate(sysall) :

        if sys in SignalSyst and nickName not in signalGroup : continue

            
            #aparts=11
        
	datacf = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/data/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)) #ZHToTauTau_2016_sysscale_t_3prong1pizeroUp.root
        for part in range(1,parts+1) : 

	    filejdl = 'condor_{0:s}_{1:s}_{2:s}_{3:s}_sys{4:s}_{5:s}of{6:s}.jdl'.format(ds,era,sel,tag, sys,str(part),str(parts))
	    filesh = 'condor_{0:s}_{1:s}_{2:s}_{3:s}_sys{4:s}_{5:s}of{6:s}.sh'.format(ds,era,sel,tag, sys,str(part),str(parts))

	    cf = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/{3:s}_{2:s}_sys{5:s}_{6:s}of{7:s}.root'.format(eospath,sel,era,ds,tag,sys,str(part),str(parts))) 
	    cff = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/NormZZ/{3:s}_{2:s}_sys{5:s}_{6:s}of{7:s}.root'.format(eospath,sel,era,ds,tag,sys,str(part),str(parts))) 

            if 'ggZH_HToTauTau_ZToLL' not in ds : 
		filejdl = 'condor_{0:s}_{1:s}_{2:s}_{3:s}_sys{4:s}.jdl'.format(ds,era,sel,tag, sys,str(part),str(parts))
		filesh = 'condor_{0:s}_{1:s}_{2:s}_{3:s}_sys{4:s}.sh'.format(ds,era,sel,tag, sys,str(part),str(parts))
		cf = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys,str(part),str(parts))) 
		cff = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/NormZZ/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys,str(part),str(parts))) 

	    cfs = os.path.isfile("./Jobs/{0:s}.submitted".format(filejdl))

	    if cf or cff or datacf:   
		print BC.bcolors.OKBLUE+'looks like you have it this in eos', ds, era, sel, tag, sys, str(part), str(parts), '/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/{3:s}_{2:s}_sys{5:s}_{6:s}of{7:s}.root'.format(eospath,sel,era,ds,tag,sys, str(part),str(parts))
		continue
	    if (not cf and not cff and not datacf) and cfs : 
		print 'probably this is still running {0:s}.submitted? '.format(filejdl)
		continue

	    if not cf and not cff and not cfs and not datacf:

		command = "cp Templates/template.sh {0:s}".format(filesh)
		os.system(command)
		if 'data' not in ds and 'Run' not in ds : 
		    command = "cp Templates/template.jdl {0:s}".format(filejdl)
		else :
		    command = "cp Templates/template_data.jdl {0:s}".format(filejdl)
		os.system(command)
		
	       
		subprocess.call(["sed -i  's/SYSTEMATICHERE/{1:s}/g' {0:s}".format(filesh,sys)], shell=True)
		subprocess.call(["sed -i  's/SYSTEMATICHERE/{1:s}/g' {0:s}".format(filejdl,sys)], shell=True)

		subprocess.call(["sed -i  's/FILEIN/{1:s}/g' {0:s}".format(filesh,ds)], shell=True)
		subprocess.call(["sed -i  's/FILEIN/{1:s}/g' {0:s}".format(filejdl,ds)], shell=True)

		subprocess.call(["sed -i  's/YEAR/{1:s}/g' {0:s}".format(filesh,era)], shell=True)
		subprocess.call(["sed -i  's/YEAR/{1:s}/g' {0:s}".format(filejdl,era)], shell=True)

		subprocess.call(["sed -i  's/CHANNEL/{1:s}/g' {0:s}".format(filesh,sel)], shell=True)
		subprocess.call(["sed -i  's/CHANNEL/{1:s}/g' {0:s}".format(filejdl,sel)], shell=True)

		subprocess.call(["sed -i  's/NICKNAME/{1:s}/g' {0:s}".format(filesh,nickName)], shell=True)
		subprocess.call(["sed -i  's/NICKNAME/{1:s}/g' {0:s}".format(filejdl,nickName)], shell=True)


		subprocess.call(["sed -i  's/TAG/{1:s}/g' {0:s}".format(filesh,tag)], shell=True)
		subprocess.call(["sed -i  's/TAG/{1:s}/g' {0:s}".format(filejdl,tag)], shell=True)

                if 'ggZH_HToTauTau_ZToLL' in ds : 
		    subprocess.call(["sed -i  's/RANGEHERE/{1:s}/g' {0:s}".format(filesh,str(part))], shell=True)
                else :  
		    subprocess.call(["sed -i  's/RANGEHERE/0/g' {0:s}".format(filesh)], shell=True)

		subprocess.call(["sed -i  's/PARTHERE/{1:s}/g' {0:s}".format(filejdl,str(part))], shell=True)
		subprocess.call(["sed -i  's/PARTSHERE/{1:s}/g' {0:s}".format(filejdl,str(parts))], shell=True)

		#outLines = []
		#outLines.append("{0:s}\n".format(ds)
		open(ds+'_'+era+'_'+sel+'_'+tag+'.txt','w').writelines(line)


		command = "chmod 777 {0:s}".format(filejdl)
		os.system(command)
		command = "chmod 777 {0:s}".format(filesh)
		os.system(command)


		command = "cp  {0:s}_{1:s}_{2:s}_{3:s}.txt Jobs/.".format(ds,era,sel,tag)
		os.system(command)
		command = "mv  {0:s} Jobs/.".format(filejdl)
		os.system(command)
		command = "mv  {0:s} Jobs/.".format(filesh)
		os.system(command)

		fileout='{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)

		#/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/2016/

		print 'this is missing..... eos', ds, era, sel, tag, sys
		command = "cd Jobs;condor_submit {0:s} ;cd ..".format(filejdl)
		os.system(command)
		com="touch ./Jobs/{0:}.submitted".format(filejdl)
		os.system(com)
		print command

print BC.bcolors.DEFAULT+'done'	
command='echo -e "\e[39m"'
os.system(command)


