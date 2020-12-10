import os
import os.path
import sys
#import fileinput
#import colors as BC
import subprocess



def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-o","--overideSyst",default='',type=str,help="overide systematics list")
    parser.add_argument("-m","--merge",default='1',type=str,help="merge")
    parser.add_argument("-r","--region",default='OS',type=str,help="OS SS")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)



signalGroup=['ZH', 'ggZH', 'HWW', 'ggHWW']

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

otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40','scale_met_unclustered', 'scale_lowpt', 'scale_highpt'] 
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


tag='pow_noL'
'''
for line in open('MCsamples_{0:s}_paper.csv'.format(era),'r').readlines() :
    vals = line.split(',')
    ds = vals[0]
    if '#' in ds : continue 
    if 'data' in ds : continue 
    if ds not in signalGroup : continue
    group=ds
    command='hadd -f /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_syslep_scaleUp.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_sysscale_lowptUp.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_sysscale_highptUp.root '.format(group,era,tag)
    hf = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_syslep_scaleUp.root'.format(group,era,tag))
    hff = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/NormZZ/{0:s}_{1:s}_syslep_scaleUp.root'.format(group,era,tag))
    if not hf and not hff: os.system(command)
    #if not hf : print command #os.system(command)

    command='hadd -f  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_syslep_scaleDown.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_sysscale_lowptDown.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_sysscale_highptDown.root '.format(group,era,tag)
    hf = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/{0:s}_{1:s}_syslep_scaleDown.root'.format(group,era,tag))
    hff = os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{2:s}/{1:s}/NormZZ/{0:s}_{1:s}_syslep_scaleDown.root'.format(group,era,tag))
    #if not hf : print command #os.system(command)
    if not hf and not hff: os.system(command)
'''

#sysall = scaleSyst + OtherSyst
#sysall = OtherSyst
sysall = scaleSyst + jesSyst + OtherSyst + SignalSyst

#sysall=['Central']
if str(args.overideSyst) != '' : sysall=[str(args.overideSyst)]



for sys in sysall : 

    #command='. makeFinalPlots.sh {0:s} 16 {1:s} {2:s}'.format(era,sys, args.merge)
    subprocess.call(['./makeFinalPlots.sh {0:s} 16 {1:s} {2:s} {3:s}'.format(era,sys, args.merge, args.region)], shell=True)
    #os.system(command)
    #print command


